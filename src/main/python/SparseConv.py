from ArchTemplates import GeneralConvUnit, GeneralLinearUnit, generate_cpp, dict_to_str, filter_loop_order


import numpy as np
import paddle.nn as nn
import paddle
import pandas as pd

from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive

class SparseConv(GeneralConvUnit):
	def get_primitive_statistics(self):				

		#super.get_primitive_statistics()


		if(self.hc["MULT_SIDE"] == "weight"):
			MULTIPLIER_bins = ['weights_data', 'inputs_data']		
			MULT_prec1 = self.hc['WEI_PREC']
			MULT_prec2 = self.hc["ACT_PREC"]	
		else:
			MULTIPLIER_bins = ['weights_data', 'inputs_data'][::-1]
			MULT_prec1 = self.hc['ACT_PREC']
			MULT_prec2 = self.hc["WEI_PREC"]	
		

		SPARSE_RATIO = self.hc["SPARSE_RATIO"]
		SPARSE_SIDE = self.hc["SPARSE_SIDE"]
		OUTPUT_SPARSITY = self.hc["OUTPUT_COMPRESSION"]
		#WEI_ZERO_MAP_EN = self.hc["ZERO_MAP_EN"]		
		#ACT_ZERO_MAP_EN = self.hc["ZERO_MAP_EN"]		
		INPUT_COMPRESSION = self.hc["INPUT_COMPRESSION"]
		WEIGHT_COMPRESSION = self.hc["WEIGHT_COMPRESSION"]
		OUTPUT_COMPRESSION = self.hc["OUTPUT_COMPRESSION"]
	

		if("weights" in SPARSE_SIDE ):
			in_condition = "weights_data != 0"		
		elif("inputs" in SPARSE_SIDE ):
			in_condition = "inputs_data != 0"
		elif("both" in SPARSE_SIDE):
			in_condition = "inputs_data != 0 && weights_data != 0"
	

		if(OUTPUT_COMPRESSION == "zero_map"):
			out_condition = "outputs_data != 0"
		else:
			out_condition = ""	
		
		if(INPUT_COMPRESSION == "zero_map"):
			out_condition = "inputs_data != 0"
		else:
			out_condition = ""	
	
		if(WEIGHT_COMPRESSION == "zero_map"):
			out_condition = "weights_data != 0"
		else:
			out_condition = ""	
	
		L1_WEI_BUF_BIT_LEN = (self.hc["TI"]*self.hc["TN"]*self.hc["TKX"]*self.hc["TKY"]*self.hc["WEI_PREC"])//self.hc["INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO"]
		L1_WEI_BUF_UNITS = L1_WEI_BUF_BIT_LEN // self.hc["L1_WEI_SRAM_SIZE"][0]




		#MODULES characterizes a NET in the netlist, can be a component
		#or can be just a NET
		self.MODULES =  {
			#Select NonZero Weights	
			"L1_WEI_BUFFER_READ": {
				"units": L1_WEI_BUF_UNITS,
				"input_metadata": {"bits": {
					"update": f"__builtin_popcount(weights_data) "
				}},
				"input_bins": [self.hc["WEI_PREC"]],	
				'cur_update': ['weights_data'],
				'prev_update': ['weights_data'],
				'input_group': 1,
				"output_metadata": { },
				"output_bins": self.hc["WEI_PREC"],
				"output_update": 'weights_data',
				"output_condition": '',
				"accumulated_input": False,
				'reset_trigger': [],
				'accumulate': False,
				'accumulate_op': '',
				"config": {
					"primitive": "memories.SRAMPrimitive",
					"type": self.hc["L1_WEI_SRAM_TYPE"],
					"entry_bits": self.hc["L1_WEI_SRAM_SIZE"][0],
					"rows": self.hc["L1_WEI_SRAM_SIZE"][1],	
					"mode": 0,#0 is read, 1 is write
				}
			},
			#CROSSBARS and NETWORKS
			"WEI_CROSSBAR": {		
				"units": self.hc["TN"]*self.hc["TY"]*self.hc["TX"]*self.hc["TB"],
				"input_metadata": {
				"toggle": {
					"update": '0',			}
	
				},
				"input_bins": [ self.hc["WEI_PREC"]*self.hc["TI"]*self.hc["TKY"]*self.hc["TKY"] ,  (self.hc["TI"]*self.hc["TKY"]*self.hc['TKX'])//SPARSE_RATIO  ],	
				"input_group": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY'],
#, 
#				self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]], #for accumulation

				#trading physical for time, used for sparse flow at the crossbar
				#"input_hold_cycles": [SPARSE_RATIO, SPARSE_RATIO] ,#["max_valid_updated_store_wei_crossbar[1][s]", "max_valid_updated_store_wei_crossbar[1][s]" ] ,#["max_valid_updated_store_wei_crossbar[0][s]" , "max_valid_updated_store_wei_crossbar[1][s]" ],#[SPARSE_RATIO, SPARSE_RATIO],#"max_valid_updated_store_wei_crossbar[jjj][s]
				"input_hold_cycles": ["max_valid_updated_store_wei_crossbar[1][s]", "max_valid_updated_store_wei_crossbar[1][s]" ] ,#["max_valid_updated_store_wei_crossbar[0][s]" , "max_valid_updated_store_wei_crossbar[1][s]" ],#[SPARSE_RATIO, SPARSE_RATIO],#"max_valid_updated_store_wei_crossbar[jjj][s]
	
				#[SPARSE_RATIO, SPARSE_RATIO],#[

				"input_time_unrolled": [1 , SPARSE_RATIO ],
				"input_trace_name": [ "in", "sel"],
				#"inner_loop_unroll": SPARSE_RATIO,	
				#"input_hold_cycles": [SPARSE_RATIO , 1], #"valid_inner_terms"

				"accumulated_input": False,

					
				"update_condition": ['1', in_condition],#'weights_data != 0'],
				"cur_update": [  'weights_data', 'wei_crossbar % INNER_GROUP_SIZE'],#'weights_data'  ],
				#'prev_update': [ 'weights_data', 'weights_data'  ],#['weights_data', 'inputs_data'],

				"output_metadata": {},

				"output_bins":  self.hc["WEI_PREC"] ,
				"output_update": 'weights_data',
				"output_condition": 'weights_data != 0',	
				"output_inner_group": self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]//SPARSE_RATIO,
				#"output_outer_group": self.hc["TN"]*self.hc["TB"]*self.hc["TX"]*self.hc["TY"],

			
				'reset_trigger': [],

				#meaning output is accumulated
				'accumulate': False,#meaning the output is accumulated
				'accumulate_op': '',
	
				"config": {
					"primitive": "networks.MuxN",
					"type": self.hc["WEI_CROSSBAR_TYPE"],
					"prec": self.hc["WEI_PREC"],
					"terms": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY'],
					"out_terms": self.hc['TI']*self.hc['TKX']*self.hc['TKY']//SPARSE_RATIO,
					"out_net": "sel"
	
				},
				'hooks': {

				"core_before_outer_group_start": "",
				"core_before_inner_group_start": "",
				"core_after_inner_group_start":"",
				"core_after_data_fetch":"",
				"core_after_inner_group_end":"",
				"core_after_outer_group_end": ""

				},


			},
			"WEI_MULTICAST": {		
				"units": self.hc["TN"]*self.hc["TY"]*self.hc["TX"]*self.hc["TB"],
				"input_metadata": {
				"toggle": {
					"update": '0',			}
	
			},
				"input_bins": [ self.hc["WEI_PREC"]*self.hc["TI"]*self.hc["TKY"]*self.hc["TKY"]  ],	
				"input_group": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY'],
#, 
				"input_hold_cycles": ["max_valid_updated_store_wei_multicast[0][s]"] ,#["max_valid_updated_store_wei_crossbar[0][s]" , "max_valid_updated_store_wei_crossbar[1][s]" ],#[SPARSE_RATIO, SPARSE_RATIO],#"max_valid_updated_store_wei_crossbar[jjj][s]
				"input_time_unrolled": [  SPARSE_RATIO ],
				"input_trace_name": [ "in"],
				"accumulated_input": False,
				"update_condition": [in_condition],#'weights_data != 0'],
				"cur_update": [ 'weights_data'],# 'wei_crossbar % INNER_GROUP_SIZE'],#'weights_data'  ],

				"output_metadata": {},
				"output_bins":  self.hc["WEI_PREC"] ,
				"output_update": 'weights_data',
				"output_condition": 'weights_data != 0',	
				"output_inner_group": self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]//SPARSE_RATIO,
				'reset_trigger': [],
				'accumulate': False,#meaning the output is accumulated
				'accumulate_op': '',
				"config": {
					"primitive": "networks.Multicast",
					"type": self.hc["INTERCONNECT_TYPE"],
					"prec": self.hc["WEI_PREC"],
					"terms": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY']//SPARSE_RATIO,
					"fanout": self.hc['TB']*self.hc['TX']*self.hc['TY'],
				},
			},

			"INPUT_CROSSBAR": {		
				"units": self.hc["TN"]*self.hc["TY"]*self.hc["TX"]*self.hc["TB"],
				"input_metadata": {
				"toggle": {
					"update": '0',			}	
			},
				"input_bins": [ self.hc["ACT_PREC"]*self.hc["TI"]*self.hc["TKY"]*self.hc["TKY"] ,  (self.hc["TI"]*self.hc["TKY"]*self.hc['TKX'])//SPARSE_RATIO  ],	
				"input_group": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY'],
				"input_hold_cycles": ["max_valid_updated_store_input_crossbar[1][s]", "max_valid_updated_store_input_crossbar[1][s]" ] ,#["max_valid_updated_store_wei_crossbar[0][s]" , "max_valid_updated_store_wei_crossbar[1][s]" ],#[SPARSE_RATIO, SPARSE_RATIO],#"max_valid_updated_store_wei_crossbar[jjj][s]
				"input_time_unrolled": [1 , SPARSE_RATIO ],
				"input_trace_name": [ "in", "sel"],
				"accumulated_input": False,
				"update_condition": ['1', in_condition],#'weights_data != 0'],
				"cur_update": [  'inputs_data', 'input_crossbar % INNER_GROUP_SIZE '],#'weights_data'  ],
				"output_metadata": {},
				"output_bins":  self.hc["ACT_PREC"] ,
				"output_update": 'inputs_data',
				"output_condition": 'inputs_data != 0',	
				"output_inner_group": self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]//SPARSE_RATIO,
				'reset_trigger': [],
				#meaning output is accumulated
				'accumulate': False,#meaning the output is accumulated
				'accumulate_op': '',
				"config": {
					"primitive": "networks.Crossbar",
					"type": self.hc["ACT_CROSSBAR_TYPE"],
					"prec": self.hc["ACT_PREC"],
					"in_terms": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY'],
					"out_terms": self.hc['TI']*self.hc['TKX']*self.hc['TKY']//SPARSE_RATIO,	
				},
			},
			"ACT_MULTICAST": {		
				"units": self.hc["TN"]*self.hc["TY"]*self.hc["TX"]*self.hc["TB"],
				"input_metadata": {
				"toggle": {
					"update2": f'''0//__builtin_popcount(cur_wei_crossbar[wei_crossbar][jjj]^prev_wei_crossbar[wei_crossbar][jjj]) ''',
					"update": '0',			}	
			},
				"input_bins": [ self.hc["ACT_PREC"]*self.hc["TI"]*self.hc["TKY"]*self.hc["TKY"]  ],	
				"input_group": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY'],
				"input_hold_cycles": ["max_valid_updated_store_act_multicast[0][s]" ] ,#["max_valid_updated_store_wei_crossbar[0][s]" , "max_valid_updated_store_wei_crossbar[1][s]" ],#[SPARSE_RATIO, SPARSE_RATIO],#"max_valid_updated_store_wei_crossbar[jjj][s]
				"input_time_unrolled": [ SPARSE_RATIO ],
				"input_trace_name": [ "in"],
				"accumulated_input": False,
				"update_condition": [ in_condition],#'weights_data != 0'],
				"cur_update": [  'inputs_data'],#'weights_data'  ],
				"output_metadata": {},
				"output_bins":  self.hc["ACT_PREC"] ,
				"output_update": 'inputs_data',
				"output_condition": 'inputs_data != 0',	
				"output_inner_group": self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]//SPARSE_RATIO,
				'reset_trigger': [],
				#meaning output is accumulated
				'accumulate': False,#meaning the output is accumulated
				'accumulate_op': '',
				"config": {
					"primitive": "networks.Multicast",
					"type": self.hc["ACT_CROSSBAR_TYPE"],
					"prec": self.hc["ACT_PREC"],
					"terms": self.hc["TI"]*self.hc["TKX"]*self.hc['TKY']//SPARSE_RATIO,
					"fanout": self.hc['TN'],
	
				},
			},


			"PE_ARRAY": {
				"units": (self.hc["TI"]*self.hc["TN"]*self.hc["TB"]*self.hc["TKX"]*self.hc["TKY"]*self.hc["TX"]*self.hc["TY"] ),# //SPARSE_RATIO,
				"input_metadata": {"bits": {
					"update": f"__builtin_popcount(weights_data) + {self.hc['WEI_PREC']}*__builtin_popcount(inputs_data)"
				}},
				"input_bins": [self.hc["WEI_PREC"], self.hc["ACT_PREC"]],

				"input_hold_cycles": ["max_valid_updated_store_pe_array[1][s]", "max_valid_updated_store_pe_array[1][s]" ] ,#["max_valid_updated_store_wei_crossbar[0][s]" , "max_valid_updated_store_wei_crossbar[1][s]" ],#[SPARSE_RATIO, SPARSE_RATIO],#"max_valid_updated_store_wei_crossbar[jjj][s]

				"input_time_unrolled": [1, 1 ],
				"unit_time_unrolled": [SPARSE_RATIO, SPARSE_RATIO ],
	
				"input_trace_name": [ "multiplicand", "factor"],
	
				'update_condition': [in_condition]*2,#'weights_data != 0'],#[ "weights_data != 0", "weights_data !=  0"  ],
				'cur_update': MULTIPLIER_bins,#[ 'weights_data', 'inputs_data'],
				'input_group': 1,
				"output_metadata": { },
				"output_bins": self.hc["WEI_PREC"]+self.hc["ACT_PREC"],
				"output_update": 'weights_data * inputs_data',
				"output_condition": '',
				"accumulated_input": False,
				'reset_trigger': [],
				'accumulate': False,
				'accumulate_op': '',
				"config": {
					"primitive": "multipliers.Multiplier2",
					"multiplierType": self.hc["MULT_TYPE"],
					"adderType": self.hc["MULT_CORE_ADDER_TYPE"],
					"side": self.hc.get("MULT_SIDE", "weight"),
					"prec1":MULT_prec1, "prec2": MULT_prec2, "radix": self.hc['MULT_RADIX']
				}
			},


			"L1_OUT": {
				"units": self.hc["TN"]*self.hc["TN"],
				"config": {

				}	
			},
			"L1_WEI": {
				"units": self.hc["TI"]*self.hc["TN"],
				"config": {

				}
			},
			"L1_ACT": {
				"units": self.hc["TI"]*self.hc["TB"],
				"config": {

				}
			},
			"L2_WEI": {
				"units": 512,
				"config": {

				}
			},
		}
		
	def infer_wei_crossbar(self, params):
		PARAMETERS = params['params']
		DATA = [
			params['inputs_obj']	,
			params['weights_obj']
		]
		NET_DATA = {
			"WEI_CROSSBAR": self.MODULES["WEI_CROSSBAR"],
		#	"WEI_MULTICAST": self.MODULES["WEI_MULTICAST"]	
		}	
		skips = ["TB", "TX", "TY"]#["TB"]#["TB", "TX", "TY"]

		self.MODULES["WEI_CROSSBAR"]['skips'] = skips
		LOOP_ORDER = self.hc["LOOP_ORDER"]
		LOOP_VAR_DEFINITIONS = self.LOOP_VAR_DEFINITIONS			
		hooks = {}#self.MODULES["PE_ARRAY"]["hooks"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]
		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] , inner_loops_skips = skips)
		return output_files
	
	def infer_wei_multicast(self, params):
		PARAMETERS = params['params']
		DATA = [
			params['inputs_obj']	,
			params['weights_obj']
		]
		NET_DATA = {
			"WEI_MULTICAST": self.MODULES["WEI_MULTICAST"]	
		}	
		skips = ["TB", "TX", "TY"]#["TB"]#["TB", "TX", "TY"]


		self.MODULES["WEI_MULTICAST"]['skips'] = skips	
		LOOP_ORDER = self.hc["LOOP_ORDER"]
		LOOP_VAR_DEFINITIONS = self.LOOP_VAR_DEFINITIONS			
		hooks = {}#self.MODULES["PE_ARRAY"]["hooks"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]
		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] , inner_loops_skips = skips)
		return output_files

	def infer_input_multicast(self, params):
		PARAMETERS = params['params']
		DATA = [
			params['inputs_obj']	,
			params['weights_obj']
		]
		NET_DATA = {
			"ACT_MULTICAST": self.MODULES["ACT_MULTICAST"]	
		}	
		skips = ["TN"]#["TB"]#["TB", "TX", "TY"]
		self.MODULES["ACT_MULTICAST"]['skips'] = skips
	

		LOOP_ORDER = self.hc["LOOP_ORDER"]
		LOOP_VAR_DEFINITIONS = self.LOOP_VAR_DEFINITIONS			
		hooks = {}#self.MODULES["PE_ARRAY"]["hooks"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]
		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] , inner_loops_skips = skips)
		return output_files



	def infer_input_crossbar(self, params):
		PARAMETERS = params['params']
		DATA = [
			params['inputs_obj']	,
			params['weights_obj']	
		]
		NET_DATA = {
			"INPUT_CROSSBAR": self.MODULES["INPUT_CROSSBAR"]
		}	
		skips = ["TN"]#["TB", "TX", "TY"]
		self.MODULES["INPUT_CROSSBAR"]['skips'] = skips
	

		LOOP_ORDER = self.hc["LOOP_ORDER"]
		LOOP_VAR_DEFINITIONS = self.LOOP_VAR_DEFINITIONS			
		hooks = {}#self.MODULES["PE_ARRAY"]["hooks"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]
		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] , inner_loops_skips = skips)
		return output_files
	
	
	
	def infer_pe(self,params):
		#any parameters we want to copy into the cpp
		PARAMETERS = params['params']
		#data we want to copy to the cpp
		DATA = [
			params['inputs_obj'],
			params['weights_obj']]
		#nets / hardware modules we want to track the toggling and features of 
		NET_DATA = {
			"PE_ARRAY": self.MODULES["PE_ARRAY"]
		}	
		#loop orders and such
		LOOP_ORDER = self.hc["LOOP_ORDER"]
		#variable definitions
		LOOP_VAR_DEFINITIONS = self.LOOP_VAR_DEFINITIONS			
		



		hooks = {}#self.MODULES["PE_ARRAY"]["hooks"]
		#generate the c++ file
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]

		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] )

		return output_files
	
	def infer_adder_accum(self,params):
		return {}	

	def infer_buffers(self,params): 
		return {}	


	def prepare_data(self, params):
		#convolution data

		input_data = params['input_data']
		weights = params['weight']

		#convolution prepare
		#input_data = input_data[0] #if is tuple
		OUT =  weights.shape[0]
		IN = weights.shape[1]
		KX = weights.shape[2]
		KY = weights.shape[3]

		BAT = input_data.shape[0]
		input_IN = input_data.shape[1]
		X = input_data.shape[2]
		Y = input_data.shape[3]
		print(input_data.shape)
		print(weights.shape)
		assert(input_data.shape[1] == weights.shape[1])
		
		#quantize (fixed point)
		#(todos) some algorithm to choose the scaling ?
		weights    = ((weights*256*256) %self.hc['WEI_PREC']).astype(np.int32)
		input_data = ((input_data*256*256) %self.hc['ACT_PREC']).astype(np.int32)
		#Randomize weights and inputs (TODOS)
		Randomize = params["SIM_PARAMS"]["Randomize"]
		Wei_Sparsity = params["SIM_PARAMS"]["Wei_Sparsity"]
		Act_Sparsity = params["SIM_PARAMS"]["Act_Sparsity"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]

		np_save= params['SIM_PARAMS']['save_np']
	

		#Randomize weights and inputs (TODOS)
		if(Randomize):
			n = IN*OUT*KX*KY
	
			k = int(n*Wei_Sparsity)
			#print(k, n)
			rand_wei = np.random.randint(0, 1<<self.hc["WEI_PREC"], size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_wei[zero_indices] = 0
			
			n = IN*BAT*X*Y
	
			k = int(n*Act_Sparsity)
			rand_act = np.random.randint(0, 1<<self.hc["ACT_PREC"], size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_act[zero_indices] = 0
			
			weights = rand_wei.reshape((OUT, IN, KX, KY))
			input_data = rand_act.reshape((BAT, IN, X, Y))
		
		w_file = root+"/"+name+".weights.txt"
		i_file = root+"/"+name+".input.txt"
		if(np_save):
			weights = rand_wei.reshape((-1))#OUT, IN, KX, KY))
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))
	
			np.savetxt(w_file, weights, fmt='%d', delimiter='\n')
			np.savetxt(i_file, input_data, fmt='%d', delimiter='\n')
			weights = rand_wei.reshape((-1))#OUT, IN, KX, KY))
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))
	
			weights = rand_wei.reshape((OUT, IN, KX, KY))
			input_data = rand_act.reshape((BAT, IN, X, Y))
	
		return {
			"params":{
				"IN": IN,
				"OUT": OUT,
				"BAT": BAT,	
				"FILTER_KX": KX, 
				"FILTER_KY": KY,
				"INPUT_X": X,
				"INPUT_Y": Y,

			},
			"weights_obj": 
				{
				"name": "weights",
				"file": w_file,
				"size": len(weights.reshape((-1))),
				"indexing": "n*IN*FILTER_KX*FILTER_KY+i*FILTER_KX*FILTER_KY+ky*FILTER_KX+kx"
			},
			"inputs_obj":
				{
				"name": "inputs",
				"file": i_file,
				"size": len(input_data.reshape((-1))),
				"indexing": "b*IN*INPUT_X*INPUT_Y+i*INPUT_X*INPUT_Y + y*INPUT_X + x"	
			},
		}
		
	def infer(self, params):
		self.get_primitive_statistics()
		self.LOOP_VAR_DEFINITIONS = {
			"B": {
				"LIM": "BAT",
				"STRIDE": 1,
				"GROUP": "OUTER"
			},
			"I": {
				"LIM": "IN",
				"STRIDE": 1,
				"GROUP": "INNER", #meaning can be collected together in the sum
			},
			"N": {
				"LIM": "OUT",
				"STRIDE": 1,
				"GROUP": "OUTER"
			},	
			"X": {
				"LIM": "INPUT_X",
				"STRIDE": params['stride'][0],	
				"GROUP": "OUTER",
			},
			"Y": {
				"LIM": "INPUT_Y",
				"STRIDE": params['stride'][1],	
				"GROUP": "OUTER",
			},
			"KX": {
				"LIM": "FILTER_KX",
				"STRIDE": 1,#params['stride'],	
				"GROUP": "INNER",
			},
			"KY": {
				"LIM": "FILTER_KY",
				"STRIDE": 1,#params['stride'],	
				"GROUP": "INNER",
			},


	
		}


		print(params)	
		p = params
		p.update(self.prepare_data(p))

		results = []

		#results.append(self.infer_pe(p))
		#results.append(self.infer_multicast(p))
		results.append(self.infer_wei_crossbar(p))
		results.append(self.infer_wei_multicast(p))
	
		results.append(self.infer_input_crossbar(p))
		results.append(self.infer_input_multicast(p))
	
		#results.append(self.infer_pe(p))

		#if(p.get("RUN_PE",1)):
		#	results.append(self.infer_pe(p))
		#if(p.get("RUN_ADDER_ACCUM", 1)):
		#	results.append(self.infer_adder_accum(p))
		#if(p.get("RUN_BUFFERS",1)):
		#	results.append(self.infer_buffers(p))
		return results

