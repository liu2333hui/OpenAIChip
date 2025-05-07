#new_path = "/nfs/project/JayMok/power_experiments_xie/primitives"
#os.environ['LD_LIBRARY_PATH'] = os.pathsep.join([new_path, os.environ.get('LD_LIBRARY_PATH', '')])
#print(os.environ['LD_LIBRARY_PATH'])
IS_LINUX = 1
SBT = "/afs/ee.ust.hk/staff/ee/jaymok/.local/share/coursier/bin/sbt"
import sys
#power_models_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(power_models_dir)
#power_models_dir = os.path.dirname(os.path.abspath(__file__) + "/power_models")
#sys.path.append(power_models_dir)
DEBUG = 0

import copy



if(IS_LINUX):
	import ctypes
	ctypes.CDLL('/nfs/project/JayMok/power_experiments_xie/primitives/libstdc++.so.6')
	ctypes.cdll.LoadLibrary('/nfs/project/JayMok/power_experiments_xie/primitives/libstdc++.so.6')
import numpy as np
import paddle.nn as nn
import os
import json
import pandas as pd
import os


############################
from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
#from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive	
from power_models.MaxNPrimitive import MaxNPrimitive
from power_models.CrossbarPrimitive import CrossbarPrimitive
from power_models.MuxNPrimitive import MuxNPrimitive
from power_models.SRAMSPrimitive import SRAMSPrimitive
from power_models.SRAMSPrimitive import SRAMSPrimitive
from power_models.DeserializerPrimitive import DeserializerPrimitive
	


############################



#general helper to generate cpp files
#Helpers

def dict_values_to_str(d):
    if isinstance(d, dict):  # 如果是字典
        return "_".join(dict_values_to_str(v) for v in d.values())
    elif isinstance(d, list):  # 如果是列表
        return "_".join(dict_values_to_str(item) for item in d)
    else:  # 其他类型（如字符串、整数等）
        return str(d)

    if isinstance(d, dict):  # 如果是字典
        return "{" + ", ".join(f"{k}: {dict_to_str(v)}" for k, v in d.items()) + "}"
    elif isinstance(d, list):  # 如果是列表
        return "[" + ", ".join(dict_to_str(item) for item in d) + "]"
    elif isinstance(d, int):  # 如果是整数
        return str(d)
    else:  # 其他类型（如字符串、浮点数等）
        return str(d)

def dict_to_str(d):
	return dict_values_to_str(d)


#given a loop order
# [X, Y, Z]
# ONly want certain, [filter = [X,Z]]
def filter_loop_order(loop_order, valid_loops):
	ll = []
	for l in loop_order:
		if l in valid_loops:
			ll.append(l)

	return ll
	


def log1p_inverse(x):
	return np.exp(x) - 1
		

def trace_file(num, TRACE_FILE, input_data, r = 1, signal_name="in"):
	print("TRACE_FILES: ", TRACE_FILE)
	print(num)	
	for t in range(num):
		#swap with an array
		file_path = TRACE_FILE[t]#f"{TRACE_FILE}_{t}"#+str(t)
		print(file_path)
		result = []
		# 打开文件进行读取
		with open(file_path, 'r') as file:
			# 读取所有行
			lines = file.readlines()
			
			# 遍历每一行
			for line in lines:
				# 按空格分割每行数据
				row_data = [int(num) for num in line.strip().split()]
				#print(row_data)
				# 若结果列表为空，先初始化结果列表
				if not result:
					result = [[] for _ in range(len(row_data))]
				# 将每行数据添加到对应列的列表中
				for i, num in enumerate(row_data):
					result[i].append(num)
			#print(result)
		input_data[f"{signal_name}_{t}"] = [re for re in result]

	print(input_data.keys())
	return input_data
	

def bit_count_helper():
	return """
	// 计算单个数字的1的数量
	int countBits(int num) {
	    int count = 0;
	    while (num) {
	        num &= (num - 1); // 清除最低位的1
	        count++;
	    }
	    return count;
	}
	
	// 对整个数组进行计算，并保存到新数组
	int* countBitsInArray(int* arr, int size) {
	    // 创建一个新数组，用于存储每个数字的1的数量
	    int* bitCounts = new int[size];
	
	    // 遍历原始数组，计算每个数字的1的数量
	    for (int i = 0; i < size; i++) {
	        bitCounts[i] = countBits(arr[i]);
	    }
	
	    return bitCounts; // 返回新数组
	}
	"""

def cpp_read_file_helper():
    return '''
#include <iostream>
#include <fstream>
#include <cstdlib>  // Pour malloc et free

// Helper functions
// Fonction pour lire un fichier et stocker les valeurs dans un tableau
int* lireFichierEtRemplirTableau(const char* filename, int*size, int count) {
		std::ifstream file(filename);
		if (!file.is_open()) {
			std::cerr << "Erreur : Impossible d'ouvrir le fichier.\t" <<filename <<std::endl;
			
			return nullptr;
		}

		int count2 = 0;
		std::string line;
		while (std::getline(file, line)) {
			count2++;
		}

		file.clear();  // Effacer les flags d'erreur
		file.seekg(0); // Retourner au début du fichier

		int* array = (int*)malloc(count * sizeof(int));
		if (array == nullptr) {
			std::cerr << "Erreur : chec de l'allocation mémoire." << std::endl;
			file.close();
			return nullptr;
		}

		// Initialiser le tableau avec des zéros
		for (int i = 0; i < count; i++) {
			array[i] = 0;
		}

		int index = 0;
		while (std::getline(file, line)) {
			array[index] = std::stoi(line); // Convertir la ligne en entier
			index++;
		}

		file.close();

		*size = count2;

		return array;
	}
	'''

#Adder Tree
def AdderAccumulateComponent(ADDER_TYPE, valid_nets, self, unit_name, loop_order, cast_skips, input_group, units, bins, prec, data_obj, update, out_prec, loop_var = {} ):

	if(ADDER_TYPE == "ACCUM"):
		if(unit_name in valid_nets):
			config = {
				unit_name : {

					"loop_order": loop_order,
					"cast_skips": cast_skips,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					#"input_bins": [self.hc[prec] ] * len(bins),	

					"units":units,
	
					"data_obj": data_obj,

	
	
					'input_group': 1,
					"accumulated_input": True,
				"globally_accumulate_output": True,
				"globally_accumulate_reset_trigger": [],

				"cur_update": ['accumulate_{}[]'],
				'cur_update': ['accumulate_max_tree_accum[max_accum]'], #value	
				'prev_update': [ 'std::max(accumulate_max_tree_accum[max_accum], prev_max_accum[max_accum][0] )' ]  ,#['weights_data', 'inputs_data'],

				"config": {
					"primitive": "maxmin.MaxAccumulator",
					"MaxType": self.hc["MAXACCUM_TYPE"],
					"prec":self.hc["MAXACCUM_PREC"],
					"out_prec":self.hc["MAXACCUM_PREC"] ,
					"terms": 1,
				}
					
			}
		}
		if(len(loop_var) > 1):
				config[unit_name].update({
				"loop_var": loop_var,
	})
	
		self.MODULES.update(config)



	if(ADDER_TYPE == "ADDER_TREE"):	

		if(unit_name in valid_nets):
			config = {
				unit_name : {

					"loop_order": loop_order,
					"cast_skips": cast_skips,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [self.hc[prec] ],	
	
					'input_group': input_group,
					"data_obj": data_obj,

	
					"units":units,
	

				"cur_update": [update],
				'accumulate': True,#meaning the output is accumulated
				'accumulate_op': f'std::max(accumulate_{unit_name.lower()}[group_{unit_name.lower()}], {update})',	

			"config": {
					"primitive": "adders.AdderN",
					#"AdderType": self.hc["TYPE"],
					#"AdderCoreType": self.hc["CORE_TYPE"],
					"adderNType": self.hc["ADDERN_TYPE"],
					"adderType": self.hc["CORE_ADDER_TYPE"],
					"prec_in":self.hc[prec],
					"prec_sum":self.hc[out_prec] ,
					"terms": input_group#self.hc["TKX"]*self.hc["TKY"]
				}	
			}}
			if(len(loop_var) > 1):
				config[unit_name].update({
				"loop_var": loop_var,
	})
	
			self.MODULES.update(config)


#SRAM Memory
def MemoryComponent(valid_nets, self, unit_name, loop_order, cast_skips, units, bins = ['weights_data'], prec = "PREC", data_obj = ['weights_obj'], runtime_lambda = lambda p : SIZE // p['avg_cycle_per_op'], fanout = 1 , ratio = 1, loop_var = {}, CustomMap = {}, SRAM_SIZE = "L1_OUT_SRAM_SIZE", SRAM_TYPE = "L1_OUT_SRAM_TYPE", MODE = 0):	
	if 1:
		if(unit_name in valid_nets):
			self.MODULES.update({
				unit_name : {
					"loop_order": loop_order,
					"cast_skips": cast_skips,
					"runtime": lambda p: OUTPUT_SIZE(p) // L1_OUT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": data_obj,

					"units":units,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [self.hc[prec] ] * len(bins),	
					'cur_update': bins,
					'input_group': 1,
					"unit_time_unrolled": [ ratio ],
					"trace_merge_units": self.hc[SRAM_SIZE][0] // self.hc[prec],
					"trace_merge_prec": self.hc[prec],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc[SRAM_TYPE],
						"entry_bits": self.hc[SRAM_SIZE][0],
						"rows": self.hc[SRAM_SIZE][1],	
						"mode": MODE,#0 is read, 1 is write
					}
				},

			})

