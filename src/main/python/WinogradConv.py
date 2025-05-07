from ArchTemplates import GeneralConvUnit, GeneralLinearUnit, generate_cpp, dict_to_str, filter_loop_order

import numpy as np
import paddle.nn as nn
import paddle
import pandas as pd

from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
#from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive

class WinogradConv(GeneralConvUnit):
	def get_primitive_statistics(self):

		#add some new tilings for the inner products mapping
		self.hc["TG"] = self.hc["TX"] + self.hc["TKX"] - 1
		self.hc["TGT"] = self.hc["TY"] + self.hc["TKY"] - 1

		self.hc["TB"] = self.hc["TX"] + self.hc["TKX"] - 1
		self.hc["TBT"] = self.hc["TY"] + self.hc["TKY"] - 1



		
		if(self.hc["MULT_SIDE"] == "weight"):
			MULTIPLIER_bins = ['weights_data', 'inputs_data']		
			MULT_prec1 = self.hc['WEI_PREC']
			MULT_prec2 = self.hc["ACT_PREC"]	
		else:
			MULTIPLIER_bins = ['weights_data', 'inputs_data'][::-1]
			MULT_prec1 = self.hc['ACT_PREC']
			MULT_prec2 = self.hc["WEI_PREC"]	
	
	
		self.MODULES =  {
			"G_WEI_MULT": {
				"units": self.hc["TN"]*self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]*self.hc["TG"],
				"input_metadata": {
				"toggle": {
					"update": f'''__builtin_popcount(cur_g_wei_mult[g_wei_mult][jjj]^prev_g_wei_mult[g_wei_mult][jjj]) ''',
			}},
				"input_bins": [ self.hc["WEI_PREC"], self.hc['WEI_PREC']  ],	
				"input_group": 1, #for accumulation
				"input_trace_name": [ "in1", "in2"],
	

				"accumulated_input": False,
				"cur_update": [  'weights_data', 'winoG_data'   ],

				"output_metadata": {},

				"output_bins":  self.hc["WEI_PREC"]*2 ,
				"output_update": 'weights_data * winoG_data',

				'reset_trigger': [],

				#meaning output is accumulated
				'accumulate': False,#meaning the output is accumulated
				'accumulate_op': '',
				
				"config": {	
					"primitive": "multipliers.ConstantMultiplier2",
					"type": self.hc["INTERCONNECT_G_MULT_TYPE"],
					"prec1": self.hc["WEI_PREC"],
					"out_prec": self.hc["WEI_PREC"]*2,
					"terms": 1,
				},


			},
			"G_WEI_ADDER": {
				"units": self.hc["TN"]*self.hc["TI"]*self.hc["TKY"]*self.hc["TG"],
				"input_metadata": {
				"toggle": {
					"update": f'''__builtin_popcount(cur_g_wei_mult[g_wei_mult][jjj]^prev_g_wei_mult[g_wei_mult][jjj]) ''',
			}},
				"input_bins": [ 2*self.hc["WEI_PREC"]]  ,	
				"input_group": self.hc["TKX"], #for accumulation

				"accumulated_input": False,
				"cur_update": [  'weights_data*winoG_data'   ],
				'prev_update': [ 'weights_data*winoG_data'  ],#['weights_data', 'inputs_data'],

				"output_metadata": {},

				#"toggles":{
				#	"update": "__builtin_popcount(out_value_g_wei_mult[g_wei_mult]^prev_out_value_g_wei_mult[g_wei_mult])",
	
				#},},

				"output_bins":  self.hc["WEI_PREC"]*2 ,
				"output_update": 'weights_data * winoG_data',

				'reset_trigger': [],

				#meaning output is accumulated
				'accumulate': True,#meaning the output is accumulated
				'accumulate_op': 'std::max(accumulate_g_wei_adder[group_g_wei_adder], weights_data * winoG_data )',
	
				"config":{
					"primitive": "AdderN",
					"type": self.hc["INTERCONNECT_G_ADD_TYPE"],
					"in_prec": self.hc["WEI_PREC"]*2,
					"out_prec": self.hc["WEI_PREC"]*2,
					"terms": self.hc["TKX"],
				}
			},
			#(todos)
			"G_WEI_MULTADD": {
				"units": 1,
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
		
	
	def infer_G_mapper(self, params):
		PARAMETERS = params['params']
		#data we want to copy to the cpp
		DATA = [
			params['weights_obj'],
			params['G_obj'],
			]
		#nets / hardware modules we want to track the toggling and features of 
		NET_DATA = {
			"G_WEI_MULT": self.MODULES["G_WEI_MULT"],
			#"G_WEI_ADDER" : self.MODULES["G_WEI_ADDER"],
		}	
		#loop orders and such
		LOOP_VAR_DEFINITIONS = {
		"N": {"LIM": "OUT","STRIDE": 1,"GROUP": "OUTER"},
		"I": {"LIM": "IN" ,"STRIDE": 1, "GROUP": "OUTER"},
		"KX":{"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "INNER"},
		"G":{"LIM": "WINO_G", "STRIDE": 1, "GROUP": "OUTER"},
		"KY":{"LIM": "FILTER_KY","STRIDE":1,"GROUP": "OUTER"},
		}

		LOOP_ORDER = filter_loop_order(self.hc["LOOP_ORDER"], LOOP_VAR_DEFINITIONS.keys()) + ["KX", "KY", "G"]
		#variable definitions
		#LOOP_VAR = dict(self.LOOP_VAR_DEFINITIONS)
		

		hooks = {
			"core_before_outer_group_start": "",
			"core_before_inner_group_start": 'std::cout << "finished outer group" << std::endl; ',
			"core_after_inner_group_start":
'std::cout << "after inner group start" << std::endl;',
			"core_after_data_fetch":f'''
        std::cout << "weights_idx\t" << weights_idx << std::endl;
	std::cout << "weights" << weights_data << std::endl;
        std::cout << n << "\t" << i << "\t" << ky << "\t" << kx << std::endl;
        std::cout << "winoG_idx\t" << winoG_idx << std::endl;
	std::cout << "winoG" << winoG_data << std::endl;
        std::cout << g << "\t" << ky << "\t" << kx << std::endl;
''',
			"core_after_inner_group_end":"",
			"core_after_outer_group_end": "",
		}
	
		#generate the c++ file
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]

		output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] )

		#print(output_files)
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
		



		hooks = self.MODULES["PE_ARRAY"]["hooks"]
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
	

		import wincnn
		wino_AT,wino_G,wino_BT,wino_f = wincnn.cookToomFilter([0,1,-1,2,-2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, -9, 10, -10],
                    self.hc['TX'], self.hc['TKX'])
		MU = max([gg.denominator for gg in np.array(wino_G).reshape(-1)])
		MU_A = max([gg.denominator for gg in np.array(wino_AT).reshape(-1)])
		wino_G = np.array(MU*wino_G).astype('int')
		wino_A = np.array(wino_AT).transpose()
		wino_GT = np.array(wino_G).transpose()
		wino_B = np.array(wino_BT).transpose()
		wino_BT = np.array(wino_BT)
		wino_AT = np.array(wino_AT)
		#For a tile of :
		#TI, TN, TB
		#TX, TY, TKX, TKY
		#np.matmul(np.matmul(AT,np.matmul(np.matmul(G,W),GT)*np.matmul(np.matmul(BT,I),B)),A)
		print(wino_G, wino_GT)
		print(wino_A, wino_AT)
		print(wino_B, wino_BT)
	
	
                      		
		#np.matmul(np.matmul(AT,np.matmul(np.matmul(G,W),GT)*np.matmul(np.matmul(BT,I),B)),A)



		#G_WEI
		G_WEI = np.zeros((weights.shape[0], weights.shape[1],
			wino_G.shape[0], weights.shape[3] ))
		#for N in range(wino_G.shape[0]):
		#	for I in range(wino_G.shape[1]):
		#		G_WEI[N][I] = np.matmul(wino_G, weights[N][I])
		orig_shape = G_WEI.shape 
		G_WEI = np.matmul(wino_G, weights.reshape((-1, weights.shape[2], weights.shape[3]))	).reshape(  orig_shape)

		print(wino_G.shape, weights.shape, G_WEI.shape)
	
		#G_WEI_GT
		G_WEI_GT = np.zeros((weights.shape[0], weights.shape[1],
			wino_G.shape[0], wino_GT.shape[1] ))
		orig_shape = G_WEI_GT.shape
	
		G_WEI_GT = np.matmul(G_WEI.reshape((-1, G_WEI.shape[3])), wino_GT	).reshape(  orig_shape)
		#G_WEI_GT = np.matmul(G_WEI, wino_GT)
		
		print(wino_GT.shape, weights.shape, G_WEI_GT.shape)
	

		#B_ACT
		#for N in range(wino_G.shape[0]):
		#	for I in range(wino_G.shape[1]):
		#		G_WEI[N][I] = np.matmul(wino_G, weights[N][I])
	
		B_ACT = np.zeros((inputs.shape[0], inputs.shape[1],
			wino_B.shape[0], inputs.shape[3] ))
		orig_shape = B_ACT.shape 
		G_WEI = np.matmul(wino_G, inputs.reshape((-1, inputs.shape[2], inputs.shape[3]))	).reshape(  orig_shape)

	
		#B_ACT = np.matmul(wino_B, weights)
		#(B, I, X, Y) --> (B, I, XX, YY, TX, TY)


		#B_ACT_BT
		#B_ACT_BT =np.matmul(B_ACT, wino_BT)



		#G_WEI = np.matmul(wino_G[np.newaxis, np.newaxis, :, :], weights.reshape((weights.shape[0], weights.shape[1], -1 )).transpose(0,1,3,2))
		exit()
		#G_WEI_GT =np.matmul(G_WEI, wino_GT)
		#B_ACT = np.matmul(wino_B, weights)
		#B_ACT_BT =np.matmul(B_ACT, wino_BT)



		g_file = root+"/"+name+".g.txt"
		gt_file = root+"/"+name+".gt.txt"
		a_file = root+"/"+name+".a.txt"
		at_file = root+"/"+name+".at.txt"
		b_file = root+"/"+name+".b.txt"
		bt_file = root+"/"+name+".bt.txt"
		if(np_save):
			print(g_file)
			np.savetxt(g_file, wino_G, fmt='%d', delimiter='\n')
			np.savetxt(gt_file, wino_GT, fmt='%d', delimiter='\n')
			np.savetxt(a_file,wino_A , fmt='%d', delimiter='\n')
			np.savetxt(at_file,wino_AT, fmt='%d', delimiter='\n')
			np.savetxt(b_file, wino_B, fmt='%d', delimiter='\n')
			np.savetxt(bt_file, wino_BT, fmt='%d', delimiter='\n')

			print(g_file)
	
		GX,GY = wino_G.shape
		AX,AY = wino_A.shape
		BX,BY = wino_B.shape
		return {
			"params":{
				"IN": IN,
				"OUT": OUT,
				"BAT": BAT,	
				"FILTER_KX": KX, 
				"FILTER_KY": KY,
				"INPUT_X": X,
				"INPUT_Y": Y,


				"WINO_G": GX,
				"WINO_GT": GY,
				"WINO_B": BX,
				"WINO_BT": BY,
				"WINO_A": AX,
				"WINO_AT": AY,

			},
	"G_obj":{	
		"name": "winoG",
		"file": g_file,
		"size": len(wino_G.reshape((-1))),
		"indexing": "kx + WINO_G*ky"},

	"GT_obj":{	
		"name": "winoGT",
		"file": gt_file,
		"size": len(wino_GT.reshape((-1))),
		"indexing": "ky + WINO_GT*kx"
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
				"STRIDE": params['stride'],	
				"GROUP": "OUTER",
			},
			"Y": {
				"LIM": "INPUT_Y",
				"STRIDE": params['stride'],	
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
		results.append(self.infer_G_mapper(p))
		#results.append(self.infer_GT_mapper)
		#results.append(self.infer_B_mapper)
		#results.append(self.infer_BT_mapper)



		#if(p.get("RUN_PE",1)):
		#	results.append(self.infer_pe(p))
		#if(p.get("RUN_ADDER_ACCUM", 1)):
		#	results.append(self.infer_adder_accum(p))
		#if(p.get("RUN_BUFFERS",1)):
		#	results.append(self.infer_buffers(p))
		return results


#if __name__ == "__main2__":
		
def core(hardware_config, benchmark = {}, MODE = 0):	
	
	"""
	hardware_config = {
	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 1,
	"TN": 1,
	"TI": 1,
	"TX": 2,
	"TY": 2,
	"TKX": 3,
	"TKY": 3,
	"LOOP_ORDER": ["B", "N", "I", "X", "Y"],

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

	"INTERCONNECT_CASTING_TYPE": "Multicast_Tree",
	"INTERCONNECT_G_MAPPING_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_G_MULT_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_G_ADD_TYPE": "Simple",#Simple, Buffered


	"INTERCONNECT_GT_MAPPING_TYPE": "Simple",
	"INTERCONNECT_GT_MAPPING_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_GT_MULT_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_GT_ADD_TYPE": "Simple",#Simple, Buffered


	"INTERCONNECT_B_MAPPING_TYPE": "Simple",
	"INTERCONNECT_BT_MAPPING_TYPE": "Simple",
	"INTERCONNECT_A_MAPPING_TYPE": "Simple",
	"INTERCONNECT_AT_MAPPING_TYPE": "Simple",
	
	
	"CLOCK": 1,
	"cap_load": 0.1,
	"tech":"tsmc40",

	}

	input_data = paddle.randn([4, 3, 224, 224])
	layer = nn.Conv2D(in_channels=3, out_channels=64, kernel_size=3)#skip bias for now
	output_data = layer(input_data) 	

	network_layer = {
	"layer_name": "Conv1",
	"layer": layer,
	"input_data": input_data,
	"output_data": output_data,
	}
	mapping = {
	"Linear1": "df1",
	}

	design = dict_to_str(hardware_config)

	SIM_PARAMS = {
	"name": network_layer['layer_name'],
	"root": f"generated/Arch/WinogradConv/{design}",
	"SIM_CYCLES": 10,
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
	'MODE': 3,
	"RUN_GOLDEN_SBT": 1,
	
	#'GEN_TRACE':True,
	'RUN_CPP': True
}
	SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])

	"""

	SIM_PARAMS = benchmark["SIM_PARAMS"]


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
	elif(SIM_PARAMS['MODE'] == 3):	
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = True
	
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
	SIM_PARAMS["root"] = f"generated/Arch/WinogradConv/{design}"	
	SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])


	#FLOW 1. compare against baselines and 
	ld =  WinogradConv(hardware_config)
	traces = ld.gen_perf_trace(network_layer,mapping, SIM_PARAMS) 
	#exit()
	ld.estimate_golden_pwr(traces, network_layer,mapping, SIM_PARAMS)
