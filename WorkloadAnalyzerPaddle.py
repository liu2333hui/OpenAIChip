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

def key_in_list(key, l, pos=-1):
    for ll in l:
        if(pos != -1):
            #print(key,ll[pos : pos+len(key)])
            if(key == ll[pos : pos+len(key)]):
                return True
        else:
            if(key in ll):
                return True

    return False

def compute_summary(compute_head, ops_dict, DEBUG=1):
    levels = []
    levels.append(compute_head)
    passes = 0
    finished_ids = set()
    level_ids = set()
    level_ids.add(compute_head.id())
    done = False



    #Computing levels
    compute_order = []

    
    #assume a time-out of 3000 leveling passes
    while(passes <= 1000):
        new_levels = set()
        get_all_outputs = []
        for l in levels:
            if(DEBUG):
                print(l.type(), l.inputs(), l.outputs())
            
        
            if 'Out' in l.outputs():
                lout = l.outputs()['Out']
            elif 'Output' in l.outputs():
                lout = l.outputs()['Output']
            else:
                lout = l.outputs()['Y']
            get_all_outputs += lout

        mask = set()
        stuck_levels = set()
        new_level_ids = set()
        
        
        #print(l.outputs())
        #if('relu_0.tmp_0.quantized.dequantized' in get_all_outputs):
        #    return
        #    print("###########################")
        #    print(len(levels), [[ll.type(), ll.inputs(), ll.outputs() ] for ll in levels])
        #    print(get_all_outputs)
        #    print("###########################")
        #print("get_all_outputs", get_all_outputs)
        for out in get_all_outputs:
            #print(out)
            if("fetch" == out):
                done = True
                break
            if(out not in ops_dict):
                print(get_all_outputs)
                print("WARNING: ","PASSES",passes, out, " not in ops_dict, does not output or drive to anything")
                return
            for oo in ops_dict[out]:
                #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                #print( [oo.type(), oo.inputs(), oo.outputs() ] )
                #print(get_all_outputs)
                #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                if "In" in oo.inputs():
                    lin = oo.inputs()["In"]
                elif "Input" in oo.inputs():
                    lin = oo.inputs()["Input"]
                else:
                    lin = oo.inputs()['X']

                
                if "Y"  in oo.inputs() and ("elementwise" in oo.type() or "matmul" in oo.type()) \
                   and not key_in_list("w_0", oo.inputs()["Y"])\
                   and not key_in_list("fc", oo.inputs()["Y"]) and not key_in_list("b_0", oo.inputs()["Y"])\
                    and not key_in_list("_", oo.inputs()["Y"], 0):
                    lin += oo.inputs()["Y"]
                    #print(get_all_outputs)
                    #return
                    #print(lin, oo.type(), oo.inputs(), oo.outputs())
                    #print("########################################")
                #vision transformer patch
                if "expand_shapes_tensor" in oo.inputs():
                    lin = []
                    for ins in oo.inputs()['expand_shapes_tensor']:
                        if("fill_constant" not in ins):
                            lin.append(ins)
                        
                is_subset = True
                for ii in lin:
                    if (ii not in get_all_outputs):
                        is_subset = False

                if(is_subset):
                    if(oo.id() not in finished_ids and oo.id() not in level_ids):
                        #print(finished_ids, oo.id())
                        new_levels.add(oo)
                        new_level_ids.add(oo.id())
                else:
                    if(oo.id() not in finished_ids and oo.id() not in level_ids):
                        #print(lin, get_all_outputs, oo.inputs()["Y"])
                        stuck_levels.add(oo)

                
        
        
        if(done):
            break

        if(DEBUG):
            print("****************************")
            print(len(stuck_levels), [[ll.type(), ll.inputs() ] for ll in stuck_levels])
            print("****************************")

        for oo in stuck_levels:
            
            #return
            if "In" in oo.inputs():
                lin = oo.inputs()["In"]
            elif "Input" in oo.inputs():
                lin = oo.inputs()["Input"]
            else:
                lin = oo.inputs()['X']

            if "Y"  in oo.inputs() and ("elementwise" in oo.type() or "matmul" in oo.type()) \
               and not key_in_list("fc", oo.inputs()["Y"]) and not key_in_list("b_0", oo.inputs()["Y"])\
               and not key_in_list("w_0", oo.inputs()["Y"])\
                and not key_in_list("_", oo.inputs()["Y"], 0):
                lin += oo.inputs()["Y"]

            #vision transformer patch
            if "expand_shapes_tensor" in oo.inputs():
                lin = []
                for ins in oo.inputs()['expand_shapes_tensor']:
                    if("fill_constant" not in ins):
                        lin.append(ins)
                
            #we assume outputs are only singular
            for l_idx, l in enumerate(levels):
                #print(l.type(), l.inputs(), l.outputs())
                if 'Out' in l.outputs():
                    lout = l.outputs()['Out']
                elif 'Output' in l.outputs():
                    lout = l.outputs()['Output']
                else:
                    lout = l.outputs()['Y']
                #print(lout)

                #if already inside, dont need to add
                #print(new_level_ids, l.id())
                #if(l.id() in new_level_ids):
                #    continue
                if (lout[0] in lin and len(lin) >= 2 ):
                    #print("_",[l_idx, l.outputs()])
                    mask.add(l_idx)

        
        #print([[ll.type(), ll.inputs(), ll.outputs() ] for ll in levels] , mask)
        #if(len(stuck_levels) >= 1):
        #    return
        
        #print([[ll.type(), ll.inputs(), ll.outputs() ] for ll in new_levels])
        compute_order.append([])
        for l_idx, l in enumerate(levels):
            if(l_idx not in mask):

                #####(TODOS)#####
                ### HERE WE PROCESS AN OPERATION THAT IS READY
                ### Operation is l 
                #################
                compute_order[-1].append(l.id())
                finished_ids.add(l.id())
            else:
                
                new_levels.add(l)
                
            #return
            
            #for out in lout:
                #print(out)
                #new_levels += ops_dict[out]
                #print(ops_dict[out])
            #new_levels.append()
        if(DEBUG):
            print("PASSES ", passes)
        #print(mask)
        #print(finished_ids)
        #print(len(levels), [[ll.id() ] for ll in levels])
        #print(len(new_levels), [[ll.id() ] for ll in new_levels])
            print(len(levels), [[ ll.type(), ll.outputs() ] for ll in levels])
            print(len(new_levels), [[ll.type(), ll.outputs() ] for ll in new_levels])
        #print(compute_order)
        #COCNAT CAN BE MANY LAYERS !
        #if(len(new_levels) >= 3):
        #    if(oo.type() == "concat"):
        #        pass
        #    else:
        #        print("FATAL ERROR, we are processing operations with more than 3 inputs ?")
        #        print(len(new_levels), [[ll.type(), ll.inputs(), ll.outputs() ] for ll in levels])
        #        print(len(new_levels), [[ll.type(), ll.inputs(), ll.outputs() ] for ll in new_levels])
        #        return
        #for ll in new_levels:
            #if("add" in ll.type()):
                #print("########################################")
                
                #print(ll.type(), ll.inputs(), ll.outputs())
            #return
                #print(len(new_levels), [[ll.type(), ll.inputs(), ll.outputs() ] for ll in new_levels])
        levels = list(new_levels)
        level_ids = new_level_ids
        passes += 1


    #print(statistics)
    statistics = {

        "ops" : len(finished_ids),
        "levels": passes, 
        "compute_order": compute_order
    }

    print(statistics)
    return statistics