#deserializer and serializer
def NetworkComponent(valid_nets, self, unit_name, loop_order, cast_skips, units, bins = ['weights_data'], prec = "PREC", data_obj = ['weights_obj'], runtime_lambda = lambda p : SIZE // p['avg_cycle_per_op'], fanout = 1 , ratio = 1, loop_var = {}, CustomMap = {}):
	#ratio > 0, means parallel2serial
	#make all inner so we can use input_group param
	#loop_var = copy.deepcopy(self.LOOP_VAR_DEFINITIONS)
	#for x in loop_var:
	#loop_var[x]["GROUP"] = "INNER"


	if(ratio < 0):
		unit_time_unrolled = [1]
		input_group = abs(ratio)	
	#ratio < 0, means Serial2parallel, deserialier
	else:
		unit_time_unrolled = [abs(ratio)]*len(bins)
		input_group = 1	
	
	#ratio = unit_time_unrolled
	if(unit_name in valid_nets):
		#ratio = self.hc["LOAD_RATIO"]
		prec = self.hc["PREC"]
		typ  = self.hc["NETWORK_TYPE"]
		config = {
			unit_name: {	
			"units_select": input_group,
				"loop_order" : loop_order,#filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "N", "B"]),
				"cast_skips": cast_skips,#["TB", "TX", "TY"],
				"runtime": runtime_lambda,#lambda p: OUTPUT_SIZE(p) // L1_OUT_BUF_BIT_LEN * p['avg_cycle_per_op'],
				"data_obj": data_obj,#["outputs_obj"],		
				"units": units,#L1_OUT_BUF_BIT_LEN,
				"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
				"input_bins": [prec]*len(bins),#[self.hc["PREC"]],	
				'cur_update': bins,# ['outputs_data'],
				'input_group': input_group,

				"unit_time_unrolled": unit_time_unrolled,#[ratio ],
			},
		}
		
		if(len(loop_var) > 1):
			config[unit_name].update({
				"loop_var": loop_var,
			})
			# meaning small2big at read, so write big2small, serializer 
			#meaning serial2parallel
		if(ratio < 0): #meaning we are small to big, Deserializer. 
			config[unit_name].update({	
					"config": {
						"primitive": "networks.Parallel2Serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": fanout,
						}
					})	
		else:
			config[unit_name].update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": fanout,
						}
					})	

		config[unit_name]['config']['CustomMap'] = CustomMap

		self.MODULES.update(config)




