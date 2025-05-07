from ArchTemplates import GeneralLinearUnit, generate_cpp, dict_to_str

import numpy as np
import paddle.nn as nn
import pandas as pd

from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive
	
"""
hardware_config = {
	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 8,
	"TN": 8,
	"TI": 8,
	"LOOP_ORDER": ["B", "N", "I"],

	"MULT_TYPE": "Simple",
	"MULT_RADIX": 4,

	"ADDERTREE_TYPE": "Simple",

	"ACCUM_TYPE": "BitSerial",

	"SRAM_SIZE": [8, 64],
	"SRAM_TYPE": "Reg",
	"L1_WEI_LEN" : 512,
	"L1_ACT_LEN" : 64,
	"L2_LEN" : 512,
	"DRAM_LEN": 512

	"INTERCONNECT_TYPE": "Multicast_Tree",

}
network_layer = {
	"layer_name": "Linear1",
	"layer": nn.Linear(1024,1024), 
	"input_data": input_data,
	"output_data" output_data,
}
mapping = {
	"Linear1": "df1",
}
SIM_PARAMS = {
	"name": "LinearDirect",
	"root": "generated/Architecture"
	"SIM_CYCLES": -1,
	"Randomize": 1,
	"wei_sparsity": 0.9,
	"act_sparsity": 0.9,	
}
"""
class LinearDirect(GeneralLinearUnit):
#	def estimate_golden_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
#		print(traces)
#		pass	

	"""
	def estimate_our_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		print(traces)
		pass

	def estimate_b1_pwr(self, traces, network_layer,mapping, SIM_PARAMS):#maestro
		pass

	def estimate_b2_pwr(self, traces, network_layer,mapping, SIM_PARAMS):#accelergy
		pass

	def estimate_b3_pwr(self, traces, network_layer,mapping, SIM_PARAMS):#aladdin
		pass

	def estimate_b4_pwr(self, traces, network_layer,mapping, SIM_PARAMS):#ETH's zigzag?
		pass

	def estimate_b5_pwr(self, traces, network_layer,mapping, SIM_PARAMS):#ETH's interstellar
		pass
	"""



	def get_primitive_statistics(self):
		
		if(self.hc["MULT_SIDE"] == "weight"):
			MULTIPLIER_bins = ['weights_data', 'inputs_data']		
			MULT_prec1 = self.hc['WEI_PREC']
			MULT_prec2 = self.hc["ACT_PREC"]	
		else:
			MULTIPLIER_bins = ['weights_data', 'inputs_data'][::-1]
			MULT_prec1 = self.hc['ACT_PREC']
			MULT_prec2 = self.hc["WEI_PREC"]	
	
	
		self.MODULES =  {
			"ADDER_TREE": {
				"units": self.hc["TB"]*self.hc["TN"],
				"config": {
					"primitive": "AdderN",
					"type": self.hc["ADDERTREE_TYPE"],
					"prec": self.hc["ADDERTREE_PREC"],
					"terms": self.hc["TI"]
				} 
			},
			"ACCUM": {
				"units": self.hc["TB"]*self.hc['TN'],
				"config":{
					"primitive": "AddAccumulate",
					"type": self.hc["ACCUM_TYPE"],
					"prec": self.hc["ACCUM_PREC"],
					"terms": 1,
				}
			},
			"PE_ARRAY": {
				"units": self.hc["TI"]*self.hc["TN"]*self.hc["TB"],
				"input_metadata": {"bits": {
					"update": f"__builtin_popcount(weights_data) + {self.hc['WEI_PREC']}*__builtin_popcount(inputs_data)"
				}},
				"input_bins": [self.hc["WEI_PREC"], self.hc["ACT_PREC"]],
				'prev_update': MULTIPLIER_bins,#['weights_data', 'inputs_data'],
				'input_group': 1,
				"output_metadata": [],
				"output_bins": [],


				'reset_trigger': [],
				'update': '0',#value
				'accumulate': False,
				'accumulate_op': '+',
				'hooks': {
					"core_before_outer_group_start": "",
				"core_before_inner_group_start": "",
				"core_after_inner_group_start":"",
				"core_after_data_fetch":"",
				"core_after_inner_group_end":"",
				"core_after_outer_group_end": ""

				},
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
		hooks = self.MODULES["PE_ARRAY"]["hooks"]
		#generate the c++ file
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]

		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] )

		#print(output_files)
		return output_files
	
	def infer_adder_accum(self,params):
		return {}	

	def infer_buffers(self,params): 
		return {}	


	def prepare_data(self, params):
		#input_data = input_data[0]
		
		input_data = params['input_data']
		weights = params['weight']

		#0. Prepare data
		#input_data = input_data[0] #if is tuple
		OUT =  weights.shape[1]
		IN = weights.shape[0]
		BAT = input_data.shape[0]
		input_IN = input_data.shape[1]
		print(input_data.shape)
		print(weights.shape)
		assert(input_data.shape[1] == weights.shape[0])
		
		#quantize (fixed point)
		#(todos) some algorithm to choose the scaling ?
		weights    = ((weights*256*256) %self.hc["WEI_PREC"]).astype(np.int32)
		input_data = ((input_data*256*256) %self.hc["ACT_PREC"]).astype(np.int32)
		
		#Randomize weights and inputs (TODOS)
		Randomize = params["SIM_PARAMS"]["Randomize"]
		Wei_Sparsity = params["SIM_PARAMS"]["Wei_Sparsity"]
		Act_Sparsity = params["SIM_PARAMS"]["Act_Sparsity"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]



		if(params["SIM_PARAMS"]['Randomize']):
			n = IN*OUT
			k = int(n*Wei_Sparsity)
			rand_wei = np.random.randint(0, 1<<self.hc["WEI_PREC"], size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_wei[zero_indices] = 0
			
			n = IN*BAT
			k = int(n*Act_Sparsity)
			rand_act = np.random.randint(0, 1<<self.hc["ACT_PREC"], size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_act[zero_indices] = 0
			
			weights = rand_wei.reshape((OUT, IN))
			input_data = rand_act.reshape((BAT, IN))
		
		w_file = root+"/"+name+".weights.txt"
		i_file = root+"/"+name+".input.txt"
		if(params['SIM_PARAMS']['save_np']):
			weights = rand_wei.reshape((-1))#OUT, IN, KX, KY))
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))
	
			np.savetxt(w_file, weights, fmt='%d', delimiter='\n')
			np.savetxt(i_file, input_data, fmt='%d', delimiter='\n')
		print("saved weights")
		print(weights)
		print(input_data)
		return {
			"IN": IN,
			"OUT": OUT,
			"BAT": BAT,
			"w_file": w_file,
			"i_file": i_file,
			"quant_weights": weights,
			"quant_inputs": input_data,
			"params":{
				"IN": IN,
				"OUT": OUT,
				"BAT": BAT,	
			},
			"weights_obj": 
				{
				"name": "weights",
				"file": w_file,
				"size": len(weights.reshape((-1))),
				"indexing": "n*IN+i"
			},
			"inputs_obj":
				{
				"name": "inputs",
				"file": i_file,
				"size": len(input_data.reshape((-1))),
				"indexing": "b*IN+i"	
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
		}


		print(params)	
		p = params
		p.update(self.prepare_data(p))

		results = []
		if(p.get("RUN_PE",1)):
			results.append(self.infer_pe(p))
		if(p.get("RUN_ADDER_ACCUM", 1)):
			results.append(self.infer_adder_accum(p))
		if(p.get("RUN_BUFFERS",1)):
			results.append(self.infer_buffers(p))
		return results


if __name__ == "__main__":
		

	hardware_config = {
	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 2,
	"TN": 2,
	"TI": 2,
	"LOOP_ORDER": ["B", "N", "I"],

	"MULT_TYPE": "HighRadixMultiplier",
	"MULT_SIDE": "weight",
	"MULT_RADIX": 4,
	"MULT_CORE_ADDER_TYPE": "SimpleAdder2",

	"ADDERTREE_TYPE": "Simple",
	"ADDERTREE_PREC": 16,

	"ACCUM_TYPE": "BitSerial",
	"ACCUM_PREC": 32,

	"SRAM_SIZE": [8, 64],
	"SRAM_TYPE": "Reg",
	"L1_WEI_LEN" : 512,
	"L1_ACT_LEN" : 64,
	"L2_LEN" : 512,
	"DRAM_LEN": 512,

	"INTERCONNECT_TYPE": "Multicast_Tree",
	
	"CLOCK": 1,
	"cap_load": 1.0,
	"tech":"tsmc40",

	}
	network_layer = {
	"layer_name": "Linear1",
	"layer": nn.Linear(4096,1024), 
	"input_data": np.random.random((4,4096)),
	"output_data": np.random.random((4, 1024)),
	}
	mapping = {
	"Linear1": "df1",
	}

	design = dict_to_str(hardware_config)

	SIM_PARAMS = {
	"name": network_layer['layer_name'],
	"root": f"generated/Architecture/LinearDirect/{design}",
	"SIM_CYCLES": 1000,
	"Randomize": 1,
	"Wei_Sparsity": 0.2,
	"Act_Sparsity": 0.8,	
	'save_np':True,#False,# True,

	#0: Baseline compare against golden
	#generate trace and cpp 
	#use specified sim-cycles

	#1: inference time
	#no trace, run_cpp, simcycles is -1

	#2: Debug-mode
	#Assume trace generated
	#only fine-tune the model powers
	'MODE': 0,
	"RUN_GOLDEN_SBT": 1,
	
	#'GEN_TRACE':True,
	#'RUN_CPP': True
}
	SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])

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
	

	#FLOW 1. compare against baselines and 
	ld =  LinearDirect(hardware_config)
	traces = ld.gen_perf_trace(network_layer,mapping, SIM_PARAMS) 
	ld.estimate_golden_pwr(traces, network_layer,mapping, SIM_PARAMS)
	ld.estimate_our_pwr_v1(traces,network_layer,mapping, SIM_PARAMS)	
	ld.estimate_our_pwr(traces,network_layer,mapping, SIM_PARAMS)
	ld.estimate_b1_pwr(traces,network_layer, mapping,SIM_PARAMS)#maestro
	ld.estimate_b2_pwr(traces, network_layer,mapping,SIM_PARAMS)#accelergy 
	ld.estimate_b3_pwr(traces, network_layer,mapping,SIM_PARAMS)#others?