def analyze_tensor(weight, bitlength, stats):


    nonzero = np.count_nonzero(weight)
    total = weight.size
    
    stats['zeros'] = total - nonzero
    stats['total'] = total
                
    stats['precision'] = bitlength
    stats['TotalBits'] = total*bitlength
    stats['OneBits'] = sum([ bin(n).count('1') for n in weight.reshape((-1)) ]) #stats['TotalBits'] - 
    stats['ZeroBitsRatio'] = 1 - ( stats['OneBits'] / stats['TotalBits'])
    stats['sparsity'] = (stats['zeros'] / total)
 


#statistics is from the previous summary function, ops_by_id addressed by the ops.id()
#analyze only weights
# ops by id is from the first analysis, state dict contains the actual weights and activations
def analyze_sparsity(statistics, ops_by_id, state_dict):
    sparsity = []
    lvl = 0
    order = 0
    for level in statistics['compute_order']:
        for op_id in level:
            op = ops_by_id[op_id]
            stats = {}
            #print(op.type(), op.inputs(), op.outputs(), op.attr_names())
            stats['name'] = "_".join(op.outputs()[op.output_names()[0]])
            stats['order'] = order
            if(op.type() == "feed"):
                continue
                #stats['weight_sparsity'] = 'n/a'
            elif(op.type() == "quantize_linear"):
                #output = input / scale
                continue
            elif(op.type() == "dequantize_linear"):
                continue
            elif(op.type() == "batch_norm"):
                mean_n = op.inputs()['Mean'][0][0:-2]
                mean = state_dict[mean_n]

                offset_n = op.inputs()['Bias'][0][0:-2]
                offset =state_dict[offset_n]

                scale_n =op.inputs()['Scale'][0][0:-2]
                scale =state_dict[scale_n]

                variance_n =op.inputs()['Variance'][0][0:-2]
                variance = state_dict[variance_n]

                
                #(TODOS)
                #bitlength = ops_dict[op.inputs()['X'][0].split(".dequantized")[0]][0].attr("bit_length")
                #print("*SCALE*=",state_dict[op.inputs()['X'][0]+"@scale"])                    
                #activation_map = np.cast['int8'](activation_map / state_dict[op.inputs()['X'][0]+"@scale"] * scale * 128) #* 20

            elif(op.type() == "conv2d"):
                weight_n = op.inputs()['Filter'][0].split(".quantized")[0]
                #print(weight_n)
                weight = state_dict[weight_n]
                #print(weight)

                #nonzero = np.count_nonzero(weight)
                #total = weight.size

                bitlength = ops_dict[op.inputs()['Input'][0].split(".dequantized")[0]][0].attr("bit_length")
                #print(bitlength)
                #return weight
                #(ASSUME the zero-point is at zero. TODOS)
                #print(op.attr('quantization_type'))
                #print(op.attr("


                analyze_tensor(weight, bitlength, stats)
                
                #stats['zeros'] = total - nonzero
                #stats['total'] = total
                
                #stats['precision'] = bitlength
                #stats['TotalBits'] = total*bitlength
                #stats['OneBits'] = sum([ bin(n).count('1') for n in weight.reshape((-1)) ]) #stats['TotalBits'] - 
                #stats['ZeroBitsRatio'] = 1 - ( stats['OneBits'] / stats['TotalBits'])
                #stats['sparsity'] = (stats['zeros'] / total)
 
                print(stats)#, state_dict[weight_n + ".quantized.dequantized@zero_point"])
                #return op
                
                #print(op.type())
                #return
            
                #continue
            #print(op_id)
            #print(ops_by_id.keys())
            #print(ops_by_id[op_id].outputs())

            order += 1
            sparsity.append(stats)

        lvl += 1
        #if lvl >= 20:
        #    print(sparsity)
        #    return
    
