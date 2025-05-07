from ArchTemplates import GeneralMaxPoolUnit, GeneralLinearUnit, generate_cpp, dict_to_str

import numpy as np
import paddle.nn as nn
import pandas as pd

from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive
from power_models.MaxNPrimitive import MaxNPrimitive
	
	
class MaxPoolDirect(GeneralMaxPoolUnit):

	def get_primitive_statistics(self):	
		self.MODULES =  {
			#Max accumulator
			"MAX_ACCUM": {
				"units": self.hc["TB"]*self.hc["TX"]*self.hc["TY"]*self.hc["TN"],
				#input
				"input_metadata": {
				"toggle": {
					"update": "__builtin_popcount(accumulate_max_tree_accum[max_accum]^prev_accumulate_max_accum[max_accum])",
			}},
				"input_bins": [ self.hc["MAXACCUM_PREC"]],
				'input_group': 1,
				
				#new
				"accumulated_input": True,
				"globally_accumulate_output": True,
				"globally_accumulate_reset_trigger": [],

				#	
				'cur_update': ['accumulate_max_tree_accum[max_accum]'], #value	
				'prev_update': [ 'std::max(accumulate_max_tree_accum[max_accum], prev_max_accum[max_accum][0] )' ]  ,#['weights_data', 'inputs_data'],


				#output
				"output_metadata": {
				},
				"output_bins": self.hc["MAXACCUM_PREC"] ,

				'reset_trigger': [],

				#meaning output is accumulated
				'accumulate': False,#meaning the output is accumulated
				'accumulate_op': '',
				'hooks': {
					"core_before_outer_group_start": "",
					"core_before_inner_group_start": "",
					"core_after_inner_group_start":"",
					"core_after_data_fetch":"",
					"core_after_inner_group_end":"",
					"core_after_outer_group_end": ""
				},
				"config": {
					"primitive": "maxmin.MaxAccumulator",
					"MaxType": self.hc["MAXACCUM_TYPE"],
					"prec":self.hc["MAXACCUM_PREC"],
					"out_prec":self.hc["MAXACCUM_PREC"] ,
					"terms": 1,
				}



			},

			#Max tree
			"MAX_TREE_ACCUM": {
				"units": self.hc["TB"]*self.hc["TX"]*self.hc["TY"]*self.hc['TN'],
				"input_metadata": {
					"toggle": {
						"update": "__builtin_popcount(cur_max_tree_accum[max_tree_accum][jjj]^prev_max_tree_accum[max_tree_accum][jjj])",
				}},
				"input_bins": [ self.hc["TKX"]*self.hc["TKY"]*self.hc["MAXTREE_PREC"]],
				'input_group': self.hc["TKX"]*self.hc["TKY"],


				#how input is tracked
				'cur_update': ['inputs_data'], #value
	
				'prev_update': [ 'inputs_data' ]  ,#['weights_data', 'inputs_data'],



				"output_metadata": {
					"toggle": {
						"update": "__builtin_popcount(accumulate_max_tree_accum[group_max_tree_accum]^prev_accumulate_max_tree_accum[group_max_tree_accum])"

					}
				},
				"output_bins": self.hc["MAXACCUM_PREC"] ,

				'reset_trigger': [],

				'accumulate': True,#meaning the output is accumulated
				'accumulate_op': 'std::max(accumulate_max_tree_accum[group_max_tree_accum], inputs_data)',
				'hooks': {
					"core_before_outer_group_start": "",
					"core_before_inner_group_start": "",
					"core_after_inner_group_start":"",
					"core_after_data_fetch":"",
					"core_after_inner_group_end":"",
					"core_after_outer_group_end": ""
				},
				"config": {
					"primitive": "maxmin.MaxN",
					"MaxType": self.hc["MAXTREE_TYPE"],
					"prec":self.hc["MAXTREE_PREC"],
					"out_prec":self.hc["MAXACCUM_PREC"] ,
					"terms": self.hc["TKX"]*self.hc["TKY"]
				}
			},

		}
		
	def infer_tree_accum(self,params):
		#any parameters we want to copy into the cpp
		PARAMETERS = params['params']
		#data we want to copy to the cpp
		DATA = [
			params['inputs_obj'],
		]
		#nets / hardware modules we want to track the toggling and features of 
		NET_DATA = {
			"MAX_TREE_ACCUM": self.MODULES["MAX_TREE_ACCUM"],
			"MAX_ACCUM": self.MODULES["MAX_ACCUM"]
		}	
		#loop orders and such
		LOOP_ORDER = self.hc["LOOP_ORDER"]
		#variable definitions
		LOOP_VAR_DEFINITIONS = self.LOOP_VAR_DEFINITIONS			
		hooks = self.MODULES["MAX_TREE_ACCUM"]["hooks"]
		#generate the c++ file
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]

		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] )

		print(output_files)
		return output_files
	
	def infer_buffers(self,params): 
		return {}	


	def prepare_data(self, params):
		input_data = params['input_data']

		#0. Prepare data
		BAT, OUT, INPUT_X, INPUT_Y = input_data.shape
		initial_shape = input_data.shape
		KERNEL = params["kernel_size"]
		PADDING = params["padding"]
		
		input_data = ((input_data*256*256) %self.hc["ACT_PREC"]).astype(np.int32)
		
		#Randomize weights and inputs (TODOS)
		Randomize = params["SIM_PARAMS"]["Randomize"]
		Act_Sparsity = params["SIM_PARAMS"]["Act_Sparsity"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]



		if(params["SIM_PARAMS"]['Randomize']):
			n = OUT*BAT*INPUT_X*INPUT_Y
			k = int(n*Act_Sparsity)
			rand_act = np.random.randint(0, 1<<self.hc["ACT_PREC"], size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_act[zero_indices] = 0
			
			input_data = rand_act.reshape(initial_shape)
		
		i_file = root+"/"+name+".input.txt"
		if(params['SIM_PARAMS']['save_np']):
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))	
			np.savetxt(i_file, input_data, fmt='%d', delimiter='\n')
		print(input_data)


		self.LOOP_VAR_DEFINITIONS = {
			"B": {
				"LIM": "BAT",
				"STRIDE": 1,
				"GROUP": "OUTER"
			},
			"N": {
				"LIM": "OUT",
				"STRIDE": 1,
				"GROUP": "OUTER", #meaning can be collected together in the sum
			},
			"X": {
				"LIM": "INPUT_X - KERNEL_X+1",
				"STRIDE": params['stride'],
				"GROUP": "OUTER", #meaning can be collected together in the sum
			},
			"Y": {
				"LIM": "INPUT_Y - KERNEL_Y+1",
				"STRIDE": params['stride'],
				"GROUP": "OUTER", #meaning can be collected together in the sum
			},
	
			"KX": {
				"LIM": "KERNEL_X",
				"STRIDE": 1,
				"GROUP": "INNER", #meaning can be collected together in the sum
			},
			"KY": {
				"LIM": "KERNEL_Y",
				"STRIDE": 1,
				"GROUP": "INNER", #meaning can be collected together in the sum
			},
		}


		return {
			"i_file": i_file,
			"quant_inputs": input_data,
			"params":{
				"OUT": OUT,
				"BAT": BAT,	
				"KERNEL_X": KERNEL,
				"KERNEL_Y": KERNEL,
				"INPUT_X": INPUT_X,
				"INPUT_Y": INPUT_Y,
			},
			"inputs_obj":
				{
				"name": "inputs",
				"file": i_file,
				"size": len(input_data.reshape((-1))),
				"indexing": "b*INPUT_Y*INPUT_X*OUT + n*INPUT_Y*INPUT_X + (kx+x)*INPUT_Y + (ky+y)"	
			},
	


		}
		
	def infer(self, params):
		self.get_primitive_statistics()
		print(params)	
		p = params
		p.update(self.prepare_data(p))

		results = []
		if(p.get("RUN_TREE_ACCUM",1)):
			results.append(self.infer_tree_accum(p))
		if(p.get("RUN_BUFFERS",1)):
			results.append(self.infer_buffers(p))
		return results