def MultiplierComponent(valid_nets, self, unit_name, loop_order, units, bins = ['weights_data', 'inputs_data'], main = "weight", wei_prec = "WEI_PREC", act_prec = "ACT_PREC", data_obj = ["inputs_obj", "weights_obj"], runtime_lambda =lambda p: MAC_NO //  p['avg_cycle_per_op'], cast_skips = [] ):

	side = main
	if(unit_name in valid_nets):
		if(self.hc["MULT_SIDE"] == main):
			MULT_update = bins#['weights_data', 'inputs_data']		
			MULT_prec1 = self.hc[wei_prec]
			MULT_prec2 = self.hc[act_prec]	
			MULT_bins = [MULT_prec1, MULT_prec2]
		else:
			MULT_update = bins[::-1]#['weights_data', 'inputs_data'][::-1]
			MULT_prec1 = self.hc[act_prec]
			MULT_prec2 = self.hc[wei_prec]	
			MULT_bins = [MULT_prec1, MULT_prec2]
		config = {
				unit_name: {
					"loop_order": loop_order,# self.hc["LOOP_ORDER"],
					"cast_skips": cast_skips,
					"runtime": runtime_lambda,
					"data_obj":data_obj, # ["inputs_obj","weights_obj"],

					"units": units, #TILE,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": MULT_bins,#[MULT_prec1, MULT_prec2],	
					'cur_update': MULT_update,
					'input_group': 1,

					"config": {
						"primitive": "multipliers.Multiplier2",
						"multiplierType": self.hc["MULT_TYPE"],
						"radix": self.hc["MULT_RADIX"],
						"prec1": MULT_prec1,
						"prec2": MULT_prec2,
						"side": self.hc.get("SIDE", "weight"),
						"adderType": self.hc["MULT_CORE_ADDER_TYPE"],
					}
				},			
			}	

		if(self.hc["MULT_TYPE"] == "ConstantMultiplier2" or self.hc["MULT_TYPE"] == "ConstantMultiplier"):
			config[unit_name].update({
			"config": {	
				"CustomMap": {"in_1": "Constant"},
				"primitive": "multipliers.ConstantMultiplier2",
				"multiplierType": self.hc["MULT_TYPE"],
				"out_prec": MULT_prec1+MULT_prec2,
				"terms": 1,
				"prec1": MULT_prec1,
				"prec2": MULT_prec2,
				"side": self.hc.get("SIDE", "weight"),
				"adderType": self.hc["MULT_CORE_ADDER_TYPE"],	
			},})
		else:	
			config[unit_name].update({

			"config": {
				"primitive": "multipliers.Multiplier2",
				"multiplierType": self.hc["MULT_TYPE"],
				"out_prec": MULT_prec1+MULT_prec2,
				"terms": 1,
				"prec1": MULT_prec1,
				"prec2": MULT_prec2,
				"radix": self.hc["MULT_RADIX"],
				"side": self.hc.get("SIDE", "weight"),
				"adderType": self.hc["MULT_CORE_ADDER_TYPE"],
			},})

		self.MODULES.update(config)		
	



def core_cpp(NET_DATA, is_group_loop = False, debug=False, DEBUG = DEBUG):	
	s = ""
	for n in NET_DATA:


		net = n.lower()
		n = NET_DATA[n]

		units = n['units']
		accumulate = n.get('accumulate', False)
		accumulate_op = n.get('accumulate_op', "")
	
		accumulated_input = n.get('accumulated_input',False)
		num_inputs =len( n['input_bins'])
		prev_update = n.get('prev_update', [])


		cur_update = n.get('cur_update', [])
	
		output_update = n.get('output_update', '0')
		group = n['input_group']

		output_inner_group = n['adjusted_output_inner']
		#output_condition = n['output_condition']
		output_update = n.get('output_update', "")

			
	
		#s += f"{n} - {accumulated_input};"
		if(not is_group_loop):
			if(accumulated_input):
				#s += 'std::cout << "skip" << {n} << std::endl;\n'
				continue
		else:
			if(not accumulated_input):
				#s += 'std::cout << "skip" << {n} << std::endl;\n'
	
				continue
	

		for m in n['input_metadata']:

			#meta_aggregate = n['input_metadata'][m]['aggregate']
			meta_update = n['input_metadata'][m]['update']
			s += f'''
			if(sim_cycles >= 0){{
			'''
			if(debug):
				s += f'''
			std::cout << "start" << std::endl;
			'''

			update_condition = n.get('update_condition', ['1']*num_inputs)
			for jjj in range(num_inputs):#(int jjj = 0 ; jjj < {num_inputs}; jjj++)
				update_if = update_condition[jjj]
	
				s += f'''if({update_if}){{'''
	
				s += f'''
					cur_{net}[{net}_{jjj}][{jjj}] = {cur_update[jjj]};
					if({DEBUG}) std::cout << "DEBUG: Updated {net}_{jjj}, s="<<sim_cycles<<"\t" << {net}_{jjj}<< "\t" << {cur_update[jjj]} <<"\t"<<{jjj}<< std::endl;
					updated_{net}[group_{net}][{jjj}]++;//meaning we updated a net, it passed the filter	
				'''	

				s += f''' }}else{{
					{net}_{jjj}--;//don't update the index, go back one
				}}
				'''	
 
			s += f'''
			//int update = update; 	
			//int prev_update = prev_{net}[{net}];
			//{m}_{net}[{net}][__builtin_popcount(update^prev_{net}[{net}])]++;					''' 
			s += f'''
			for(int jjj = 0; jjj < {num_inputs}; jjj++){{
				//{m}_{net}[{net}_{jjj}][{meta_update}]++; 
			}}
			'''	
			s += f'''
			}}
			'''


		
		for jjj in range(num_inputs):#(int jjj = 0 ; jjj < {num_inputs}; jjj++)
			
			if(len(prev_update) == 0):
				prev = f'cur_{net}[{net}_{jjj}][{jjj}]'		
			else:
				prev = prev_update[jjj]

			if(debug):
				s += f'std::cout <<"net\t"<< {net}_{jjj} << {prev} << std::endl;'	

			
				s += f'std::cout <<"net\t"<< {net}_{jjj} << {prev} << std::endl;'	
	
			s += f'''
					prev_{net}[{net}_{jjj}][{jjj}] = {prev};
				'''
			#if(need_trace):
			#	s += (f'goldenOutFile_{net}_{jjj} << {prev_update[jjj]}  << "\\n";\n');



		#take care of output updating, if accumulating skip and move forward
		if(debug):
			s += 'std::cout << "start accum" <<std::endl;'
	
		#s += f"int out_update_{net} = {output_update};\n"
	
		#print(n['output_metadata'])
		for m in n.get('output_metadata',{}):
			meta_update = n['output_metadata'][m]['update']
	
			if(accumulate):
				s += f"accumulate_{net}[group_{net}_{jjj}] = {accumulate_op};"	
			else:
				s += f'out_{m}_{net}[{net}_{jjj}][{meta_update}]++;' 	

				#what to do ?

				#for m in n['output_metadata']:
				#s += ("out_prev_{net}[{net}] = {output_update};")						
		if(debug):	
			s += f'''
			//std::cout << "done accum" <<std::endl;
			'''
		s += f'''
			{net} = ({net}+1);
		'''
		for jjj in range(len(n['input_bins'])):
			s += f'{net}_{jjj}++;\n'



	return s
#run_it --> run the ./a.out
#need_trace --> this is for the acutal data, tracing like vcd
def generate_cpp(root,name,PARAMETERS,DATA,NETS, loop_order, valid_loops, tiling_pre = "CNN_T",hardware_config = {}, SIM_CYCLE_LIM = -1,hooks = {
				"core_before_outer_group_start": "",
				"core_before_inner_group_start": "",
				"core_after_inner_group_start":"",
				"core_after_data_fetch":"",
				"core_after_inner_group_end":"",
				"core_after_outer_group_end": ""
				}		, run_it=True, need_trace=False,	
debug = 0,#False and True,
DEBUG = DEBUG,
inner_loops_skips = []
):
	if(os.path.isdir("generated/out")):
		pass
	else:
		os.mkdir("generated/out")
	orig_name = "generated/out/" + root.split("/")[-1] + "_"+name

	hooks["core_before_global_loop_start"] = hooks.get("core_before_global_loop_start", "")
	hooks["core_before_outer_group_start"] = hooks.get("core_before_outer_group_start", "")
	hooks["core_before_inner_group_start"] = hooks.get("core_before_inner_group_start", "")	
	hooks["core_after_inner_group_start"] = hooks.get("core_after_inner_group_start", "")
	hooks["core_after_data_fetch"] = hooks.get("core_before_after_data_fetch", "")
	hooks["core_after_inner_group_end"] = hooks.get("core_after_inner_group_start", "")
	hooks["core_after_outer_group_end"] = hooks.get("core_after_outer_group_start", "")

	PRE = tiling_pre
	OUTPUT_FILES = {}
	if True:
		NET_DATA = NETS
		#1. define files
		for n in NET_DATA:
			rep = n	
		CPP_FILE = root + "/"+name+"."+rep+".cpp"
		name = name + "."+str(abs(SIM_CYCLE_LIM))
		for n in NET_DATA:
			OUTPUT_FILES[n] = {}
	
			#TOGGLING_FILE is the toggling data
			#TRACE_FILE is the actual data
			#JSON file is the json used by scala
			#POWER GOLDEN FILE is the golden ptpx
			#RUNTIME file is related with the timing
			#(todos) AREA file is related with the area
			BASE = root + "/" + name + "." + n + "."	
	
			NET_DATA[n]['TOGGLING_FILE'] = BASE+"toggling"
			NET_DATA[n]['OUTPUT_TOGGLING_FILE'] = BASE+"out.toggling"


			NET_DATA[n]['TRACE_FILE'] = BASE+"trace"
			NET_DATA[n]['JSON_FILE'] =  BASE+"json"
			NET_DATA[n]['POWER_GOLDEN_FILE'] = BASE+"golden"	
			NET_DATA[n]['RUNTIME_FILE'] = BASE+"runtime"	

			#TOGLGING_FILE is INPUT_TOGGLING_FILE
			#OUTPUT_FILES[n]["BASE"] = 


			OUTPUT_FILES[n]['TOGGLING_FILE'] = BASE+"toggling"
			OUTPUT_FILES[n]['OUTPUT_TOGGLING_FILE'] = BASE+"out.toggling"
			OUTPUT_FILES[n]['TRACE_FILE'] = BASE+"trace"
			OUTPUT_FILES[n]['JSON_FILE'] =  BASE+"json"
			OUTPUT_FILES[n]['POWER_GOLDEN_FILE'] = BASE+"golden"	
			OUTPUT_FILES[n]['RUNTIME_FILE'] = BASE+"runtime"	

			OUTPUT_FILES[n]["GEN_TRACE_FILES"] = []

			#for n in NET_DATA:
			if 1:
				net_orig = n
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				units = n['units']
	
				group = n['input_group']
				TOGGLING_FILE = n['TOGGLING_FILE']#'#root+"/"+name+f".{net}.trace"
				TRACE_FILE = n['TRACE_FILE']
				OUTPUT_TOGGLING_FILE = n['OUTPUT_TOGGLING_FILE']
				
				units = n['units']//group
				prec = n['input_bins']
				prec = 1
				for i in n['input_bins']:
					prec *= i


				output_prec = n.get('output_bins',8)
				


				#inputs now
				units = n['units']
				group = n['input_group']
				num_inputs =len( n['input_bins'])
	
				split_inputs = n.get("split_inputs", 1)
				num_inputs *= split_inputs
			
				if(need_trace):
					inner_unroll = n.get('input_time_unrolled', [1]*num_inputs)
					unit_unroll = n.get("unit_time_unrolled", [1]*num_inputs)
					hold = n.get("input_hold_cycles", [1]*num_inputs)

					trace_merge_prec = n.get('trace_merge_prec', 8)
					trace_merge_units = n.get('trace_merge_units', 1) 						
					#for (int g = 0 ; g < {group}; g++){{
					#	for (int jjj = 0; jjj < {num_inputs}; jjj++){{
					c = hardware_config
	

					casting_skip = n.get("units_select", 1)
					for sss in inner_loops_skips:
						casting_skip*= c[sss]

					#f.write(f"int casting_skip = {casting_skip};")
	
					for jjj in range(num_inputs):
						unrolled = inner_unroll[jjj]
						group_unrolled = group//unrolled

						#print(group_unrolled, group, unrolled)	
						
						for g in range(group_unrolled):
							i = jjj + num_inputs*g
							trace_file_name = n.get('input_trace_name',['in']*num_inputs)[jjj]
							gen_trace_file = f"{TRACE_FILE}.{trace_file_name}_{jjj}_{g}"
							print(gen_trace_file)

	
							OUTPUT_FILES[net_orig]["GEN_TRACE_FILES"].append(gen_trace_file)	
		if(not run_it and need_trace):
			return OUTPUT_FILES
	

		with open(CPP_FILE, "w") as f:
			f.write("#include <iostream>\n")
			f.write("#include <algorithm>\n")
			f.write(cpp_read_file_helper())
			f.write(bit_count_helper())
			f.write("\nint main(){\n")


			for p,v in PARAMETERS.items():
				f.write(f"\tint {p} = {v};\n")


			for i in DATA:
				name = i['name']
				filename = i['file']
				size = i['size']
				f.write(f"\tint {name}_size;\n")
				f.write(f"\tint* {name} = lireFichierEtRemplirTableau(\"{filename}\", &{name}_size, {size});\n") 	


			for nk in NET_DATA:
				n = NET_DATA[nk]
				net =nk.lower()# n["net"]
				units = n['units']
				prec = 1
				for i in n['input_bins']:
					prec *= i
				#prec = n['input_bins']
				num_inputs = len(n['input_bins'])
				
				for m in n['input_metadata']:
					
					f.write(f'''
	int {m}_{net}[{units}][{prec}];
	for (int k = 0; k < {units}; k++)
	for (int j = 0; j < {prec}; j++) {{
		{m}_{net}[k][j] = 0;
	}}''')


				#this keeps track of the actual out value
				
				if(n.get('accumulated_input', False)):
					output_inner_group = 1
				else:
					output_inner_group = n.get('output_inner_group', n['input_group'])
				output_outer_group = n.get('output_outer_group', n['units'])

				NET_DATA[nk]['adjusted_output_inner'] = output_inner_group
				NET_DATA[nk]['adjusted_output_outer'] = output_outer_group	
				#adjusted_output_inner = n['adjusted_output_inner']

				f.write(f'''
	int out_value_{net}[{units}][{output_inner_group}];
	int prev_out_value_{net}[{units}][{output_inner_group}];
	for (int k = 0; k < {units}; k++){{
		for (int j = 0; j < {output_inner_group}; j++) {{
			out_value_{net}[k][j] = 0;
			prev_out_value_{net}[k][j] = 0;
		}}
	}}
				''')

				#this keeps track of toggling and meta data
				for m in n.get('output_metadata', {}):
					
					f.write(f'''
					int out_{m}_{net}[{units}][{prec}];
	
					for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {prec}; j++) {{
							out_{m}_{net}[k][j] = 0;

					}}''')


				groups = n['input_group']
				total_units = units * groups
				f.write(f'''
	int prev_{net}[{total_units}][{num_inputs}];
	int cur_{net}[{total_units}][{num_inputs}];
	
	for(int k = 0; k < {total_units}; k++){{
		for (int j = 0; j < {num_inputs}; j++){{
			prev_{net}[k][j] = 0;
			cur_{net}[k][j] = 0;	
		}}
	}}					
				''')
				if(debug):
					f.write(f'std::cout << "// Analyzing Workload" << std::endl;\n')
	
			# neck
			if True:
				#body 
				if(debug):
					f.write(f'std::cout << "// Analyzing Workload" << std::endl;\n')


			for n in NET_DATA:
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				group = n['input_group']
				num_inputs =len( n['input_bins'])
	
				TRACE_FILE = n['TRACE_FILE']#'#root+"/"+name+f".{net}.trace"
				#for i in range(num_inputs):#terms = FC_TI for adder tree	
				#	f.write(f'std::ofstream goldenOutFile_{net}_{i}("{TRACE_FILE}_{i}");\n');

			#3.5
			#variable init	
			f.write(f'\n\tint sim_cycles = -1;\n')	
			if(need_trace):
				for n in NET_DATA:
					net = n.lower()
					n = NET_DATA[n]
					units = n['units']
					
					accumulate = n.get('accumulate', False)
					num_inputs =len( n['input_bins'])
					group = n['input_group']
	
					if(SIM_CYCLE_LIM == -1):
						SIM_CYCLES = 88888888
					else:
						SIM_CYCLES = SIM_CYCLE_LIM
					f.write(f'\tint trace_store_{net}[{units}*{group}][{num_inputs}][{SIM_CYCLES}];\n')
					f.write(f'\tint valid_updated_store_{net}[{units}][{num_inputs}][{SIM_CYCLES}];\n')
					f.write(f'\tint max_valid_updated_store_{net}[{num_inputs}][{SIM_CYCLES}];\n')





			for n in NET_DATA:
				net = n.lower()#["net"].lower()
				n = NET_DATA[n]	
				#These are global
				f.write(f'\tint {net} = 0;\n')
				f.write(f'\tint group_{net} = 0;\n')
				#These are local
				for jjj in range(len(n['input_bins'])):
					f.write(f'\tint {net}_{jjj} = 0;\n')
					f.write(f'\tint group_{net}_{jjj} = 0;\n')


	

			#3.6
			#body
			#outer loop
			START = {}
			DEPTH = {}
			#print(valid_loops)
			for v in valid_loops:

				START[v] = "0"
				DEPTH[v] = valid_loops[v]["LIM"]

			cnt = 0
			c = hardware_config
			for lp in loop_order:
				for v in valid_loops:
					if(lp == v and c[PRE+lp] != 0):
						f.write(f'''\tint prev_{v} = 0;\n''')

			for lp in loop_order:
				for v in valid_loops:
					if(lp == v and c[PRE+lp] != 0):
						start = START[lp]
						depth = DEPTH[lp]
						stride = valid_loops[v]["STRIDE"]

						
						f.write((1+cnt)*"\t"+f"for(int {lp} = {start}; {lp} < {start+'+'+depth}; \
						{lp} += {c[PRE+lp]}*{stride})"+"{\n")
						DEPTH[lp] = PRE+lp
						START[lp] = lp
						cnt += 1
		
			#self.outer_cnt = cnt
			#3.7
			#body
			#inner loop


		
			INNER_LOOPS = {}
			inner_cnt = 0
			INNER_GROUP_SIZE = 1	
			for v in valid_loops:
				if(PRE+v in inner_loops_skips):
					continue
				#variable = v[1:].upper() #TB, the B here
				variable = v
				lowv = variable.lower()
				lim = valid_loops[variable]["LIM"]
				stride = valid_loops[variable]["STRIDE"]
				INNER_LOOPS[variable] = cnt*"\t"+(inner_cnt)*"\t"+f'''for (int {lowv} = {variable}; {lowv} < std::min({variable} + {c[PRE+variable]}*{stride}, {lim}); {lowv}+={stride}){{\n'''
				inner_cnt += 1

				group = valid_loops[v]['GROUP']
	
				if(group == "INNER"):
					INNER_GROUP_SIZE *= c[PRE+variable]

			f.write((1+cnt)*"\t"+f"int INNER_GROUP_SIZE = {INNER_GROUP_SIZE};\n")
		
			print(INNER_LOOPS)	

			#3.8
			#interior core
			#dantian
			#(this part is the custom part that one should write, is functional too)
			CYCLE_LIMIT = SIM_CYCLE_LIM
			if(CYCLE_LIMIT == -1):
				pass
			else:
				if(debug):
					#f.write('std::cout<< N << "\t" << B << "\t" << X<< "\t" <<Y<< "\t" << KX << "\t"<< KY << "\t" << std::endl;')
					f.write('std::cout<< N << "\t" << "\t" << KX << "\t"<< KY << "\t" << std::endl;')
				
				f.write(f'''
{(1+cnt)*"	"}	if(sim_cycles >= {CYCLE_LIMIT}-1){{
{(1+cnt)*"	"}		continue;
{(1+cnt)*"	"}	}}
{(1+cnt)*"	"}	sim_cycles++;
''')
			#statistics at the cycle-level
			for n in NET_DATA:
				net = n.lower()#net = n["net"].lower()
				n = NET_DATA[n]	
				units = n['units']	
				num_inputs = len(n['input_bins'])
				f.write(f'''
{(1+cnt)*"	"}	int updated_{net}[{units}][{num_inputs}];
{(1+cnt)*"	"}	for (int jjj = 0; jjj < {num_inputs}; jjj++){{
{(1+cnt)*"	"}		for (int u = 0; u < {units}; u++){{
{(1+cnt)*"	"}			updated_{net}[u][jjj] = 0;
{(1+cnt)*"	"}		}}
{(1+cnt)*"	"}	}}
{(1+cnt)*"	"}	//core before outer group start
		''')
	
			f.write(f'{(1+cnt)*"	"}//hooks["core_before_outer_group_start"]')

		
			f.write(hooks['core_before_outer_group_start'])

			#if continuous_accumulate, this net will be not zero, but {net} = {net}
			for n in NET_DATA:
				net = n.lower()#net = n["net"].lower()
				n = NET_DATA[n]	
				group = n['input_group']
				#f.write(f"int accumulate_{net} = 0;\n")

				f.write(f'{(1+cnt)*"	"}	{net} = 0;\n')
				f.write(f'{(1+cnt)*"	"}	group_{net} = 0;\n')

				for jjj in range(len(n['input_bins'])):
					f.write(f'{(1+cnt)*"	"}{net}_{jjj} = 0;\n')
					f.write(f'{(1+cnt)*"	"}group_{net}_{jjj} = 0;\n')
					
				f.write(f'''
{(1+cnt)*"	"} for(int k = 0; k < {total_units}; k++){{
{(1+cnt)*"	"} for (int j = 0; j < {num_inputs}; j++){{
{(1+cnt)*"	"}	prev_{net}[k][j] = 0;
{(1+cnt)*"	"}	cur_{net}[k][j] = 0;	
{(1+cnt)*"	"}		}}
{(1+cnt)*"	"}   }}
''')	
			
			outer_loops = 0

			for lp in loop_order:
				for v in valid_loops:
					if(lp == v and c[PRE+lp] != 0):	
						#for v in valid_loops:
	
						#for v in valid_loops:
						if(PRE+v in inner_loops_skips):
							continue
	
						group = valid_loops[v]['GROUP']
						if(group != "INNER"):
							#print(v)
							#print(inner_tiles)
							#print(inner_tiles[v])
							#print(INNER_LOOPS[inner_tiles[v]])
							f.write(INNER_LOOPS[v])
							outer_loops += 1	

			f.write(f'{(1+cnt)*"	"}//core before inner group start\n')
			f.write(hooks['core_before_inner_group_start'])
		
			#todos, local and global accumulate
			for n in NET_DATA:
				net = n.lower()#net = n["net"].lower()
				n = NET_DATA[n]	
				units = n['units'] // n['input_group']	
				group = n['input_group']
				f.write(f'{(1+cnt)*"	"}int accumulate_{net}[{units}];\n')	
				f.write(f'{(1+cnt)*"	"}int prev_accumulate_{net}[{units}];\n')
				f.write(f'''
{(1+cnt)*"	"}	for (int idx = 0; idx < {units} ; idx++){{
{(1+cnt)*"	"}		accumulate_{net}[idx] = 0;	
{(1+cnt)*"	"}		prev_accumulate_{net}[idx] = 0;
{(1+cnt)*"	"}	}}
{(1+cnt)*"	"}	//sync the PEs, so that it is output based even if the inner is compressed due to sparsity or other reasons
{(1+cnt)*"	"}     {net} = group_{net}*{INNER_GROUP_SIZE};
''')	
				num_inputs = len(n['input_bins'])
				for jjj in range(num_inputs):
					f.write(f'{(1+cnt)*"	"}{net}_{jjj} = group_{net}_{jjj}*{INNER_GROUP_SIZE};\n')	

					
			inner_loops = 0
			for lp in loop_order:
				for v in valid_loops:
					if(lp == v and c[PRE+lp] != 0):	
						#for v in valid_loops:
						if(PRE + v in inner_loops_skips):
							continue
	
						group = valid_loops[v]['GROUP']
						if(group == "INNER"):
							f.write(INNER_LOOPS[v])
							inner_loops += 1
		
			f.write(f'{(1+cnt)*"	"}//core_after_inner_group_start')
	
			f.write(hooks['core_after_inner_group_start'])
		
			for d in DATA:
				name = d['name']
				size = d['size']
				indexing = d['indexing']
				if(debug):
					f.write('{(1+cnt)*"	"}std::cout << "data_recovered" << std::endl;')
				f.write(f'''
{(1+cnt)*"	"}int {name}_idx = {indexing};
{(1+cnt)*"	"}int {name}_data = {name}[{name}_idx];
''')
				
			f.write(hooks['core_after_data_fetch'])
					
			#update oggle bins and previous values
			f.write(core_cpp(NET_DATA, False, debug))

			#Inner Tile End
			for i in range(inner_loops):
				f.write(f'}}//end inner loop {i}\n')
			
			#Inner Tile End Hook
			f.write(hooks.get("inner_loop_finished", ""))

			#update Inner Tile End Core if is accumulated
			f.write(core_cpp(NET_DATA, True, debug))
			
			#Update any output metadata		
			for n in NET_DATA:
				net = n.lower()
				n = NET_DATA[n]

				units = n['units']
				accumulate = n.get('accumulate',False)
				accumulate_op = n.get('accumulate_op', "")
	
				accumulated_input = n.get('accumulated_input',False)
				num_inputs =len( n['input_bins'])
				prev_update = n.get('prev_update', '0')
				cur_update = n.get('cur_update', '0')
	
				output_update = n.get('output_update', '0')
				group = n['input_group']
	
				for m in n.get('output_metadata', {}):
					meta_update = n['output_metadata'][m]['update']
					
					if(accumulate):
						f.write(f'out_{m}_{net}[group_{net}][{meta_update}]++;')	
				if(accumulate):
					if(debug):
						f.write(f'{(1+cnt)*"	"}std::cout << "accumulated " << accumulate_{net}[group_{net}] << std::endl;\n')

			#(todos) in the general case, the group can be inserted at any layer	
			#Update After INner Group End Loop
			f.write(f'''
{(1+cnt)*"	"}group_{net} = (group_{net}+1);
			''')
			for jjj in range(len(n['input_bins'])):
				f.write(f'{(1+cnt)*"	"}group_{net}_{jjj}++;\n')
	
			#Hook Before Outer Loop ENd
			f.write("//hooks['core_after_inner_group_end']\n")
	
			f.write(hooks['core_after_inner_group_end'])
		
			#Outer Loop End
			for i in range(outer_loops):
				f.write(f'}}\n')

			#After Outer Loop End Save Trace
			if(need_trace):
				for n in NET_DATA:
					net = n.lower()
					n = NET_DATA[n]
					units = n['units']
					
					accumulate = n.get('accumulate',False)
					num_inputs =len( n['input_bins'])
					group = n['input_group']
					if(debug):	
						f.write(f'''
					std::cout << "trace starting" << sim_cycles <<std::endl;
					''')
					
					for jjj in range(num_inputs):#(int jjj = 0 ; jjj < {num_inputs}; jjj++)	
						for g in range(group): 
							for u in range(units):
								pass
								#f.write(f'std::cout << {net} << "\t" << prev_{net}[{u}][{jjj}] << std::endl;')
								#f.write(f'//goldenOutFile_{net}_{jjj} << prev_{net}[{u}][{jjj}]  << "\\t";\n');
								#f.write(f'goldenOutFile_{net}_{jjj} << "testing" << "\\t";\n');
				
								#small issue, the prev_{net} is updated inner loop, the outer, so the grouping should be in the inner indexing. But is flipped for teh store.
					f.write(f'''
	for (int jjj = 0; jjj < {num_inputs}; jjj++)
		for (int g = 0; g < {group}; g++)
			for(int u = 0; u < {units}; u++){{
trace_store_{net}[u+{units}*g][jjj][sim_cycles] = prev_{net}[g+{group}*u][jjj];

if({DEBUG}) std::cout << "DEBUG: trace_store_{net} \t"<<jjj<<"\t"<<g<<"\t"<<u<< "\t" << prev_{net}[g+{group}*u][jjj]<<"\\n";


}}
''')

					inner_unroll = n.get('input_time_unrolled', [1]*num_inputs)
					group = n['input_group']
					group_unroll = [group // inner_unroll[jjj] for jjj in range(num_inputs)]
					f.write(f'''int group_unroll_{net}[{num_inputs}];''')
					for jjj in range(num_inputs):
						f.write(f"group_unroll_{net}[{jjj}] = {group_unroll[jjj]};\n")

					f.write(f'''
		for (int jjj = 0; jjj < {num_inputs}; jjj++){{
		for (int u = 0; u < {units}; u++){{
	valid_updated_store_{net}[u][jjj][sim_cycles]=	(updated_{net}[u][jjj] + group_unroll_{net}[jjj]-1) / group_unroll_{net}[jjj];	

if({DEBUG}) std::cout << "DEBUG: valid_updated_store_{net} \t"<<valid_updated_store_{net}[u][jjj][sim_cycles]<<std::endl;

}}

		int mmm = 0;
		for (int u = 0; u < {units}; u++){{
			if(valid_updated_store_{net}[u][jjj][sim_cycles] >mmm)
			mmm =  valid_updated_store_{net}[u][jjj][sim_cycles];//=updated_{net}[u][jjj];
		}}
		max_valid_updated_store_{net}[jjj][sim_cycles] = mmm;

		}}
				''')
						

		
			#HOOK: After outer tile done	
			f.write(hooks['core_after_outer_group_end'])

			#Completed loop tail 
			for i in range(cnt):
				f.write("}\n")
				
			#SAVE RESULTS
			f.write(f'''
//done_sim:
std::cout << "// Saving Data" << std::endl;''')
			f.write(f'std::cout << "run simulation for " << sim_cycles << std::endl;\n')
			#f.write(f'''
			#	std::ofstream timeFile("{RUNTIME}");
			#	timeFile << sim_cycles << "\\n";
			#	timeFile.close();''')


			for n in NET_DATA:
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				units = n['units']
	
				group = n['input_group']
				if(debug):
					f.write(f'''
			std::cout <<"final latest_trace"<<std::endl;
			for (int s = 0; s < 5; s++)
			for(int u = 0; u < {units} ; u++)
				for (int jjj = 0; jjj < {num_inputs}; jjj++)
					for (int g =0; g < {group}; g++)
	std::cout<<u <<"\\t"<<jjj<<"\\t"<<g<<"\\t"<<	trace_store_{net}[u+{units}*g][jjj][s];
				
				''')
	


			for n in NET_DATA:
				net_orig = n
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				units = n['units']
	
				group = n['input_group']
				TOGGLING_FILE = n['TOGGLING_FILE']#'#root+"/"+name+f".{net}.trace"
				TRACE_FILE = n['TRACE_FILE']
				OUTPUT_TOGGLING_FILE = n['OUTPUT_TOGGLING_FILE']
				
				units = n['units']//group
				prec = n['input_bins']
				prec = 1
				for i in n['input_bins']:
					prec *= i


				output_prec = n.get('output_bins',8)
				


				#inputs now
				units = n['units']
				group = n['input_group']
				num_inputs =len( n['input_bins'])
	

			
				if(need_trace):
					f.write(f'//{units} {group}')
					f.write(f'std::cout << "saving input raw trace!" << std::endl;\n')
					f.write(f'int saved = 0;\n')
					
					if(debug):
						f.write(f'''
			std::cout <<"final latest_trace"<<std::endl;
			for (int s = 0; s < 5; s++)
			for(int u = 0; u < {units} ; u++)
				for (int jjj = 0; jjj < {num_inputs}; jjj++)
					for (int g =0; g < {group}; g++)
	std::cout<<"DEBUG\\t"<<u <<"\\t"<<jjj<<"\\t"<<g<<"\\t"<<	trace_store_{net}[u+{units}*g][jjj][s];
				
				''')
					inner_unroll = n.get('input_time_unrolled', [1]*num_inputs)
					unit_unroll = n.get("unit_time_unrolled", [1]*num_inputs)
					hold = n.get("input_hold_cycles", [1]*num_inputs)

					trace_merge_prec = n.get('trace_merge_prec', 8)
					trace_merge_units = n.get('trace_merge_units', 1) 						

					#for (int g = 0 ; g < {group}; g++){{
					#	for (int jjj = 0; jjj < {num_inputs}; jjj++){{

					casting_skip = 1
					casting_skip = n.get("units_select", 1)
	
					for sss in inner_loops_skips:
						casting_skip*= c[sss]

					#f.write(f"int casting_skip = {casting_skip};")
	
					for jjj in range(num_inputs):
						unrolled = inner_unroll[jjj]
						group_unrolled = group//unrolled

						#print(group_unrolled, group, unrolled)
						#exit()
						
						
						for g in range(group_unrolled):
							i = jjj + num_inputs*g
							trace_file_name = n.get('input_trace_name',['in']*num_inputs)[jjj]
							gen_trace_file = f"{TRACE_FILE}.{trace_file_name}_{jjj}_{g}"
							print(gen_trace_file)

	
							#OUTPUT_FILES[net_orig]["GEN_TRACE_FILES"].append(gen_trace_file)	
							f.write(f'''
				std::ofstream goldenOutFile_{net}_{i}("{gen_trace_file}");		
				saved = 0;
				for(int s = 0; s < sim_cycles; s++){{

					//Unit-level synced hold
					int HOLD = {hold[jjj]};
					for(int h = 0; h < HOLD; h++){{
						//std::cout << s << "\\t";
						int u = 0;
						int entry = 0;
						for (u = 0; u < {units}/{casting_skip} ; u++){{
							if({debug}){{
								//std::cout	<<trace_store_{net}[u+{units}*{g}][{jjj}][s] << "\\t"; 
								std::cout	<<s << "\\t"	<<trace_store_{net}[u+{units}*(({g} + h* {group//unrolled} ) %{group})][{jjj}][s] << "\\t"; 

							}}

							entry = (entry << {trace_merge_prec} ) | trace_store_{net}[u+{units}*(({g} + h*{group//unrolled}) % {group})][{jjj}][s] ;
				

							if((u+1) % {trace_merge_units}== 0  ){{

							goldenOutFile_{net}_{i}	<< entry << "\\t"; 

							entry = 0;
}} else {{
	//	entry = entry <<  {trace_merge_prec};
}}
	

	''')
		#Meaning is slowed down, input larger than output in time, i.e. parallel2serial
							if(unit_unroll[jjj] > 0):
				
								f.write(f'''	
						if((u+1) % ({(units)//unit_unroll[jjj]} / {casting_skip} ) == 0){{
							goldenOutFile_{net}_{i} << std::endl;
	}}''')
							else:
								f.write(f'''	
						if((saved+1) % ({units*-unit_unroll[jjj]} / {casting_skip} ) == 0){{
							goldenOutFile_{net}_{i} << std::endl;
	}}''')
	

	

							f.write(f'''					
saved++;

}} //end u loop



						//goldenOutFile_{net}_{i} << std::endl;
						if(u  == {units}/{casting_skip} ) {{
							//goldenOutFile_{net}_{i} << std::endl;
						}}


						if({debug}){{
							std::cout	<< std::endl;; 
						}}


					}}
	
		}}
			''')
						
							if(unit_unroll[jjj] < 0):
								
								f.write(f'''	
				
						while((saved) % ({units*-unit_unroll[jjj]}) != 0){{
							//std::cout << saved<<std::endl;
							if((saved) % {trace_merge_units}== 0  ){{
							goldenOutFile_{net}_{i} << "0\t";
							}}
							saved+= 1;//{trace_merge_units};
	}}''')
	
							f.write(f'''
	goldenOutFile_{net}_{i}.close();
	//std::cout << std::endl;
						''')



					"""
					for g in range(group):#terms = FC_TI for adder tree	
						for jjj in range(num_inputs):

							i = jjj + num_inputs*g
							f.write(f'std::ofstream goldenOutFile_{net}_{i}("{TRACE_FILE}_{i}");\n');	
							f.write(f'''
			for(int s = 0 ; s < sim_cycles; s++){{
	
				for(int u = 0; u < {units}; u++){{
			goldenOutFile_{net}_{i}	<<	trace_store_{net}[u+{units}*{g}][{jjj}][s] << "\\t"; 
			//std::cout	<<s << "\\t"	<<trace_store_{net}[{u}+{units}*{g}][{jjj}][s] << "\\t"; 

				}}
			goldenOutFile_{net}_{i} << std::endl;
			//std::cout << std::endl;
	
			}} ''')
						f.write(f'goldenOutFile_{net}_{i}.close();\n');	
					"""	



				for m in n['input_metadata']:
					
					f.write(f'std::cout << "saving input metadata toggles!" << std::endl;\n')
	

					f.write(f'std::ofstream ToggleOutFile_{m}_{net}("{TOGGLING_FILE}");\n');
	
					f.write(f'''
					//int {m}_{net}[{units}][{prec}];
					for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {prec}; j++) {{
					ToggleOutFile_{m}_{net}	<<	{m}_{net}[k][j] << "\\n" ;
					//if({m}_{net}[k][j] > 0)
					//std::cout << k << "\\t" <<j<<"\\t"	<<	{m}_{net}[k][j] << "\\n" ;
	
					}}''')

					f.write(f'ToggleOutFile_{m}_{net}.close();\n');
	



				"""
				for m in n['output_metadata']:
					f.write(f'std::cout << "saving output toggles!" << std::endl;\n')
					f.write(f'std::ofstream OutputToggleOutFile_{m}_{net}("{OUTPUT_TOGGLING_FILE}");\n');	
					f.write(f'''
						//int {m}_{net}[{units}][{prec}];
						for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {output_prec}; j++) {{
						OutputToggleOutFile_{m}_{net}	<<	out_{m}_{net}[k][j] << "\\n" ;
					if(out_{m}_{net}[k][j] > 0){{
					//std::cout <<"OUT\t" << k << "\\t" <<j<<"\\t"	<<	out_{m}_{net}[k][j] << "\\n" ;
					}}
	
					}}\n''')


					
					f.write(f'OutputToggleOutFile_{m}_{net}.close();\n')
				"""

	

			for d in DATA:
				name = d['name']
				size = d['size']
				indexing = d['indexing']
				f.write(f'''
					free({name});
					''')
	
			f.write(f'''return 0;
				}}''')
	


		#run it
		#if gen-trace true, but no run cpp, we can skip g++
		if(not run_it and need_trace):
			return OUTPUT_FILES
		if(not IS_LINUX):
			
			print(f"g++ -O2 {CPP_FILE} -o {orig_name}.exe") #make this as fast as possible please	
			
			os.system(f"g++ -O2 {CPP_FILE} -o {orig_name}.exe") #make this as fast as possible please	
			if(run_it):
				os.system(".\\{orig_name}.exe")
				#os.system("rm .\\{orig_name}.exe")
		else:
			print(f"g++ -O3 {CPP_FILE} -Wl,-rpath,/nfs/project/JayMok/power_experiments_xie/primitives -o {orig_name}.out")
	
			os.system(f"g++ -O3 {CPP_FILE} -Wl,-rpath,/nfs/project/JayMok/power_experiments_xie/primitives -o {orig_name}.out")
	
			if(run_it):	
				os.system(f"./{orig_name}.out")
				#os.system(f"rm ./{orig_name}.out")

	
		#post-processing
		'''
		if(run_it):
			for n in NET_DATA:
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				group = n['input_group']
				num_inputs =len( n['input_bins'])	
	
				split_inputs = n.get("split_inputs", 1)
				print(OUTPUT_FILES["GEN_TRACE_FILES"])
				#exit()
		'''	

		#OUTPUT_FILES["GEN_TRACE_FILES"] = GEN_TRACE_FILES

		#print(OUTPUT_FILES)
		return OUTPUT_FILES	



#general architecture
#Infer the PPA on a network
#1. Our Power Model w/ Toggle
#2. Baselines (Maestro, Accelergy, Aladdin, Interstellar)
#3. Ground Truth (scala + ptpx)
#Methodology:
#1. Generate trace and simulation output files
#2. Estimate the Power

#FLOW 1: PERF ARCH +GOLDEN+ ESTIMATE POWER+BASELINE
#1. ga = GenArch(haredware_configs)
#2. ga.gen_perf_trace(network_configs, SIM_CYCLES = 100) 
#3. ga.estimate_golden_pwr(nc)
#4. ga.estimate_our_pwr(nc)
#5. ga.estimate_b1_pwr(nc)
#6. ga.estimate_b2_pwr(nc) 

#FLOW 2: FOR DSE
#1. ga = GenArch(hardware_configs)
#2. ga.gen_perf_trace(network_configs, SIM_CYCLE = FULL)
#3. ga.estimate_our_pwr(network_configs)

#FLOW 3: LONG PERF ARCH, already run, changing updating our power model
#1. ga = GenArch(hardware_configs)
#2. ga.estimate_our_pwr(network_configs)
class GeneralUnit:
	#hc is a specific hardware
	#nc is a specific network layer
	def __init__(self, hc, work_folder = "generated/Architecture/"):
		self.hc = hc
	def get_primitive_statistics(self):
		self.MODULES = {
		}


	#estimate powers
	def analyze_results(self, traces, network_layer,mapping, SIM_PARAMS):
		total_results = []
		for blocks in traces:
			total_results.append( {})

			for module in blocks:
				POWER_GOLDEN_FILE = blocks[module]["POWER_GOLDEN_FILE"]	
				#OTHER BENCHMARKS
				gold = pd.read_csv(POWER_GOLDEN_FILE,  delimiter="\t")
				units = self.MODULES[module]['units']	
				skips = self.MODULES[module].get('cast_skips', [])	



				casting_skip = 1
				casting_skip = n.get("units_select", 1)
	
				for sss in skips:
					casting_skip*= self.hc[sss]

				unroll = self.MODULES[module].get('unit_time_unrolled', [1])
				
				unroll = max(unroll)
				merge = self.MODULES[module].get("trace_merge_units", 1)

				if(unroll > 0):
					units = (((units) // casting_skip) // merge) // unroll
				else:
					units = (((units) // casting_skip) // merge)* -unroll

				assert(units > 0)

				rel = gold.tail(n=units)['Total_Pwr']
				at_golden_pwr = np.sum(rel)
				res = {"unit_pwrs": rel, "total_pwrs": np.sum(rel), "avg_pwrs": np.sum(rel)/len(rel)}
				#print(res)
				total_results[-1][module] = res
				
				#benchmark other results
	

		print(total_results)
		gold_head = []
		gold_tail = []
		#print("DEBUG")
		for t in total_results:
			for k in t:
				#print ("DEBUG ",k, t[k])
				gold_head.append("golden_"+k) 
				gold_tail.append(t[k]['total_pwrs'])
		print(gold_tail)
		
		gold_head.append("golden_total")
		gold_tail.append(sum(gold_tail))


		head = "\t".join(gold_head)
		tail = "\t".join([str(s) for s in gold_tail])
		#head = "\t".join([k+"_golden" for t in total_results  for k in t[total_results]  ])
		#tail = "\t".join([total_results[t][k]['total_pwrs'] for t in total_results   for k in t[total_results]  ])		
		print(head)
		print(tail)
	
		root = SIM_PARAMS.get("root", "generated/Architecture/GeneralUnit")
		root = "/".join(root.split("/")[0:-1])
		SAVE_RESULTS = SIM_PARAMS.get("SAVE_RESULTS", "generated/Architecture/GeneralUnit")		
		print(root+"/"+SAVE_RESULTS)
		with open(root+"/"+SAVE_RESULTS+".head.txt", "a") as f:
			f.write(head + "\n")		

		with open(root+"/"+SAVE_RESULTS+".tail.txt", "a") as f:
			f.write(tail + "\n")		
	
				
		#exit()
		return total_results					


		
	
	def estimate_golden_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		print(traces)
		
		total_results = []
		for blocks in traces:
			total_results.append( {})

			for module in blocks:
				print(module)
				print(blocks[module].keys())
				print(self.MODULES[module].keys())
				print(self.MODULES[module])		
				print(self.MODULES[module]['config'].keys())
				print(self.MODULES[module].keys())
					
				POWER_GOLDEN_FILE = blocks[module]["POWER_GOLDEN_FILE"]	
				if(os.path.exists(POWER_GOLDEN_FILE) and  SIM_PARAMS['SKIP_IF_EXISTING_GOLDEN']):
					print("SKIP " + POWER_GOLDEN_FILE)
					continue
		
				CONFIG = dict(self.hc)
				CONFIG.update({
						"EDAVerification": True,
						"fanout_load": 0.0,
						"OutputPowerFile": blocks[module]["POWER_GOLDEN_FILE"],
						"CustomMap": self.MODULES[module]['config'].get("CustomMap", {}),
				})
				CONFIG.update(self.MODULES[module]['config'])
					
				JSON_FILE = blocks[module]["JSON_FILE"]

				with open(JSON_FILE, "w") as json_file:
					json.dump(CONFIG, json_file, indent=4)  # indent 用于格式化输出		
					TRACE_FILE = blocks[module]["TRACE_FILE"]
					input_bins = self.MODULES[module]['input_bins']
					group = self.MODULES[module]['input_group']

					TRACE_FILES = " ".join(blocks[module]["GEN_TRACE_FILES"]) #" ".join([TRACE_FILE+"_"+str(i) for i in range(len(input_bins)*group)])
					print(blocks[module])
					print("TRACE",len(TRACE_FILES.split(" ")))
					#input()
					#exit()
					print("run sbt")

				primitive = self.MODULES[module]['config']['primitive']

				if(SIM_PARAMS["RUN_GOLDEN_SBT"]):
					print(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
					os.system(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
				#os.system(f'{SBT} "test:runMain adders.AdderNSpecFromFile {PE_TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
			
					gold = pd.read_csv(POWER_GOLDEN_FILE,  delimiter="\t")
					#get relevant rows
					units = self.MODULES[module]['units']	
					rel = gold.tail(n=units)['Total_Pwr']
					print("GOLDEN POWER")
					print(rel, np.sum(rel))
					#print("GOLDEN ADDER TREE", np.sum(rel))
					at_golden_pwr = np.sum(rel)
					res = {"unit_pwrs": rel, "total_pwrs": np.sum(rel), "avg_pwrs": np.sum(rel)/len(rel)}
					total_results[-1][module] = res

		print(total_results)
		return total_results					

				


	def estimate_our_pwr(self, traces, network_layer,mapping, SIM_PARAMS):

		return {}


	def estimate_our_pwr_v1(self, traces, network_layer,mapping, SIM_PARAMS):
		all_powers = {}
		for blocks in traces:
			for module in blocks:	
				primitive = self.MODULES[module]['config']['primitive']
			
				n = self.MODULES[module]	
				num_inputs = n['input_group']*len(n['input_bins'])
	

				primitive_name = primitive.split(".")[1]

				#import importlib
				#module_name = f"power_models.{primitive_name}Primitive"
				
				#prim = importlib.import_module(module_name)
				#PRIM = getattr(prim, f"{primitive_name}Primitive")

				#from power_models.AdderNPrimitive import AdderNPrimitive
				#prim = PRIM()

				TRACE_FILE = blocks[module]["TRACE_FILE"]
				input_bins = self.MODULES[module]['input_bins']

				TRACE_FILES = " ".join([TRACE_FILE+"_"+str(i) for i in range(len(input_bins))])
				TRACE_FILES = blocks[module]["GEN_TRACE_FILES"] #" ".join([TRACE_FILE+"_"+str(i) for i in range(len(input_bins)*group)])


				CONFIG = self.hc
				CONFIG.update({
						"EDAVerification": True,
						"fanout_load": 0.0,
						"OutputPowerFile": blocks[module]["POWER_GOLDEN_FILE"]
				})
				CONFIG.update(self.MODULES[module]['config'])
	

				if(primitive_name == "Multiplier2"):
					prim = Multiplier2Primitive()
				
				elif(primitive_name == "MaxN"):
					prim = MaxNPrimitive()
				elif(primitive_name == "AdderN"):
					prim = AdderNPrimitive()
				#elif(primitive_name == "ConstantMultiplier"):
				#	prim = ConstantMultiplier()
				elif(primitive_name == "SRAMS"):
					prim = SRAMSPrimitive()		
				elif(primitive_name == "Deserializer"):#caster
					prim = DeserializerPrimitive()		
	
	
				elif(primitive_name == "MuxN"):
					prim = MuxNPrimitive()		
	
				elif(primitive_name == "Crossbar"):
					prim = CrossbarPrimitive()		
				else:
					print("primitive ", primitive_name, "no model")

				
				g,h,d = prim.get_features(primitive_name, out_features = ['Total_Pwr'])
	
				input_data = {}
				for gg in h+g:
					if("inv" in gg):
						ggg = gg.split("_")[1]	
						input_data[gg] = [1.0/CONFIG[ggg]]
						input_data[ggg] = [CONFIG[ggg]]


					else:
						input_data[gg] = [CONFIG[gg]]
	
							
				
				
				r = 5
				'''
				input_data = {
					"CLOCK": [CONFIG["CLOCK"]],
					"cap_load": [CONFIG["cap_load"]],
					"prec_in" : [prec],
					"prec_sum": [prec],
					"terms": [self.FC_TI]
				}
				'''	
					
			
				input_data = trace_file(num=num_inputs, TRACE_FILE=TRACE_FILES, input_data=input_data, r = r)

				if 'terms' not in input_data:
					input_data['terms'] = [num_inputs]

				#(TODOS), for crossbar, because output is many, we don't need to have a multi-crossbar
				#mode, therefore split the input_data in_0... into multiple segments and loopo
				
				print(input_data)
				res = prim.execute_testing(
					name = primitive_name,
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = input_data
				)
				#print(res)
				at_estimate_pwr = res['Total_Pwr']['res']#['res_sum']
				#compress
				unit_pwrs = []
				#print(at_estimate_pwr.keys()	)
				sum_pwrs = []	
				for units in res['Total_Pwr']['res']:
					ress = units
					#print(units)
					#print(res[0])
					avg_pwr = sum(ress[0])/len(ress[0])		
					sum_pwr = sum(ress[0])
					unit_pwrs.append(avg_pwr)
					sum_pwrs.append(sum_pwr)
				total_pwr = sum(unit_pwrs)
				print(sum_pwrs)
				print(unit_pwrs, total_pwr)	
				#print(at_estimate_pwr)	
				our = {
					"total_pwr": total_pwr,
					"unit_pwr": unit_pwrs,
					#"res": res["Total_Pwr"]['res']	
				}
				import json
				POWER_GOLDEN_FILE = blocks[module]["POWER_GOLDEN_FILE"]	
	
				with open(POWER_GOLDEN_FILE+".our_model", "w") as f:
				    json.dump(our, f, indent=4)  # ‌:ml-citation{ref="1,3" data="citationList"}
				#with open("compact.json", "w") as f:
				#    json.dump(data, f, separators=(",", ":"))  # ‌:ml-citation{ref="3" data="citationList"}

	
	

				CHECK_AGAINST_GOLDEN = 1
				if(CHECK_AGAINST_GOLDEN):
					POWER_GOLDEN_FILE = blocks[module]["POWER_GOLDEN_FILE"]	
	
					gold = pd.read_csv(POWER_GOLDEN_FILE,  delimiter="\t")
					#get relevant rows
					units = self.MODULES[module]['units']	
					skips = self.MODULES[module].get('cast_skips', [])	



					casting_skip = 1
					casting_skip = n.get("units_select", 1)
	
					for sss in skips:
						casting_skip*= self.hc[sss]

					unroll = self.MODULES[module].get('unit_time_unrolled', [1])
				
					unroll = max(unroll)
					merge = self.MODULES[module].get("trace_merge_units", 1)

					if(unroll > 0):
						units = (((units) // casting_skip) // merge) // unroll
					else:
						units = (((units) // casting_skip) // merge)* -unroll

					assert(units > 0)

					#units = self.MODULES[module]['units']	
					rel = gold.tail(n=units)['Total_Pwr']
					print("GOLDEN POWER")
					print(rel, np.sum(rel))
					#print("GOLDEN ADDER TREE", np.sum(rel))
					at_golden_pwr = np.sum(rel)
					res = {"unit_pwrs": rel, "total_pwrs": np.sum(rel), "avg_pwrs": np.sum(rel)/len(rel)}
					print("GOLDEN", res)
					input("OK CHECK AGAINST GOLDEN?")					



				return at_estimate_pwr


	def estimate_b1_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		return {}

	def estimate_b2_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		return {}
	

	#def gen_perf_trace(self, SIM_CYCLES = 8888888888888888):
	#	return {}	
	def infer(self, params):
		return {}
	def gen_perf_trace(self,network_layer,mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):
		work_folder = SIM_PARAMS.get("root", "generated/Architecture/GeneralUnit")
		print(work_folder)
		#if(not os.path.exists(work_folder)):
		#	os.mkdir(work_folder)	
	
		path_parts = work_folder.split('/')
	
		current_path = ""
		for part in path_parts:
		    current_path = os.path.join(current_path, part) if current_path else part
		    if not os.path.exists(current_path):
		        os.mkdir(current_path)
		        print(f"目录已创建: {current_path}")
		    else:
		        print(f"目录已存在: {current_path}")


		'''
		print(SIM_PARAMS)
		work_folder = SIM_PARAMS.get("root", "generated/Architecture/GeneralUnit")
		import os
		path = work_folder #+ "/" + dict_to_str(self.hc)
		#os.makedirs(path, exist_ok=True)
		# 分割路径为每一层
		path ="/".join( work_folder.split('/')[0:3])
		print(path)
		path_parts = path.split('/')
		
		# 逐层检查并创建目录
		current_path = ""
		for part in path_parts:
		    current_path = os.path.join(current_path, part) if current_path else part
		    if not os.path.exists(current_path):
		        os.mkdir(current_path)
		        print(f"目录已创建: {current_path}")
		    else:
		        print(f"目录已存在: {current_path}")

		
		designs = {}
		if os.path.exists(path+"/designs.txt"):
		
			with open(path+"/designs.txt", "r") as f:
				for l in f.readlines():
					a = l.split("\t")
					if(len(a) == 1):
						continue
					j = a[0]
					y = a[1]
					designs[j] = y

		import hashlib
		def string_to_hash(long_string, algorithm="sha256"):
    			hash_func = hashlib.new(algorithm)
    			hash_func.update(long_string.encode('utf-8'))
	    		return hash_func.hexdigest()

		long_string = work_folder.split('/')[-1]
		#print("SHA256:", string_to_hash(long_string)) 
		gua = string_to_hash(long_string)

		designs[gua] = work_folder

		with open(path+"/designs.txt", "w") as f:
			for d in designs:
				f.write(d + "\t"+designs[d]+"\n")	


		path = path +"/"+ gua
		if(not os.path.exists(path)):
			os.mkdir(path)
		print(path)
		print(gua)
		#exit()


		self.root = path
		SIM_PARAMS['root'] = self.root
		print("here")
		'''

	
		return {}	


class GeneralConvUnit(GeneralUnit):
	def gen_perf_trace(self,network_layer,mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):
		super().gen_perf_trace(network_layer, mapping, SIM_PARAMS)

		layer = network_layer['layer']
		input_data = network_layer['input_data']
		output_data = network_layer['input_data']
	
		print(dir(layer))
	
		params = {
		"SIM_PARAMS": SIM_PARAMS,
		"in_channels": layer._in_channels,
					"out_channels": layer._out_channels,
					"kernel_size": layer._kernel_size,
					"stride": layer._stride,
					"padding": layer._padding,
					"input_data": input_data,
					"weight": layer.weight,
					"out_data": output_data,
				}
		print(params)
		results = self.infer(params)
		return results	

class GeneralMaxPoolUnit(GeneralUnit):
	def gen_perf_trace(self,network_layer, mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):	
		super().gen_perf_trace(network_layer, mapping, SIM_PARAMS)


		layer = network_layer['layer']
		input_data = network_layer['input_data']
		output_data = network_layer['input_data']
		#print(layer)	
		#print(dir(layer))
	
		params = {
					"kernel_size": layer.ksize,
					"stride": layer.stride,
					"padding": layer.padding,
					"input_data": input_data,
					"out_data": output_data,
					"SIM_PARAMS": SIM_PARAMS,
				}
		
		results = self.infer(params)
	
		return results


class GeneralLinearUnit(GeneralUnit):
	def gen_perf_trace(self,network_layer,mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):

		super().gen_perf_trace(network_layer, mapping, SIM_PARAMS)

		layer = network_layer['layer']
		input_data = network_layer['input_data']
		output_data = network_layer['input_data']
	
		
		params = {
			"in_features": layer.weight.shape[1],
			"out_features": layer.weight.shape[0],
			"input_data": input_data,
			"weight": layer.weight,
			"out_data": output_data,
			"SIM_PARAMS": SIM_PARAMS
		}
		results = self.infer(params)		
		return results

###################################################

#CONV converted to FC, has POOL, RELU, Simple Activations, Element-wise addition
#can do AlexNet, Resnet
#Other types of Conv?

class SystolicConv(GeneralConvUnit):
	pass

class WinogradConv(GeneralConvUnit):
	pass

class SparseConv(GeneralConvUnit):
	pass


class DirectConv(GeneralConvUnit):
	def infer(self, params):
		print(params)
		return {}
class SparseLinear(GeneralLinearUnit):
	def infer(self, params):
		print(params)
		return {}
#################################################


#given a network, mapping, hardware
#output the trace and ppa
class GeneralArch:
	def __init__(self, hc, nc, mapping):
		self.hc = hc
		self.nc = nc
		self.mapping = mapping
	
	def get_hardware_statistics(self):
		return {}

	def gen_perf_trace_full(self,intermediate_outputs,SIM_CYCLES):
		self.SIM_CYCLES = SIM_CYCLES
		for layer_name, layer, input_data, out_data in intermediate_outputs:
			if isinstance(layer, nn.Conv2D):
				params = {
					"in_channels": layer._in_channels,
					"out_channels": layer._out_channels,
					"kernel_size": layer._kernel_size,
					"stride": layer._stride,
					"padding": layer._padding,
					"input_data": input_data,
					"weight": layer.weight,
					"out_data": out_data,
				}
				results = self.infer_conv(params)
			elif isinstance(layer, nn.Linear):
				params = {
					"in_features": layer.weight.shape[1],
					"out_features": layer.weight.shape[0],
					"input_data": input_data,
					"weight": layer.weight,
					"out_data": out_data
				}
				results = self.infer_fc(params)	
			elif isinstance(layer, nn.MaxPool2D):
				print(input_data, out_data)
				print(layer)
				print("todos - maxpool")
				#results = self.infer_maxpool(params)	
			elif isinstance(layer, nn.AvgPool2D):
				print(input_data, out_data)
				print(layer)
				print("todos - maxpool")	
				#results = self.infer_avgpool(params)
			elif isinstance(layer, nn.ReLU) or isinstance(layer, nn.BatchNorm2D) or isinstance(layer, nn.Sigmoid):
				print("do ReLU")
				#results = self.infer_activations(params)		

			#self.save_results(layer_name,results)
			print(f"arch sim of Layer: {layer_name}")



if __name__ == "__main__":

	hc = {
		"conv1": {
			
		},
	}
	ga = SingleFlowArch(hc)
	#FLOW 1: PERF ARCH +GOLDEN+ ESTIMATE POWER+BASELINE
	#simple 
	#for layer_name, layer, input_data, out_data in intermediate_outputs:
	network_configs = [
		["cnn1", nn.Conv2D(
 		   in_channels=3,  # Input channels, for example, RGB images have 3 channels
		    out_channels=16,  # Output channels
		    kernel_size=3,  # Convolutional kernel size of 3x3
		    stride=1,  # Stride of 1
		    padding=1  # Padding of 1
		  ), np.random((8, 3, 16, 16)), np.random((16, 3, 3, 3)) , np.random((8, 16, 14, 14))],
	]
	#mapping between network_configs layer and a dataflow
	mapping = {
		"cnn1": "conv1",
	}
	nc = network_configs
	ga.gen_perf_trace(hc, nc, mapping, SIM_CYCLES = 100) 
	ga.estimate_golden_pwr(nc)
	ga.estimate_our_pwr(nc)
	ga.estimate_b1_pwr(nc)
	ga.estimate_b2_pwr(nc)

#FLOW 2: FOR DSE
#1. ga = GenArch(hardware_configs)
#2. ga.gen_perf_trace(network_configs, SIM_CYCLE = FULL)
#3. ga.estimate_our_pwr(network_configs)

#FLOW 3: LONG PERF ARCH, already run, changing updating our power model
#1. ga = GenArch(hardware_configs)
#2. ga.estimate_our_pwr(network_configs)