#analyze_sparsity(statistics, ops_by_id, state_dict)


# 导入依赖包
from PIL import Image
from paddle.vision.datasets import DatasetFolder
from paddle.vision.transforms import transforms
# 定义DataSet
class ImageNetDataset(DatasetFolder):
    def __init__(self, path, image_size=224):
        super(ImageNetDataset, self).__init__(path)
        normalize = transforms.Normalize(
            mean=[123.675, 116.28, 103.53], std=[58.395, 57.120, 57.375])
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(image_size), transforms.Transpose(),
            normalize
        ])

    def __getitem__(self, idx):
        img_path, _ = self.samples[idx]
        print(img_path)
        return self.transform(Image.open(img_path).convert('RGB'))

    def __len__(self):
        return len(self.samples)

# 定义DataLoader
#train_dataset = ImageNetDataset("./ILSVRC2012_data_demo/ILSVRC2012/train/")



#TODOS
#Not only weight sparsity, but also the input sparsity + any activations sparsity
def analyze_full_sparsity(statistics, ops_by_id, inputs, state_dict)\
:

    #analyze an example
    print(inputs)

    #First dequantize will be the input layer represented in INT
    sparsity = []
    lvl = 0
    order = 0


    activation_map = inputs
    scale = 1
    
    #(TODOS) analyze the activation_map's sparsity and potentially toggling rates
    
    for level in statistics['compute_order']:
        for op_id in level:
            op = ops_by_id[op_id]
            stats = {}
            print(op.type(), op.inputs(), op.outputs(), op.attr_names())
            stats['name'] = "_".join(op.outputs()[op.output_names()[0]])
            stats['order'] = order
            if(op.type() == "feed"):
                continue
                #stats['weight_sparsity'] = 'n/a'
            elif(op.type() == "quantize_linear"):
                #output = input / scale
                
                


                bitlength = op.attr("bit_length")
                if(bitlength <= 8):
                    cast = 'int8'
                else:
                    cast = 'int16'


                #print("*SCALE*=",state_dict[op.inputs()['X'][0]+"@scale"])                    
                activation_map = np.cast[cast](activation_map / state_dict[op.inputs()['X'][0]+"@scale"] * scale * 128) #* 20


                #print(activation_map)
                analyze_tensor(activation_map, bitlength, stats)

                scale = state_dict[op.inputs()['X'][0]+"@scale"][0] / 128
                #print("*SCALE*=",scale)
                print(stats)
                #return
            elif(op.type() == "dequantize_linear"):
                continue
            elif(op.type() == "conv2d"):
                weight_n = op.inputs()['Filter'][0].split(".quantized")[0]
                weight = state_dict[weight_n]

                conv = paddle.nn.Conv2D(in_channels=weight.shape[1], out_channels=weight.shape[0],
                                        kernel_size=weight.shape[-2:], stride = op.attr("strides"),
                                        padding = op.attr("paddings"),
                                        dilation = op.attr("dilations"),
                                        groups = op.attr("groups"), )
                conv.weight.set_value(paddle.to_tensor(weight, dtype="float32"))

                activation_map = conv(paddle.to_tensor(activation_map.reshape(((-1,)+activation_map.shape[-3:])), dtype="float32"))
                activation_map = np.cast['int16'](activation_map.numpy())
                #print(activation_map)
                analyze_tensor(activation_map, bitlength*2, stats)
                #paddle.nn.Conv2D(

                if(bitlength <= 8):
                    cast = 'int8'
                    activation_map = np.cast['int8'](activation_map)
                    #print(activation_map)
                print(stats)
            elif(op.type() == "batch_norm"):
                mean_n = op.inputs()['Mean'][0][0:-2]
                mean = state_dict[mean_n]

                offset_n = op.inputs()['Bias'][0][0:-2]
                offset =state_dict[offset_n]

                bn_scale_n =op.inputs()['Scale'][0][0:-2]
                bn_scale =state_dict[bn_scale_n]

                variance_n =op.inputs()['Variance'][0][0:-2]
                variance = state_dict[variance_n]
                #print(mean,offset,bn_scale,variance)
                #print("*SCALE*=",scale)
               
                
                mean = np.cast[cast](mean/scale).reshape((-1,)+variance.shape+(1,1,))
                offset = np.cast[cast](offset/scale).reshape((-1,)+variance.shape+(1,1,))
                bn_scale = np.cast[cast](bn_scale/scale).reshape((-1,)+variance.shape+(1,1,))
                variance = np.cast[cast](variance/scale).reshape((-1,)+variance.shape+(1,1,))

                #print(mean,offset,bn_scale,variance)


                activation_map = (activation_map - mean)/variance *bn_scale + offset

                #Should it be cast to int 8 instead ? but there is a multiply, should be int16 then.
                activation_map = np.cast['int16'](activation_map)

                
                analyze_tensor(activation_map, bitlength*2, stats)
                #print(activation_map)
                print(stats)
                return op
            else:
                print("UNKNOWN")
                return
                #return activation_map, weight, op
            order += 1
            sparsity.append(stats)

        lvl += 1





