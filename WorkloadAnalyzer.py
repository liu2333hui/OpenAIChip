import os
import six
import pickle
import numpy as np
import paddle
from paddle.fluid import core

from paddle.fluid import unique_name
from paddle import compat as cpt

#################################################################
def _is_persistable(var_desc):
    if (
        var_desc.type() == core.VarDesc.VarType.FEED_MINIBATCH
        or var_desc.type() == core.VarDesc.VarType.FETCH_LIST
        or var_desc.type() == core.VarDesc.VarType.READER
        or var_desc.type() == core.VarDesc.VarType.RAW
    ):
        return False
    return var_desc.persistable()


def _is_parameter(persistable_var_desc, program_desc):
    # 1. firstly, param should be input of op
    input_ops = []  # op can be repeated
    for block_idx in six.moves.range(program_desc.num_blocks()):
        block = program_desc.block(block_idx)
        for op_idx in six.moves.range(block.op_size()):
            op = block.op(op_idx)
            # NOTE: parameter is the input of a certain op
            if persistable_var_desc.name() in op.input_arg_names():
                input_ops.append(op)
    # 2. secondly, param should not be output of op or be same op's output
    for block_idx in six.moves.range(program_desc.num_blocks()):
        block = program_desc.block(block_idx)
        for op_idx in six.moves.range(block.op_size()):
            op = block.op(op_idx)
            if persistable_var_desc.name() in op.output_arg_names():
                # such as batch_norm_op
                if op in input_ops:
                    continue
                else:
                    return False
    return True
def _get_persistable_vars(program_desc):
    persistable_vars = []
    for i in six.moves.range(program_desc.num_blocks()):
        block = program_desc.block(i)
        persistable_vars.extend(list(filter(_is_persistable, block.all_vars())))
    return persistable_vars

def _get_persistable_var_names(program_desc):
    """
    Get all persistable variable names in ProgramDesc.
    """
    var_names = []
    persistable_vars = _get_persistable_vars(program_desc)
    for var in persistable_vars:
        var_names.append(var.name())
    return var_names

def _generate_unique_var_name_sync_with_main_program(prefix):
    return unique_name.generate(prefix)