def core(test_id, hardware_config, benchmark = {}, MODE = 0):	
	
	"""
	hardware_config_reference = {
	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 1,
	"TN": 16,
	"TI": 16,
	"TX": 1,
	"TY": 1,
	"TKX": 1,
	"TKY": 1,
	"LOOP_ORDER": ["B", "N", "I", "X", "Y", "KX", "KY"],

	"SPARSE_RATIO": 4, #we can compress from 4 to 4
	"SPARSE_SIDE": "weights",
	"WEIGHT_COMPRESSION": "none",
	"INPUT_COMPRESSION" : "none",	
	"OUTPUT_COMPRESSION": "none",

	"WEI_CROSSBAR_TYPE": "Full",#Full, Partial, Butterfly, Benes, 
	"ACT_CROSSBAR_TYPE": "Full",

	"MULT_TYPE": "HighRadixMultiplier",
	"MULT_SIDE": "weight",
	"MULT_RADIX": 4,
	"MULT_CORE_ADDER_TYPE": "SimpleAdder2",

	"ADDER_TREE_TYPE": "Simple",
	"ADDER_TREE_PREC": 16,

	"ACCUM_TYPE": "BitSerial",
	"ACCUM_PREC": 32,

	"L1_WEI_SRAM_SIZE": [8, 64],
	"L1_ACT_SRAM_SIZE": [8, 64],	
	"L1_WEI_SRAM_TYPE": "Reg",
	"L1_ACT_SRAM_TYPE": "Reg",	
	"L1_WEI_TOTAL_SIZE" : 48000,
	"L1_ACT_TOTAL_SIZE" : 48000,

	"L1_OUT_SRAM_SIZE": [8, 64],
	"L1_OUT_SRAM_TYPE": "Reg",
	"L1_OUT_TOTAL_SIZE" : 48000,
	
	"L2_SRAM_SIZE": [8, 64],	
	"L2_TOTAL_SIZE": 512000,

	#skip DRAM for now... no discussion.
	"DRAM_LEN": 512,

	#Interconnections and if any queueing buffers between layers
	"INTERCONNECT_TYPE": "Multicast_Tree",#Multicast,
	#"WEI_MULTICAST_TYPE": "MulticastTree",#
	"INTERCONNECT_WEI_SYSTOLIC_CAST_RATIO": 1,
	"INTERCONNECT_ACT_SYSTOLIC_CAST_RATIO": 1,
	"INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO": 1,
	"INTERCONNECT_ACT_SYSTOLIC_LOAD_RATIO": 1,	
	"INTERCONNECT_OUT_SYSTOLIC_LOAD_RATIO": 1,
	
	"INTERCONNECT_ACT_INTER_PE_X": False,
	"INTERCONNECT_ACT_INTER_PE_Y": False,
	#"INTERCONNECT_PSUM_SYSTOLIC_LOAD_RATIO": 1,

	"INTERCONNECT_L2_SYSTOLIC_LOAD_RATIO": 1,#compared to max(L1_WEI_LEN, L1_ACT_LEN)
	



	"CLOCK": 1,
	"cap_load": 1.0,
	"tech":"tsmc40",

	}

	input_data = paddle.randn([4, 32, 28, 28])
	layer = nn.Conv2D(in_channels=32, out_channels=64, kernel_size=3)#skip bias for now
	output_data = layer(input_data) 	
	repr_str = repr(layer)
	weight_name = repr(layer).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")
	input_name = repr(input_data.shape).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")

	#print(weight_name)
	#print(input_name)
	#exit()
	network = {
	"input_data" :input_name,
		"layer": weight_name,
	
	}
	
	#print(layer)
	network_layer_reference = {
	"layer_name": dict_to_str(network),#"Conv1",
	"layer": layer,
	"input_data": input_data,
	"output_data": output_data,
	}

	benchmark

	mapping_reference = {
	"Linear1": "df1",
	}

	design = dict_to_str(hardware_config)

	SIM_PARAMS = {
	"name": network_layer['layer_name'],
	"root": f"generated/Architecture/SparseConv/{design}",
	"SIM_CYCLES": 10,
	"Randomize": 1,
	"Wei_Sparsity": 0.1,
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
	'MODE': MODE,
	"RUN_GOLDEN_SBT": 1,
	
	#'GEN_TRACE':True,
	'RUN_CPP': True
}
	SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])
	"""
	SIM_PARAMS = benchmark["SIM_PARAMS"]

	#FULL
	if(SIM_PARAMS['MODE'] == 0):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True	
		SIM_PARAMS['RUN_GOLDEN_SBT'] = True
	#ONLY TRACE	
	elif(SIM_PARAMS['MODE'] == 1):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True	
		SIM_PARAMS['RUN_GOLDEN_SBT'] = False

	#RUN POWER SIMS ONLY
	elif(SIM_PARAMS['MODE'] == 2):	
		SIM_PARAMS['GEN_TRACE'] = False
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
		SIM_PARAMS['RUN_GOLDEN_SBT'] = True
	#DEBUG TRACE
	elif(SIM_PARAMS['MODE'] == 3):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False	
		SIM_PARAMS['RUN_GOLDEN_SBT'] =False 
	#DEBUG TRACE
	elif(SIM_PARAMS['MODE'] == 4):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = True
		SIM_PARAMS['RUN_GOLDEN_SBT'] =False 
	#GEN TRACE AND RUN	
	elif(SIM_PARAMS['MODE'] == 5):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
		SIM_PARAMS['RUN_GOLDEN_SBT'] = True
	#GEN TRACE AND RUN WITH RELOADED WEIGHTS
	elif(SIM_PARAMS['MODE'] == 6):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = True
		SIM_PARAMS['RUN_GOLDEN_SBT'] = True
	elif(SIM_PARAMS['MODE'] == 7):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] =False
		SIM_PARAMS['RUN_GOLDEN_SBT'] = False
	elif(SIM_PARAMS['MODE'] == 8):	
		SIM_PARAMS['GEN_TRACE'] = False
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] =False
		SIM_PARAMS['RUN_GOLDEN_SBT'] = False
	elif(SIM_PARAMS['MODE'] == 9):	
		SIM_PARAMS['GEN_TRACE'] = False
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] =False
		SIM_PARAMS['RUN_GOLDEN_SBT'] = False
	
	else:
		print("invalid option, select from")
		print("0. FULL")
		print("1. RERUN TRACE")
		print("2. RUN_POWERS")
		print("3. GEN_TRACE")
		print("4. GEN_TRACE_NO_GEN_DATA")
		print("5. RUN_POWERS_RERUN_TRACE")
		print('''
	#FULL
	if(SIM_PARAMS['MODE'] == 0):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True	
		SIM_PARAMS['RUN_SBT'] = True
	#ONLY TRACE	
	elif(SIM_PARAMS['MODE'] == 1):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True	
		SIM_PARAMS['RUN_SBT'] = False

	#RUN POWER SIMS ONLY
	elif(SIM_PARAMS['MODE'] == 2):	
		SIM_PARAMS['GEN_TRACE'] = False
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
		SIM_PARAMS['RUN_SBT'] = True
	#DEBUG TRACE
	elif(SIM_PARAMS['MODE'] == 3):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False	
		SIM_PARAMS['RUN_SBT'] =False 
	#DEBUG TRACE
	elif(SIM_PARAMS['MODE'] == 4):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = True
		SIM_PARAMS['RUN_SBT'] =False 
	#GEN TRACE AND RUN	
	elif(SIM_PARAMS['MODE'] == 5):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
		SIM_PARAMS['RUN_SBT'] = True
	#GEN TRACE AND RUN WITH RELOADED WEIGHTS
	elif(SIM_PARAMS['MODE'] == 6):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = True
		SIM_PARAMS['RUN_SBT'] = True

''')
		exit()

	network_layer = benchmark['network_layer']
	mapping = benchmark['mapping']
	#SIM_PARAMS = benchmark["SIM_PARAMS"]


	design = dict_to_str(hardware_config)

	SIM_PARAMS['name'] = network_layer['layer_name']
	SIM_PARAMS["root"] = f"generated/Arch/SparseConv/{design}"	
	SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])


	#FLOW 1. compare against baselines and 
	ld =  SparseConv(hardware_config)
	#	if(not (not SIM_PARAMS['RUN_CPP'] and not  SIM_PARAMS['save_np'] and not SIM_PARAMS['GEN_TRACE'])):
	traces = ld.gen_perf_trace(network_layer,mapping, SIM_PARAMS) 
	#exit()

	if(MODE != 9):
		ld.estimate_golden_pwr(traces, network_layer,mapping, SIM_PARAMS)

	root = SIM_PARAMS.get("root", "generated/Architecture/GeneralUnit")
	SAVE_RESULTS = SIM_PARAMS.get("SAVE_RESULTS", "generated/Architecture/GeneralUnit")		
	
	if(test_id == 0 and MODE == 8):
		root = SIM_PARAMS.get("root", "generated/Architecture/GeneralUnit")
		root = "/".join(root.split("/")[0:-1])
		SAVE_RESULTS = SIM_PARAMS.get("SAVE_RESULTS", "generated/Architecture/GeneralUnit")		
	
		with open(root+"/"+SAVE_RESULTS+".head.txt", "w") as f:
			f.write("")		

		with open(root+"/"+SAVE_RESULTS+".tail.txt", "w") as f:
			f.write("")#tail + "\n")		
	
	if(MODE == 8):
		ld.analyze_results(traces, network_layer,mapping, SIM_PARAMS)
	
	
	if (MODE == 9):
		ld.estimate_our_pwr_v1(traces,network_layer,mapping, SIM_PARAMS)	
		exit()	
	#ld.estimate_our_pwr(traces,network_layer,mapping, SIM_PARAMS)
	#ld.estimate_b1_pwr(traces,network_layer, mapping,SIM_PARAMS)#maestro
	#ld.estimate_b2_pwr(traces, network_layer,mapping,SIM_PARAMS)#accelergy 
	#ld.estimate_b3_pwr(traces, network_layer,mapping,SIM_PARAMS)#others?