#todos, (pool_input_loop_order)
#todos, (..? what else ?)
#transformer is acombination of attention, elemetnwise, fully connected operations
#What about a dedicated transformer accelerator dataflow ？

#weight loop order for convolutions
def conv2d_weight_loop_order(op, weight, \
    input_height = 32, input_width = 32            \
                             , tx=1, ty=1, ti=8, tn=8, tb=1, batch = 1, loop_order = "os", SparsityStrategy = 0):

    #loop_order = "ws"
    
    #dilations/groups todos
    in_channels=weight.shape[1]
    out_channels=weight.shape[0]
    kernel_size=weight.shape[-2:]
    height_kernel_size = kernel_size[0]
    width_kernel_size = kernel_size[1]
    stride = op.attr("strides")[0]
    padding = op.attr("paddings")
    height_padding = padding[0]
    width_padding = padding[1]
    dilation = op.attr("dilations")
    groups = op.attr("groups") 

    is_first = False
    
    #"ws", "os", "is", "rs" etc.
    #curr_weight = np.zeros()
    #prev_weight = np.zeros()
    #ws stationary V1, only tile on the TI and TN layers
    prev_weight = []
    toggling = []
    t = 0


    
    if(loop_order == "os"):#diannano 
        for k in range(batch):
            for y in range(0, height_padding + input_height-height_kernel_size+1, stride):
                for x in range(0, width_padding + input_width-width_kernel_size+1, stride):
                    for nn in range(0, out_channels, tn):
                        for kx in range(width_kernel_size):
                            for ky in range(height_kernel_size):
                                for ii in range(0, in_channels, ti ):
                                    #performed per cycle, this is the data we want to analyze !
                                    #for n in range(nn, min(nn+self.TN, out_channels)):
                                    #   for i in range(ii, min(ii+self.TI, in_channels)):
                                    #weight[k, n, i, kx, ky]

                                    t += 1
                                    if(is_first == False):
                                        prev_weight = weight[ ii:min(ii+ti, in_channels) , nn:min(nn+tn, out_channels), kx, ky]
                                        is_first = True
                                    else:
                                        curr_weight = weight[ ii:min(ii+ti, in_channels) , nn:min(nn+tn, out_channels), kx, ky]
                                        if(prev_weight.shape != curr_weight.shape):
                                            prev_weight = curr_weight
                                            continue
                                        tog = prev_weight^curr_weight
                                        tog_count = sum([ bin(n).count('1') for n in tog.reshape((-1)) ])
                                        #print("time=",t,"tog_count",tog_count)
                                        toggling.append(tog_count)
                                        prev_weight = curr_weight
                                    
                                    #print(TILED, TILED.shape)
                        #return


    elif(loop_order == "ws_nvdla"):
        #in addition to ws, we also enable features such as input channel extension (i.e. for input channel = 3, we will
        #1. will actualy change the tiling to TI=3 x TN (TN is extended)
        #Also add features such as winograd (todos)
        print(" todos")
    elif(loop_order == "ws"):#nvdla style, Ascend Style
        for k in range(batch):
            for nn in range(0, out_channels, tn):
                for kx in range(width_kernel_size):
                    for ky in range(height_kernel_size):
                        for ii in range(0, in_channels, ti ):
                            for y in range(0, height_padding + input_height-height_kernel_size+1, stride):
                                for x in range(0, width_padding + input_width-width_kernel_size+1, stride):
                                    #performed per cycle, this is the data we want to analyze !
                                    #for n in range(nn, min(nn+self.TN, out_channels)):
                                    #   for i in range(ii, min(ii+self.TI, in_channels)):
                                    #weight[k, n, i, kx, ky]
                                    #TILED = weight[ ii:min(ii+ti, in_channels) , nn:min(nn+tn, out_channels), kx, ky]
                                    #print(TILED, TILED.shape)
                                    t += 1
                                    if(is_first == False):
                                        prev_weight = weight[ ii:min(ii+ti, in_channels) , nn:min(nn+tn, out_channels), kx, ky]
                                        is_first = True
                                    else:
                                        curr_weight = weight[ ii:min(ii+ti, in_channels) , nn:min(nn+tn, out_channels), kx, ky]
                                        if(prev_weight.shape != curr_weight.shape):
                                            prev_weight = curr_weight
                                            continue
                                        tog = prev_weight^curr_weight
                                        tog_count = sum([ bin(n).count('1') for n in tog.reshape((-1)) ])
                                        #print("time=",t,"tog_count",tog_count)
                                        toggling.append(tog_count)
                                        prev_weight = curr_weight

                                        
                        #return
    elif(loop_order == "is"):
        print("IS todos")
    elif(loop_order == "rs"):
        print("RS todos")
        return #todos
    else:
        print("undefined loop order")
        return
    print(toggling)
    print(sum(toggling)/(len(toggling)*ti*tn*tx*ty))