def _rename_var_program_desc(program_desc, include=None, exclude=None):
    """
    Change the name of the loaded variables.Use 'unique_name.generate' to avoid duplication.
    It is used when loading multiple program during inference.

    e.g. linear_0.tmp_3 ==> linear_0.tmp_1, x ==> x_0. For double grad, x@GRAD ==> x_0@GRAD
    If 'include' is not `None`,variables in include and the corresponding
      double grad variables (if exist) are renamed.
    If 'exclude' is not `None`,variables that are in exclude and the
      corresponding double grad variables (if exist) are not renamed.

    Args:
        program_desc(ProgramDesc):the variables in it will be modified.
        include(List):list of names of variables.
        exclude(List):list of names of variables.

    Returns:
        tuple of (dict_rename_var_new_old, dict_rename_var_old_new)
        dict_rename_var_new_old is a dict mapping from new name to old name
        dict_rename_var_old_new is a dict mapping from old name to new name
    """
    dict_rename_var_old_new = dict()
    dict_rename_var_new_old = dict()
    old_names = []
    # Store all old names
    for b_idx in six.moves.range(program_desc.num_blocks()):
        cur_block = program_desc.block(b_idx)
        for var in cur_block.all_vars():
            old_names.append(var.name())

    # Create dict_rename_var_new_old and dict_rename_var_old_new for non double
    # grad variables
    has_double_grad = False
    for b_idx in six.moves.range(program_desc.num_blocks()):
        cur_block = program_desc.block(b_idx)
        for var_idx, var in enumerate(cur_block.all_vars()):
            name_old = var.name()
            is_double_grad_var = "@GRAD" in name_old
            has_double_grad = has_double_grad or is_double_grad_var
            should_rename = (
                (include is None or name_old in include)
                and (exclude is None or name_old not in exclude)
                and not is_double_grad_var
            )
            if should_rename:
                temp_name = name_old.split('_')
                if len(temp_name) > 1 and temp_name[-1].isnumeric():
                    temp_name = "_".join(temp_name[:-1])
                else:
                    temp_name = name_old
                while True:
                    name_new = _generate_unique_var_name_sync_with_main_program(
                        temp_name
                    )
                    if (
                        name_new
                        not in old_names[:var_idx] + old_names[var_idx + 1 :]
                    ):
                        break
            else:
                name_new = name_old
            if name_old != name_new:
                cur_block._rename_var(
                    cpt.to_bytes(name_old), cpt.to_bytes(name_new)
                )
            if not is_double_grad_var:
                dict_rename_var_old_new[name_old] = name_new
                dict_rename_var_new_old[name_new] = name_old

    # Handle double grad names
    if has_double_grad:
        double_grad_rename_dict = {}
        for name_old in dict_rename_var_old_new:
            for b_idx in six.moves.range(program_desc.num_blocks()):
                cur_block = program_desc.block(b_idx)
                for var_idx, var in enumerate(cur_block.all_vars()):
                    var_name = var.name()
                    if "@GRAD" in var_name and name_old in var_name:
                        new_var_name = var_name.replace(
                            name_old, dict_rename_var_old_new[name_old]
                        )
                        double_grad_rename_dict[var_name] = new_var_name
        for var_name in double_grad_rename_dict:
            dict_rename_var_old_new[var_name] = double_grad_rename_dict[
                var_name
            ]
            dict_rename_var_new_old[
                double_grad_rename_dict[var_name]
            ] = var_name

    # Rename on program desc
    for b_idx in six.moves.range(program_desc.num_blocks()):
        cur_block = program_desc.block(b_idx)
        for op_idx in six.moves.range(cur_block.op_size()):
            op = cur_block.op(op_idx)
            for input_arg_name in op.input_arg_names():
                if input_arg_name in dict_rename_var_old_new:
                    if (
                        input_arg_name
                        != dict_rename_var_old_new[input_arg_name]
                    ):
                        op._rename_input(
                            input_arg_name,
                            dict_rename_var_old_new[input_arg_name],
                        )
                        if cur_block.has_var(cpt.to_bytes(input_arg_name)):
                            cur_block._rename_var(
                                cpt.to_bytes(input_arg_name),
                                cpt.to_bytes(
                                    dict_rename_var_old_new[input_arg_name]
                                ),
                            )
            for output_arg_name in op.output_arg_names():
                if output_arg_name in dict_rename_var_old_new:
                    if (
                        output_arg_name
                        != dict_rename_var_old_new[output_arg_name]
                    ):
                        op._rename_output(
                            output_arg_name,
                            dict_rename_var_old_new[output_arg_name],
                        )
                        if cur_block.has_var(cpt.to_bytes(output_arg_name)):
                            cur_block._rename_var(
                                cpt.to_bytes(output_arg_name),
                                cpt.to_bytes(
                                    dict_rename_var_old_new[output_arg_name]
                                ),
                            )
    program_desc.flush()
    return dict_rename_var_new_old, dict_rename_var_old_new


############################FROM IO.PY of version 2.4.1 paddlepaddle###########
model_file_path = "./benchmarks/paddle/efficientnetb0_QAT/inference.pdmodel"
params_file_path = "./benchmarks/paddle/efficientnetb0_QAT/inference.pdiparams"

#def parse(model_file_path, params_file_path):
with open(model_file_path, "rb") as f:
    program_desc_str = f.read()

program_desc = core.ProgramDesc(program_desc_str)
list_persistable_var = _get_persistable_var_names(program_desc)
rename_new_old_dict, _ = _rename_var_program_desc(
                program_desc, list_persistable_var
            )
# 1. Prune original program
# remove feed, fetch and scale-1 op, remove op_callstack attr
ops_to_remove = []
root_block = program_desc.block(0)
for i in six.moves.range(root_block.op_size()):
    op = root_block.op(i)
    print(i, op.type())
    if op.type() == 'feed':
        print(op.type())
        break

#2. found the feed
compute_head = op
compute_summary(compute_head)

#3. sparsity analysis
#analyze_sparsity()

#4. toggling analysis (tiling-based toggle-level, accumulator-level, others?)
#   three types:
#     1. dense DLA (and variants)
#     2. sparse DLA
#       2.1. Clock-Gated
#       2.2. Encoded/Index-Based


#parse(model_file_path, params_file_path)