if __name__ == "__main__":
	import sys	
	MODE = int(sys.argv[-1]	)
	#define hardware_configs
	combos = []

	base_hardware_config = {
	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 1,
	"TN": 16,
	"TI": 16,
	"TX": 1,
	"TY": 1,
	"TKX": 1,
	"TKY": 1,
	"LOOP_ORDER": ["B", "N", "I", "X", "Y", "KX", "KY"],

	"SPARSE_RATIO": 4, #we can compress from 4 to 4
	"SPARSE_SIDE": "weights",
	"WEIGHT_COMPRESSION": "n",
	"INPUT_COMPRESSION" : "n",	
	"OUTPUT_COMPRESSION": "n",

	"WEI_CROSSBAR_TYPE": "Full",#Full, Partial, Butterfly, Benes, 
	"ACT_CROSSBAR_TYPE": "Full",

	"MULT_TYPE": "HighRadixMultiplier",
	"MULT_SIDE": "weight",
	"MULT_RADIX": 4,
	"MULT_CORE_ADDER_TYPE": "SimpleAdder2",

	"ADDER_TREE_TYPE": "Simple",
	"ADDER_TREE_PREC": 16,

	"ACCUM_TYPE": "BitSerial",
	"ACCUM_PREC": 32,

	"L1_WEI_SRAM_SIZE": [8, 64],
	"L1_ACT_SRAM_SIZE": [8, 64],	
	"L1_WEI_SRAM_TYPE": "Reg",
	"L1_ACT_SRAM_TYPE": "Reg",	
	"L1_WEI_TOTAL_SIZE" : 48000,
	"L1_ACT_TOTAL_SIZE" : 48000,

	"L1_OUT_SRAM_SIZE": [8, 64],
	"L1_OUT_SRAM_TYPE": "Reg",
	"L1_OUT_TOTAL_SIZE" : 48000,
	
	"L2_SRAM_SIZE": [8, 64],	
	"L2_TOTAL_SIZE": 512000,

	#skip DRAM for now... no discussion.
	"DRAM_LEN": 512,

	#Interconnections and if any queueing buffers between layers
	"INTERCONNECT_TYPE": "Multicast_Tree",#Multicast,
	#"WEI_MULTICAST_TYPE": "MulticastTree",#
	"INTERCONNECT_WEI_SYSTOLIC_CAST_RATIO": 1,
	"INTERCONNECT_ACT_SYSTOLIC_CAST_RATIO": 1,
	"INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO": 1,
	"INTERCONNECT_ACT_SYSTOLIC_LOAD_RATIO": 1,	
	"INTERCONNECT_OUT_SYSTOLIC_LOAD_RATIO": 1,
	
	"INTERCONNECT_ACT_INTER_PE_X": False,
	"INTERCONNECT_ACT_INTER_PE_Y": False,
	#"INTERCONNECT_PSUM_SYSTOLIC_LOAD_RATIO": 1,

	"INTERCONNECT_L2_SYSTOLIC_LOAD_RATIO": 1,#compared to max(L1_WEI_LEN, L1_ACT_LEN)

	"CLOCK": 1,
	"cap_load": 0.1,
	"tech":"tsmc40",

	}
	
	for wei_prec in [8, 16]:
		for act_prec in [8, 16]:	
			for side in ['weights', 'inputs', 'both']:
	
				for     tb,tn,ti,tx,ty,tkx,tky in [
		        	[1,16,  16,1,  1,  1,1],
        			[1,8,  8,1,  1,  2,2],
        			[1,8,  8,1,  2,  1,2],	
        			[1,16,  4,1,  2,  1,2],	
        			[1,4,  16,2,  2,  1,2],			
        			[2,4,  8,2,  2,  1,1],			
	       			[2,2,  16,2,  2,  1,1],			
	       			[1,8,  32,1,  1,  1,1],			
				]:
					for lp in [ 
					["B", "N", "I", "KX", "KY", "X", "Y"],
					["B", "N", "Y", "X", "I", "KX", "KY"],
					["B", "Y", "X", "KY", "KX", "I", "N"],
					["KY", "KX", "I", "X", "Y", "B", "N"],
					["I", "N", "KX", "KY", "Y", "X", "B"],
					["B", "N", "I", "X", "Y", "KX", "KY"],	
				       ]:
						for sparse_ratio in [1, 2, 4, 8, 16]:
							if(sparse_ratio > ti*tkx*tky):
								continue
					
							hc = dict(base_hardware_config)
							hc["SPARSE_RATIO"] = sparse_ratio
							hc["TB"] =  tb
							hc["TI"] =  ti
							hc["TN"] =  tn
							hc["TX"] =  tx
							hc["TY"] =  ty
							hc["TKX"] =  tkx
							hc["TKY"] =  tky		
							hc["SIDE"] = side
							hc["LOOP_ORDER"] = lp
							hc["WEI_PREC"] = wei_prec
							hc["ACT_PREC"] = act_prec
							combos.append(hc)							

	benchmarks = []

	#reference
	input_data = paddle.randn([4, 32, 28, 28])
	layer = nn.Conv2D(in_channels=32, out_channels=64, kernel_size=3)#skip bias for now
	output_data = layer(input_data) 	
	repr_str = repr(layer)
	weight_name = repr(layer).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")
	input_name = repr(input_data.shape).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")

	network = {
	"input_data" :input_name,
		"layer": weight_name,	
	}
	
	#print(layer)
	base_network_layer = {
	"layer_name": dict_to_str(network),#"Conv1",
	"layer": layer,
	"input_data": input_data,
	"output_data": output_data,
	}

	base_mapping = {
	"SparseConv": "df1",
	}

	design = dict_to_str(base_hardware_config)

	base_SIM_PARAMS = {
	"SAVE_RESULTS": "analyzed_04_03",

	"name": base_network_layer['layer_name'],
	"root": f"generated/Arch/SparseConv/{design}",
	"SIM_CYCLES": 1000,
	"Randomize": 1,
	"Wei_Sparsity": 0.1,
	"Act_Sparsity": 0.1,	
	'save_np':True,#False,# True,
	'MODE': MODE,
	"RUN_GOLDEN_SBT": 1,	
	'RUN_CPP': True
	}
	SIM_PARAMS = base_SIM_PARAMS
	base_SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])

	
	for Wei_Sparsity in [0.1, 0.8]:
		for Act_Sparsity in [0.1 ,0.8]:	
			for batch, in_channels, out_channels, kernel_size, stride, X, Y in [
			     #[4    ,   32,         64,            3,         1,    32, 64],
#         	             [4    ,   3,         64,            7,         2,    32, 64],
			     [4    ,   64,         64,            5,         2,    32, 64],
		   	     [4    ,   8,         8,            3,         1,    32, 32],
			     [4    ,   32,         32,            1,         1,    32, 32],
			     #[4    ,   8,         16,            1,         1,    16, 32],	
	
			]:	

				for SIM_CYCLES in [10]:#, 100]:
					
					benchmark = {
									'SIM_PARAMS': dict(base_SIM_PARAMS),
									'network_layer': dict(base_network_layer),
									'mapping': dict(base_mapping)
								}
		
					benchmark["SIM_PARAMS"]["Randomize"] = 1
					benchmark["SIM_PARAMS"]["Wei_Sparsity"] = Wei_Sparsity
					benchmark["SIM_PARAMS"]["Act_Sparsity"] = Act_Sparsity
					benchmark["SIM_PARAMS"]["SIM_CYCLES"] = SIM_CYCLES
	
	
					input_data = paddle.randn([batch, in_channels, X, Y])
					layer = nn.Conv2D(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride = stride)#skip bias for now
	
					output_data = layer(input_data) 	
					repr_str = repr(layer)
					weight_name = repr(layer).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")
					input_name = repr(input_data.shape).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")
	
					network = {
								"input_data" :input_name,
								"layer": weight_name,	
								}
		
								#print(layer)
					network_layer = {
									"layer_name": dict_to_str(network),#"Conv1",
									"layer": layer,
									"input_data": input_data,
									"output_data": output_data,
								}
	
					benchmark["network_layer"] = network_layer
					benchmarks.append(benchmark)
	
	'''
	combos = [base_hardware_config]
	benchmarks = [ {
		'SIM_PARAMS': base_SIM_PARAMS
		'network_layer': base_network_layer
		'mapping': base_mapping
		}]
	'''
	
	tested = 0

	for inputs in combos:
		for benchmark in [benchmarks[0]]:
			core(tested, inputs, benchmark, MODE)	
		tested += 1
		#if(tested > 2):
		#	exit()	