#Analyze the toggling
#only analyze the weight toggling behavior
def analyze_weight_toggling(statistics, ops_by_id, state_dict, \
                            tx = 1, ty = 1, ti = 8, tn = 8, tb = 1, loop_order = "ws" , SparsityStrategy = 0)\
:

    #analyze an example
    #print(inputs)

    #First dequantize will be the input layer represented in INT
    sparsity = []
    lvl = 0
    order = 0

    
    #(TODOS) analyze the activation_map's sparsity and potentially toggling rates
    
    for level in statistics['compute_order']:
        for op_id in level:
            op = ops_by_id[op_id]
            stats = {}
            print(op.type(), op.inputs(), op.outputs(), op.attr_names())
            stats['name'] = "_".join(op.outputs()[op.output_names()[0]])
            stats['order'] = order
            if(op.type() == "feed"):
                continue
            elif(op.type() == "quantize_linear"):
                continue
            elif(op.type() == "dequantize_linear"):
                continue
            elif(op.type() == "conv2d"):
                weight_n = op.inputs()['Filter'][0].split(".quantized")[0]
                weight = state_dict[weight_n]

                #analyze the neural network via tiling
                conv2d_weight_loop_order(op, weight, tx=tx, ty=ty, ti=ti, tn=tn, tb=tb, loop_order = loop_order, SparsityStrategy = SparsityStrategy)                
                
                return
                conv = paddle.nn.Conv2D(in_channels=weight.shape[1], out_channels=weight.shape[0],
                                        kernel_size=weight.shape[-2:], stride = op.attr("strides"),
                                        padding = op.attr("paddings"),
                                        dilation = op.attr("dilations"),
                                        groups = op.attr("groups"), )
                conv.weight.set_value(paddle.to_tensor(weight, dtype="float32"))

                activation_map = conv(paddle.to_tensor(activation_map.reshape(((-1,)+activation_map.shape[-3:])), dtype="float32"))
                activation_map = np.cast['int16'](activation_map.numpy())
                #print(activation_map)
                analyze_tensor(activation_map, bitlength*2, stats)
                #paddle.nn.Conv2D(

                if(bitlength <= 8):
                    cast = 'int8'
                    activation_map = np.cast['int8'](activation_map)
                    print(activation_map)
                print(stats)
            elif(op.type() == "batch_norm"):
                continue
            else:
                print("UNKNOWN")
                return
                #return activation_map, weight, op
            order += 1
            sparsity.append(stats)

        lvl += 1
    