#	ld.estimate_our_pwr_v1(traces,network_layer,mapping, SIM_PARAMS)	
#	ld.estimate_our_pwr(traces,network_layer,mapping, SIM_PARAMS)
#	ld.estimate_b1_pwr(traces,network_layer, mapping,SIM_PARAMS)#maestro
#	ld.estimate_b2_pwr(traces, network_layer,mapping,SIM_PARAMS)#accelergy 
#	ld.estimate_b3_pwr(traces, network_layer,mapping,SIM_PARAMS)#others?



if __name__ == "__main__":
	import sys	
	MODE = int(sys.argv[-2]	)
	JUST_DEFAULT = int(sys.argv[-1])

	base_hardware_config = {
	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 1,
	"TN": 1,
	"TI": 1,
	"TX": 2,
	"TY": 2,
	"TKX": 3,
	"TKY": 3,
	"LOOP_ORDER": ["B", "N", "I", "X", "Y"],

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

	"INTERCONNECT_CASTING_TYPE": "Multicast_Tree",
	"INTERCONNECT_G_MAPPING_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_G_MULT_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_G_ADD_TYPE": "Simple",#Simple, Buffered


	"INTERCONNECT_GT_MAPPING_TYPE": "Simple",
	"INTERCONNECT_GT_MAPPING_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_GT_MULT_TYPE": "Simple",#Simple, Buffered
	"INTERCONNECT_GT_ADD_TYPE": "Simple",#Simple, Buffered


	"INTERCONNECT_B_MAPPING_TYPE": "Simple",
	"INTERCONNECT_BT_MAPPING_TYPE": "Simple",
	"INTERCONNECT_A_MAPPING_TYPE": "Simple",
	"INTERCONNECT_AT_MAPPING_TYPE": "Simple",
	
	
	"CLOCK": 1,
	"cap_load": 0.1,
	"tech":"tsmc40",

	}

	in_channels = 16
	input_data = paddle.randn([4, in_channels, 224, 224])
	layer = nn.Conv2D(in_channels=in_channels, out_channels=64, kernel_size=3)#skip bias for now
	output_data = layer(input_data) 	

	base_network_layer = {
	"layer_name": "Conv1",
	"layer": layer,
	"input_data": input_data,
	"output_data": output_data,
	}
	base_mapping = {
	"ConvWino1": "df1",
	}

	design = dict_to_str(base_hardware_config)

	base_SIM_PARAMS = {
	"name": base_network_layer['layer_name'],
	"root": f"generated/Arch/WinogradConv/{design}",
	"SIM_CYCLES": 10,
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
	'MODE': MODE,
	"RUN_GOLDEN_SBT": 1,
	
	#'GEN_TRACE':True,
	'RUN_CPP': True
}
	SIM_PARAMS = base_SIM_PARAMS
	base_SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])




	#define hardware_configs
	combos = []

	for wei_prec in [8, 16]:
		for act_prec in [8, 16]:	
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
					["B", "N", "I", "X", "Y", "KX", "KY"],
					["B", "N", "I", "KX", "KY", "X", "Y"],
					["B", "N", "Y", "X", "I", "KX", "KY"],
					["B", "Y", "X", "KY", "KX", "I", "N"],
					["KY", "KX", "I", "X", "Y", "B", "N"],
					["I", "N", "KX", "KY", "Y", "X", "B"],
				       ]:
					if True:	
						if True:
							hc = dict(base_hardware_config)
							hc["TB"] =  tb
							hc["TI"] =  ti
							hc["TN"] =  tn
							hc["TX"] =  tx
							hc["TY"] =  ty
							hc["TKX"] =  tkx
							hc["TKY"] =  tky		
							hc["LOOP_ORDER"] = lp
							hc["WEI_PREC"] = wei_prec
							hc["ACT_PREC"] = act_prec
							combos.append(hc)							

	benchmarks = []

	
	for Wei_Sparsity in [0.1, 0.8]:
		for Act_Sparsity in [0.1 ,0.8]:	
			for batch, in_channels, out_channels, kernel_size, stride, X, Y in [
			     [4    ,   32,         64,            3,         1,    32, 64],
         	             [4    ,   3,         64,            5,         2,    32, 64],
			     [4    ,   64,         64,            3,         2,    32, 64],
		   	     [4    ,   8,         8,            3,         1,    32, 32],
			     [4    ,   32,         32,            7,         1,    32, 32],
			     [4    ,   8,         16,            5,         1,    16, 32],	
	
			]:	

				for SIM_CYCLES in [10, 100]:
					
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
	

	if(JUST_DEFAULT):
		combos = [base_hardware_config]
		benchmarks = [ {
		'SIM_PARAMS': base_SIM_PARAMS,
		'network_layer': base_network_layer,
		'mapping': base_mapping
			}]
	
	tested = 0
	for inputs in combos:
		for benchmark in benchmarks:
			core(inputs, benchmark, MODE)	
		tested += 1