if __name__ == "__main__":
		

	hardware_config = {
	"ACT_PREC": 16,

	"TB": 2,
	"TN": 2,
	"TX": 1,
	"TY": 1,
	"TKX": 2,
	"TKY": 2,
	"LOOP_ORDER": ["B", "N", "X", "Y", "KX", "KY"],

	"MAXTREE_TYPE": "SimpleMax",
	"MAXTREE_PREC": 16,	

	"MAXACCUM_TYPE": "BitSerial",
	"MAXACCUM_PREC": 16,

	"SRAM_SIZE": [8, 64],
	"SRAM_TYPE": "Reg",
	"L1_WEI_LEN" : 512,
	"L1_ACT_LEN" : 64,
	"L2_LEN" : 512,
	"DRAM_LEN": 512,
	
	"CLOCK": 1,
	"cap_load":0.1,
	"tech":"tsmc40",

	}
	network_layer = {
	"layer_name": "MaxPool1",
	"layer": nn.MaxPool2D(kernel_size=4, stride=1), 
	"input_data": np.random.random((2,8, 60, 60)),
	"output_data": np.random.random((2,8, 55,55)),
	}
	mapping = {
		"MaxPool1": "df1",
	}

	design = dict_to_str(hardware_config)

	SIM_PARAMS = {
	"name": network_layer['layer_name'],
	"root": f"generated/Architecture/MaxPoolDirect/{design}",
	"SIM_CYCLES": 100,
	"Randomize": 1,
	"Act_Sparsity": 0.1,	
	'save_np':True,#False,# True,

	#0: Baseline compare against golden
	#generate trace and cpp 
	#use specified sim-cycles

	#1: inference time
	#no trace, run_cpp, simcycles is -1

	#2: Debug-mode
	#Assume trace generated
	#only fine-tune the model powers
	'MODE': 3,
	"RUN_GOLDEN_SBT": 1,
	
	#'GEN_TRACE':True,
	#'RUN_CPP': True
}
	SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS['Act_Sparsity'])

	if(SIM_PARAMS['MODE'] == 0):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True	
	elif(SIM_PARAMS['MODE'] == 1):
		SIM_PARAMS['GEN_TRACE'] = False
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True	
	elif(SIM_PARAMS['MODE'] == 2):	
		SIM_PARAMS['GEN_TRACE'] = False
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
		SIM_PARAMS['RUN_GOLDEN_SBT'] = False	
	elif(SIM_PARAMS['MODE'] == 3):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = True
		SIM_PARAMS['RUN_GOLDEN_SBT'] = False	


	#FLOW 1. compare against baselines and 
	ld =  MaxPoolDirect(hardware_config)
	traces = ld.gen_perf_trace(network_layer,mapping, SIM_PARAMS) 
	#print("HERE")
	#print(traces)
	ld.estimate_golden_pwr(traces, network_layer,mapping, SIM_PARAMS)
	ld.estimate_our_pwr_v1(traces,network_layer,mapping, SIM_PARAMS)	
	ld.estimate_our_pwr(traces,network_layer,mapping, SIM_PARAMS)
	ld.estimate_b1_pwr(traces,network_layer, mapping,SIM_PARAMS)#maestro
	ld.estimate_b2_pwr(traces, network_layer,mapping,SIM_PARAMS)#accelergy 
	ld.estimate_b3_pwr(traces, network_layer,mapping,SIM_PARAMS)#others?