############################FROM IO.PY of version 2.4.1 paddlepaddle###########
#We assume the model here is already quantized (i.e. to something less than 32/64 floating)
#such as 8-bit INT, 4-bit INT for example
#(Todos) do we support 8-bit FP or 4-bit FP?

DEBUG = 1


file_path = "./benchmarks/paddle/ResNet50_vd_QAT/inference"
file_path = "./benchmarks/paddle/efficientnetb0_QAT/inference"
file_path = "./benchmarks/paddle/PPHGNet_tiny_QAT/inference"
file_path = "./benchmarks/paddle/GhostNet_x1_0_QAT/inference"
file_path = "./benchmarks/paddle/ShuffleNetV2_x1_0_QAT/inference"
file_path = "./benchmarks/paddle/ViT_base_patch16_224_QAT/inference"
#file_path = "./benchmarks/paddle/efficientnetb0_QAT/inference"
file_path = "./benchmarks/paddle/ShuffleNetV2_x1_0_QAT/inference"
file_path = "./benchmarks/paddle/PPHGNet_tiny_QAT/inference"
file_path = "./benchmarks/paddle/efficientnetb0_QAT/inference"
file_path = "./benchmarks/paddle/ResNet50_vd_QAT/inference"
file_path = "./benchmarks/paddle/efficientnetb0_INT8/inference"
file_path = "./benchmarks/paddle/ResNet50_vd_QAT/inference"


b = 'efficientnetb0_UnstructurePrune0.5_INT8'#'efficientnetb0_UnstructurePrune0.2_INT8'#'efficientnetb0_UnstructurePrune0.5_INT8'#"efficientnetb0_ChannelPrune0.5_INT8"
b = 'efficientnetb0_UnstructurePrune0.5_INT4'#'efficientnetb0_UnstructurePrune0.2_INT4'

#b = 'GhostNet_x1_0_QAT'
#b = 'MobileNetV3_large_x1_0_QAT'


file_path = "./benchmarks/paddle/%s/inference" %(b)
picture = 0

dataset = "./ILSVRC2012/train"


ti = 3
tn = 3
loop_order = "ws"


model_file_path =file_path+".pdmodel"
params_file_path = file_path+".pdiparams"


#(TODO there is a bug in the origianl repository, the loading will fail because it will consume a "fetch" or "scale" that could be None type by accident )
state_dict = paddle.load(file_path)

def parse(model_file_path, DEBUG = 0):
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
    ops_dict = {}
    ops_by_id = {}
    for i in six.moves.range(root_block.op_size()):
        op = root_block.op(i)

        #if ("add" in op.type()):
        #print(i, op.type(), op.inputs(), op.outputs())

        #if("Y" in op.inputs()):
        #    print(i, op.type(), op.inputs(), op.outputs())

        if op.type() == 'feed':
            compute_head = op
            #op.
            print(op.type())
            #break
        #print(op.type(), op.inputs())
        if('Input' in op.inputs()):
            op_x = op.inputs()['Input']
        elif("X" in op.inputs()):
            op_x = op.inputs()['X']
        else:
            print("WARNING: Skipping ", op.type(), op.inputs())
            continue

        #exceptional case
        if "Y"  in op.inputs() and ("elementwise" in op.type() or "matmul" in op.type()) \
            and not key_in_list("fc", op.inputs()["Y"]) and not key_in_list("b_0", op.inputs()["Y"])\
            and not key_in_list("w_0", op.inputs()["Y"])\
            and not key_in_list("_", op.inputs()["Y"], 0):
            op_x += op.inputs()["Y"]

        if "expand_shapes_tensor" in op.inputs():
            op_x = []
            for ins in op.inputs()['expand_shapes_tensor']:
                if("fill_constant" not in ins):
                    op_x.append(ins)
                    
        #if "Y" in op.inputs() and "elementwise_add" in op.type():
        #    print("ELEMENTWISE", op_x, op.inputs()["Y"])
        #if(len(op_x) >= 2):
            #print(op_x)
            
        #if('sigmoid' in op_x):
        if DEBUG:
            print(op.id(),op.type(), op.inputs(), op.outputs(), op_x)
        #    #break
        for x in op_x:
            #print(x)
            #if("sigmoid" in x):
            print(op_x, op.id(), op.type(), op.inputs(), op.outputs())
            if(x not in ops_dict):
                ops_dict[x] = []

            #make uniqufiy
            skip_add = False
            for x_idx, oo in enumerate( ops_dict[x] ):
                for l in oo.outputs():
                    #print(l)
                    if(l in op.outputs() and oo.outputs()[l] == op.outputs()[l]):
                        #print("^^^^^^^^^^^^^^^^^^^^^^^")
                        if DEBUG:
                            print("WARNING: Duplicated operation in paddle model, uniquifying")
                        if(op.type() == "quantize_linear"):
                            #choose any
                            skip_add = True
                        elif(op.type() == "dequantize_linear"):
                            #choose the one with zero_point is dequantized, always the second
                            skip_add = True
                            ops_dict[x_idx] = op_x
                        if DEBUG:
                            print(" --> ", op.id(),op.type(), op.inputs(), op.outputs(), op_x)
                            print(" --> ", oo.id(),oo.type(), oo.inputs(), oo.outputs(), op_x)
                        #print("^^^^^^^^^^^^^^^^^^^^^^^")
            #ops_dict[x].append(op)

            if(skip_add):
                continue
            else:
                ops_dict[x].append(op)
                
        ops_by_id[op.id()] = op
    return compute_head, ops_dict


if __name__ == "__main__":
    compute_head, ops_dict = parse(model_file_path)
    #exit()
    #2. found the computing order and graph
    statistics = compute_summary(compute_head, ops_dict)

    #3. sparsity analysis (weight)
    weight = analyze_sparsity(statistics, ops_by_id, state_dict = state_dict)


    #3. sparsity analysis (including data)
    train_dataset = ImageNetDataset(dataset)
    analyze_full_sparsity(statistics, ops_by_id, state_dict=state_dict, inputs = [train_dataset[picture]])



    #4. toggling analysis (weight)

    #SparsityStrategy = 0 (No sparsity gating/skipping max togglings, 1(ZeroGated), 2 (SparsitySkipping), 3 (ZeroGated + SparsitySkipping)
    analyze_weight_toggling(statistics, ops_by_id, state_dict, \
                                tx = 1, ty = 1, ti = ti, tn = tn, tb = 1, loop_order = loop_order,
                                SparsityStrategy = 0 )




    #4. toggling analysis (tiling-based toggle-level, accumulator-level, others?)
    #   three types:
    #     1. dense DLA (and variants)
    #     2. sparse DLA
    #       2.1. Clock-Gated
    #       2.2. Encoded/Index-Based


    #parse(model_file_path, params_file_path)
