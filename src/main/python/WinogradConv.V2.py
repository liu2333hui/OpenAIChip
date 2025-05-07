from ArchTemplates import GeneralConvUnit, GeneralLinearUnit, generate_cpp, dict_to_str, filter_loop_order
import copy

from SystolicConv import SystolicConv, core

import numpy as np
import paddle.nn as nn
import paddle
import pandas as pd

from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
#from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive
from ArchTemplates import GeneralConvUnit, GeneralLinearUnit, generate_cpp, dict_to_str,filter_loop_order, MultiplierComponent, NetworkComponent, MemoryComponent, AdderAccumulateComponent



#Systolic + WinogradConvolution
class WinogradConv(SystolicConv):
	def get_primitive_statistics(self, hc):
		
		super().get_primitive_statistics(hc)	

		#add new somi tilings for the inner products mapping
		self.hc["TG"] = self.hc["TX"] + self.hc["TKX"] - 1
		self.hc["TGT"] = self.hc["TY"] + self.hc["TKY"] - 1

		self.hc["TB"] = self.hc["TX"] + self.hc["TKX"] - 1
		self.hc["TBT"] = self.hc["TY"] + self.hc["TKY"] - 1

		self.hc["TA"] = self.hc["TX"] + self.hc["TKX"] - 1
		self.hc["TAT"] = self.hc["TY"] + self.hc["TKY"] - 1



		net = hc["VALID_NETS"]

		'''
		if("OUT_WINO_AT_MULT" in net):
		if("OUT_WINO_AT_ADD" in net):

		if("OUT_WINO_A_MULT" in net):
		if("OUT_WINO_A_ADD" in net):
	

		if("ACT_WINO_BT_MULT" in net):
		if("ACT_WINO_BT_ADD" in net):


		if("ACT_WINO_B_MULT" in net):
		if("ACT_WINO_B_ADD" in net):

		if("ACT_WINO_BT_MULT" in net):
		if("ACT_WINO_BT_ADD" in net):

		if("WEI_WINO_GT_MULT" in net):
		if("WEI_WINO_GT_ADD" in net):
		'''
	
		#WEI_WINO_G_MULT
		LOOP_VAR_DEFINITIONS = {
			"N": {"LIM": "OUT","STRIDE": 1,"GROUP": "OUTER"},
			"I": {"LIM": "IN" ,"STRIDE": 1, "GROUP": "OUTER"},
			"KX":{"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "INNER"},
			"G":{"LIM": "WINO_G", "STRIDE": 1, "GROUP": "OUTER"},
			"KY":{"LIM": "FILTER_KY","STRIDE":1,"GROUP": "OUTER"},
			"B": {"LIM": "BAT","STRIDE": 1,"GROUP": "OUTER"},
			"X": {"LIM": "INPUT_X","STRIDE": 1,"GROUP": "OUTER"},
			"Y": {"LIM": "INPUT_Y","STRIDE": 1,"GROUP": "OUTER"},
			"KX": {"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "OUTER"},
			"KY": {"LIM": "FILTER_KY","STRIDE": 1,"GROUP": "OUTER"},
		}
		self.LOOP_VAR_DEFINITIONS = {
			"N": {"LIM": "OUT","STRIDE": 1,"GROUP": "OUTER"},
			"I": {"LIM": "IN" ,"STRIDE": 1, "GROUP": "OUTER"},
			"KX":{"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "INNER"},
			"G":{"LIM": "WINO_G", "STRIDE": 1, "GROUP": "OUTER"},
			"KY":{"LIM": "FILTER_KY","STRIDE":1,"GROUP": "OUTER"},
			"B": {"LIM": "BAT","STRIDE": 1,"GROUP": "OUTER"},
			"X": {"LIM": "INPUT_X","STRIDE": 1,"GROUP": "OUTER"},
			"Y": {"LIM": "INPUT_Y","STRIDE": 1,"GROUP": "OUTER"},
			"KX": {"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "OUTER"},
			"KY": {"LIM": "FILTER_KY","STRIDE": 1,"GROUP": "OUTER"},
		}
		loop_order = self.hc["LOOP_ORDER"] + ["KX", "KY", "G"]
		TILE = self.hc["TN"]*self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]*self.hc["TG"]   *self.hc["TB"]*self.hc["TX"]*self.hc["TY"]

		#WEIGHT TRANSFORM
		#NetworkComponent(net, self, "WEI_WINO_G_MULT", loop_order = loop_order, units = TILE, bins = ['weights_data', 'winoG_data'], main = "weight", wei_prec = "WEI_PREC", act_prec = "WEI_PREC", data_obj = ["weights_obj", "winoG_obj"], runtime_lambda = lambda p : MAC_NO // p['avg_cycle_per_op'] )

		MultiplierComponent(net, self, "WEI_WINO_G_MULT", loop_order = loop_order, units = TILE, bins = ['weights_data', 'winoG_data'], main = "weight", wei_prec = "IN_PREC", act_prec = "IN_PREC", data_obj = ["weights_obj", "G_obj"], runtime_lambda = lambda p : MAC_NO // p['avg_cycle_per_op'], cast_skips = ["TB", "TX", "TY"] )

		AdderAccumulateComponent(ADDER_TYPE = "ADDER_TREE", valid_nets=net, self=self, unit_name="WEI_WINO_G_ADD", loop_order = loop_order, cast_skips = ["TB", "TX", "TY"], units = self.hc["TN"]*self.hc["TI"]*self.hc["TKY"]*self.hc["TG"], input_group = self.hc["TKX"], bins = [], prec = "IN_PREC", data_obj = ["weights_obj", "G_obj"], update = "weights_data*winoG_data",  out_prec = "OUT_PREC", loop_var = LOOP_VAR_DEFINITIONS)

		#Broadcast Network

		MultiplierComponent(net, self, "WEI_WINO_GT_MULT", loop_order = loop_order, units = TILE, bins = ['G_WEI_data', 'GT_data'], main = "weight", wei_prec = "IN_PREC", act_prec = "IN_PREC", data_obj = ["weights_obj", "G_obj"], runtime_lambda = lambda p : MAC_NO // p['avg_cycle_per_op'], cast_skips = ["TB", "TX", "TY"] )

		AdderAccumulateComponent(ADDER_TYPE = "ADDER_TREE", valid_nets=net, self=self, unit_name="WEI_WINO_GT_ADD", loop_order = self.hc["LOOP_ORDER"], cast_skips = ["TB", "TX", "TY"], units = self.hc["TN"]*self.hc["TI"]*self.hc["TKY"]*self.hc["TG"], input_group = self.hc["TKX"], bins = [], prec = "PREC", data_obj = ["weights_obj", "G_obj"], update = "weights_data*winoG_data",  out_prec = "OUT_PREC")



		print(self.MODULES)

		#ACT_WINO_B_MULT
		#MultiplierComponent(net, self, "ACT_WINO_B_MULT", loop_order = self.hc["LOOP_ORDER"], units = self.hc["TN"]*self.hc["TI"]*self.hc["TX"]*self.hc["TY"]*self.hc["TG"], bins = ['weights_data', 'winoG_data'], main = "weight", wei_prec = "WEI_PREC", act_prec = "WEI_PREC", data_obj = ["weights_obj", "G_obj"], runtime_lambda = lambda p : MAC_NO // p['avg_cycle_per_op'] )
	
			

	def prepare_data(self, params):
		#convolution data

		self.hc["TG"] = self.hc["TX"] + self.hc["TKX"] - 1
		self.hc["TGT"] = self.hc["TY"] + self.hc["TKY"] - 1

		self.hc["TB"] = self.hc["TX"] + self.hc["TKX"] - 1
		self.hc["TBT"] = self.hc["TY"] + self.hc["TKY"] - 1


		input_data = params['input_data']
		weights = params['weight']
		output_data = params['out_data']



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
		WEI_PREC = self.hc.get('WEI_PREC', self.hc.get("PREC",8))
		ACT_PREC = self.hc.get('ACT_PREC', self.hc.get("PREC",8))
		OUT_PREC = self.hc.get('OUT_PREC', self.hc.get("PREC",8))




		#if(np_save):
		weights    = ((weights*256*256) %WEI_PREC).astype(np.int32)
		input_data = ((input_data*256*256) %ACT_PREC).astype(np.int32)
		output_data = ((output_data*256*256) %OUT_PREC).astype(np.int32)



		#Randomize weights and inputs (TODOS)
		Randomize = params["SIM_PARAMS"]["Randomize"]
		Wei_Sparsity = params["SIM_PARAMS"]["Wei_Sparsity"]
		Act_Sparsity = params["SIM_PARAMS"]["Act_Sparsity"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]

		np_save= params['SIM_PARAMS']['save_np']
	

		#Randomize weights and inputs (TODOS)
		if(Randomize ):
			n = IN*OUT*KX*KY
	
			k = int(n*Wei_Sparsity)
			rand_wei = np.random.randint(0, 1<< WEI_PREC, size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_wei[zero_indices] = 0
			
			n = IN*BAT*X*Y
	
			k = int(n*Act_Sparsity)
			rand_act = np.random.randint(0, 1<<ACT_PREC, size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_act[zero_indices] = 0


			weights = rand_wei.reshape((OUT, IN, KX, KY))
			input_data = rand_act.reshape((BAT, IN, X, Y))
			n = OUT*BAT*X*Y
	
			k = int(n*max(Act_Sparsity, Wei_Sparsity))
			rand_out = np.random.randint(0, 1<<ACT_PREC, size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_out[zero_indices] = 0

			output_data = rand_out.reshape((BAT, OUT, X, Y))



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
		print("WINO_B", wino_B, wino_BT)
	
	
                      		
		#np.matmul(np.matmul(AT,np.matmul(np.matmul(G,W),GT)*np.matmul(np.matmul(BT,I),B)),A)



		#G_WEI
		G_WEI = np.zeros((weights.shape[0], weights.shape[1],
			wino_G.shape[0], weights.shape[3] ))
		#for N in range(wino_G.shape[0]):
		#	for I in range(wino_G.shape[1]):
		#		G_WEI[N][I] = np.matmul(wino_G, weights[N][I])
		orig_shape = G_WEI.shape 
		if(np_save):	
			G_WEI = np.matmul(wino_G, weights.reshape((-1, weights.shape[2], weights.shape[3]))	).reshape(  orig_shape)

		print(wino_G.shape, weights.shape, G_WEI.shape)
	
		#G_WEI_GT

		G_WEI_GT = np.zeros((weights.shape[0], weights.shape[1],
			wino_G.shape[0], wino_GT.shape[1] ))
		orig_shape = G_WEI_GT.shape
	

		if(np_save):	
			G_WEI_GT = np.matmul(G_WEI.reshape((-1, G_WEI.shape[3])), wino_GT	).reshape(  orig_shape)
		#G_WEI_GT = np.matmul(G_WEI, wino_GT)
		
		print(wino_GT.shape, weights.shape, G_WEI_GT.shape)
	

		#B_ACT
		#for N in range(wino_G.shape[0]):
		#	for I in range(wino_G.shape[1]):
		#		G_WEI[N][I] = np.matmul(wino_G, weights[N][I])
	
		inputs = input_data
		INPUT_REFORMED = input_data.reshape((
			inputs.shape[0], inputs.shape[1], 
			inputs.shape[2] //(self.hc["TB"])  , inputs.shape[3] //self.hc["TBT"] ,
			self.hc["TB"]      , self.hc["TBT"]
		  ))


		B_ACT = np.zeros((INPUT_REFORMED.shape)) 

		#np.zeros((inputs.shape[0], inputs.shape[1],
		#inputs.shape[0], inputs.shape[3] ))
		#orig_shape = B_ACT.shape 
		orig_shape = B_ACT.shape 

		if(np_save):	
			B_ACT = np.matmul(wino_B, INPUT_REFORMED.reshape((-1, INPUT_REFORMED.shape[-2], INPUT_REFORMED.shape[-1]))	).reshape(  orig_shape)


		B_ACT_BT = np.zeros((INPUT_REFORMED.shape)) #np.zeros((weights.shape[0], weights.shape[1],
			#wino_G.shape[0], wino_GT.shape[1] ))

		print(B_ACT.shape, B_ACT_BT.shape)
		print(G_WEI.shape, G_WEI_GT.shape)
	
		orig_shape = B_ACT_BT.shape
	
		if(np_save):
			B_ACT_BT = np.matmul(B_ACT.reshape((-1, B_ACT.shape[-1])), wino_BT	).reshape(  orig_shape)



		print(B_ACT.shape, B_ACT_BT.shape)
		print(G_WEI.shape, G_WEI_GT.shape)
		#input("OK?")



		#OUTPUT MAPPING
		#very tricky to do , because the psums can be huge.
		#we only model the A_PE layer and assume the cost is doubled

	
		#B_ACT, B_ACT_BT, G_WEI, G_WEI_GT

		#B_ACT = np.matmul(wino_B, weights)
		#(B, I, X, Y) --> (B, I, XX, YY, TX, TY)


		#B_ACT_BT
		#B_ACT_BT =np.matmul(B_ACT, wino_BT)



		#G_WEI = np.matmul(wino_G[np.newaxis, np.newaxis, :, :], weights.reshape((weights.shape[0], weights.shape[1], -1 )).transpose(0,1,3,2))
		#G_WEI_GT =np.matmul(G_WEI, wino_GT)
		#B_ACT = np.matmul(wino_B, weights)
		#B_ACT_BT =np.matmul(B_ACT, wino_BT)


		w_file = root+"/"+name+".weights.txt"
		i_file = root+"/"+name+".input.txt"
		o_file = root+"/"+name+".output.txt"

		if(np_save):
			weights = rand_wei.reshape((-1))#OUT, IN, KX, KY))
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))
			output_data = rand_out.reshape((-1))
	
			np.savetxt(w_file, weights, fmt='%d', delimiter='\n')
			np.savetxt(i_file, input_data, fmt='%d', delimiter='\n')
			weights = rand_wei.reshape((-1))#OUT, IN, KX, KY))
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))

			np.savetxt(o_file, output_data, fmt='%d', delimiter='\n')
			#output_data = rand_out.reshape((-1))#OUT, IN, KX, KY))
	
	
			weights = rand_wei.reshape((OUT, IN, KX, KY))
			input_data = rand_act.reshape((BAT, IN, X, Y))



		g_file = root+"/"+name+".g.txt"
		gt_file = root+"/"+name+".gt.txt"
		a_file = root+"/"+name+".a.txt"
		at_file = root+"/"+name+".at.txt"
		b_file = root+"/"+name+".b.txt"
		bt_file = root+"/"+name+".bt.txt"

		g_wei_file = root+"/"+name+".g_wei.txt"
		g_wei_gt_file = root+"/"+name+".g_wei_gt.txt"
		b_act_file = root+"/"+name+".b_act.txt"
		b_act_bt_file = root+"/"+name+".b_act_bt.txt"



		GX,GY = wino_G.shape
		AX,AY = wino_A.shape
		BX,BY = wino_B.shape
	

		if(np_save):
			wino_G = wino_G.reshape((-1))#OUT, IN, KX, KY))
			wino_GT= wino_GT.reshape((-1))#BAT, IN, X, Y))
			wino_A = wino_A.reshape((-1))
			wino_AT = wino_AT.reshape((-1))
			wino_B = wino_B.reshape((-1))
			wino_BT = wino_BT.reshape((-1))
		
			G_WEI = G_WEI.reshape((-1))
			G_WEI_GT = G_WEI_GT.reshape((-1))
			B_ACT = B_ACT.reshape((-1))
			B_ACT_BT =B_ACT_BT.reshape((-1))
	
	
			np.savetxt(g_file, wino_G, fmt='%d', delimiter='\n')
			np.savetxt(gt_file, wino_GT, fmt='%d', delimiter='\n')
			np.savetxt(a_file,wino_A , fmt='%d', delimiter='\n')
			np.savetxt(at_file,wino_AT, fmt='%d', delimiter='\n')
			np.savetxt(b_file, wino_B, fmt='%d', delimiter='\n')
			np.savetxt(bt_file, wino_BT, fmt='%d', delimiter='\n')

			np.savetxt(g_wei_file, G_WEI , fmt='%d', delimiter='\n')
			np.savetxt(g_wei_gt_file, G_WEI_GT , fmt='%d', delimiter='\n')
			np.savetxt(b_act_file, B_ACT, fmt='%d', delimiter='\n')
			np.savetxt(b_act_bt_file, B_ACT_BT, fmt='%d', delimiter='\n')

		self.LOOP_VAR_DEFINITIONS = {
			"N": {"LIM": "OUT","STRIDE": 1,"GROUP": "INNER"},
			"I": {"LIM": "IN" ,"STRIDE": 1, "GROUP": "INNER"},
			"KX":{"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "INNER"},
			"G":{"LIM": "WINO_G", "STRIDE": 1, "GROUP": "INNER"},
			"GT":{"LIM": "WINO_GT", "STRIDE": 1, "GROUP": "INNER"},
			"B":{"LIM": "WINO_B", "STRIDE": 1, "GROUP": "INNER"},
			"BT":{"LIM": "WINO_BT", "STRIDE": 1, "GROUP": "INNER"},
			"A":{"LIM": "WINO_A", "STRIDE": 1, "GROUP": "INNER"},
			"AT":{"LIM": "WINO_AT", "STRIDE": 1, "GROUP": "INNER"},

			"KY":{"LIM": "FILTER_KY","STRIDE":1,"GROUP": "INNER"},
			"B": {"LIM": "BAT","STRIDE": 1,"GROUP": "INNER"},
			"X": {"LIM": "INPUT_X","STRIDE": 1,"GROUP": "INNER"},
			"Y": {"LIM": "INPUT_Y","STRIDE": 1,"GROUP": "INNER"},
			"KX": {"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "INNER"},
			"KY": {"LIM": "FILTER_KY","STRIDE": 1,"GROUP": "INNER"},
		}

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

		#G_WEI_GT = np.zeros((weights.shape[0], weights.shape[1],
		#	wino_G.shape[0], wino_GT.shape[1] ))
		#orig_shape = G_WEI_GT.shape	
		#G_WEI_GT = np.matmul(G_WEI.reshape((-1, G_WEI.shape[3])), wino_GT	).reshape(  orig_shape)
	
		"G_WEI_obj": {
			"name": "winoG_WEI",
			"file": g_wei_file,
			"size": len(G_WEI_GT.reshape((-1))),
			"indexing": "kx + WINO_G*ky"	
		},
		"G_WEI_GT_obj": {
			"name": "winoG_WEI",
			"file": g_wei_gt_file,
			"size": len(G_WEI_GT.reshape((-1))),
			"indexing": "kx + WINO_G*ky"	
		},

		"G_obj":{	
			"name": "winoG",
			"file": g_file,
			"size": len(wino_G.reshape((-1))),
			"indexing": "kx + WINO_G*ky"
			},

		"GT_obj":{	
			"name": "winoGT",
			"file": gt_file,
			"size": len(wino_GT.reshape((-1))),
			"indexing": "ky + WINO_GT*kx"
		},
		"weights_obj":	{
				"name": "weights",
				"file": w_file,
				"size": len(weights.reshape((-1))),
				"indexing": "n*IN*FILTER_KX*FILTER_KY+i*FILTER_KX*FILTER_KY+ky*FILTER_KX+kx"
		},
		"inputs_obj":{
				"name": "inputs",
				"file": i_file,
				"size": len(input_data.reshape((-1))),
				"indexing": "b*IN*INPUT_X*INPUT_Y+i*INPUT_X*INPUT_Y + y*INPUT_X + x"	
		},
	}
		

	




#THe experiment where we compare our power model against baselines
def run_wino_fig6(base_hardware_config, base_mapping, base_network_layer, base_SIM_PARAMS, VALID_UNITS):

	#test cases
	combos = []
	
	big_loop = -1
	BIG_LOOP_SAMPLE = 1000
	for lp in [ 
					["B", "N", "I", "X", "Y"],
					["B", "N", "Y", "X", "I",],
					["B", "Y", "X",  "I", "N"],
					["B", "Y", "X", "N", "I"],	
					[ "I", "X", "Y", "B", "N"],
					["I", "N", "Y", "X", "B"],
	
				       ]:
			


		for     tb,tn,  ti,tx, ty,tkx,tky in [
			#64 pe case
		[1, 1,   2,2,  2,  3,3],
		[1, 2,   1,2,  2,  3,3],
		[1, 2,   2,2,  2,  3,3],
		[1, 4,   1,2,  2,  3,3],
		[1, 1,   4,2,  2,  3,3],
	
	
	
		[1, 1,   1,3,  3,  3,3],
 		[1, 1,   1,4,  4,  3,3],

 
		#	[1,16,  16,1,  1,  1,1],
        	#	[1,8,  8,1,  1,  2,2],
        	#	[1,8,  8,1,  2,  1,2],	
        	#	[1,16,  4,1,  2,  1,2],	
        		#	[1,4,  16,2,  2,  1,2],			
        		#	[2,4,  8,2,  2,  1,1],			
	       		#	[2,2,  16,2,  2,  1,1],			
	       		#	[1,8,  32,1,  1,  1,1],			
				]:
		
			big_loop = big_loop +1
			if(big_loop > BIG_LOOP_SAMPLE):
				continue

			#hc = dict(base_hardware_config)
			hc = copy.deepcopy(base_hardware_config)	
	
			hc["GENERAL"]["TB"] =  tb
			hc["GENERAL"]["TI"] =  ti
			hc["GENERAL"]["TN"] =  tn
			hc["GENERAL"]["TX"] =  tx
			hc["GENERAL"]["TY"] =  ty
			hc["GENERAL"]["TKX"] =  tkx
			hc["GENERAL"]["TKY"] =  tky		
			hc["GENERAL"]["LOOP_ORDER"] = lp
			#print(hc)
			#if(big_loop > 0):
			#print(combos[0])

			#NAIVE would have had total of 16 x 16 x 14 x 14 x 80 = 4,014,080  4 million already!
			#with 8 x 8 = 64 OUTER combinations --> 256 million !
			# Total Combos = 16 + 16 + 14 + 14 + 80 = 140
			#with outer combinations --> 140 
			# Total Combos = 8960 only, much better
				
			#WEI_LOADER variations
			# 2 x 4 x 2 = 16
			Flag = False
			sample = 0
			unit = "WEI_LOADER"
			SAMPLE = 10

			if(unit in VALID_UNITS):
				for wei_network in ["Mux", "Shift"]:
					for load_ratio in [-4,-2,1,2, 4]:
						for wei_prec in [8, 16]:
							if(Flag):
								continue

							h = copy.deepcopy(hc)	
	
							if(load_ratio > 0 and wei_prec*ti*tn*tkx*tky < load_ratio*h[unit]["L1_WEI_SRAM_SIZE"][0]):
								continue	
							#h = dict(hc)	
							#h = copy.deepcopy(hc)	
	

							h[unit]["PREC"] = wei_prec
							h[unit]["NETWORK_TYPE"] = wei_network
							h[unit]["LOAD_RATIO"] = load_ratio
							h["VALID_UNITS"] = [unit]#hc[unit]["VALID_UNITS"]		
					
							h["VALID_NETS"] = hc[unit]["VALID_NETS"]

							combos.append(h)							
							#print("WEI_LOADER")
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True


			#OUT_LOADER variations
			# 2 x 4 x 2 = 16
			Flag = False
			sample = 0
			unit = "OUT_LOADER"
			SAMPLE = 3

			if(unit in VALID_UNITS):
				for wei_network in ["Mux", "Shift"]:
					for load_ratio in [-4, -2, 1,2, 4]:
						for wei_prec in [8, 16]:
							if(Flag):
								continue

							if(load_ratio > 0 and wei_prec*tb*tn*tx*ty < load_ratio*h[unit]["L1_OUT_SRAM_SIZE"][0]):
								continue
							#h = dict(hc)	
							h = copy.deepcopy(hc)	
	

							h[unit]["PREC"] = wei_prec
							h[unit]["NETWORK_TYPE"] = wei_network
							h[unit]["LOAD_RATIO"] = load_ratio
							h["VALID_UNITS"] = [unit]#hc[unit]["VALID_UNITS"]		
					
							h["VALID_NETS"] = hc[unit]["VALID_NETS"]

							combos.append(h)							
							#print("WEI_LOADER")
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True




			'''
			print("COMBOS",len(combos))
			for idx,c in enumerate(combos):
				#print(c)
				VU = c["VALID_UNITS"]
				print(idx, VU)
			'''


			#ACT_LOADER variations
			#16
			Flag = False
			sample = 0
			unit = "ACT_LOADER"
			SAMPLE = 10

			if(unit in VALID_UNITS):			
				for act_network in ["Mux", "Shift"]:
					for load_ratio in [-4,-2, 1,2, 4]:
						for act_prec in [8, 16]:
							if(Flag):
								continue

							if(load_ratio > 0 and act_prec*ti*tb*(tx+tkx-1)*(ty+tky-1) < load_ratio*h[unit]["L1_ACT_SRAM_SIZE"][0]):
	
								continue
							#h = dict(hc)	
							h = copy.deepcopy(hc)	
	

	
							h[unit]["PREC"] = act_prec
							h[unit]["NETWORK_TYPE"] = act_network
							h[unit]["LOAD_RATIO"] = load_ratio	
							h["VALID_UNITS"] = [unit]#hc[unit]["VALID_UNITS"]		
	
							h["VALID_NETS"] = h[unit]["VALID_NETS"]
							combos.append(h)							
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True

			'''
			print("COMBOS",len(combos))
			for idx,c in enumerate(combos):
				print("keys",c.keys())
				VU = c["VALID_UNITS"]
				#print(idx, VU, VALID_UNITS)
			'''



			#OUT_LOADER variations (todos)
						

			#WEI_PE_CAST	
			#2 x 7 = 14
			Flag = False
			sample = 0
			unit = "WEI_PE_CAST"
			SAMPLE = 10
			if(unit in VALID_UNITS):	
				for wei_prec in [8, 16]:
					for ratio in [1, 2, 4, 8, 16, 32, 64]:
						for network in ["Mux", "Shift"]:
	
							if(Flag):
								continue
	
							if(tb*tx*ty < ratio):
								continue
							#h = dict(hc)	
							h = copy.deepcopy(hc)	
	

		
							h["VALID_UNITS"] = [unit]#h[unit]["VALID_UNITS"]		
	
							h[unit]["PREC"] =wei_prec
							h[unit]["CAST_RATIO"] =ratio	
							h[unit]["NETWORK_TYPE"] = network

							h["VALID_NETS"] = h[unit]["VALID_NETS"]
							combos.append(h)							
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True	
						
			#ACT_PE_CAST
			#2 x 7 = 14
			Flag = False
			sample = 0
			unit = "ACT_PE_CAST"
			SAMPLE = 10
			if(unit in VALID_UNITS):
				for prec in [8, 16]:
					for ratio in [1, 2, 4, 8, 16, 32, 64]:
						for network in ["Mux", "Shift"]:
	
							if(Flag):
								continue
	
							if(tb*tx*ty < ratio):
								continue
							h = copy.deepcopy(hc)	
	

							#h = dict(hc)	
		
							h["VALID_NETS"] = h[unit]["VALID_NETS"]		
							h["VALID_UNITS"] = [unit]#h[unit]["VALID_UNITS"]			
	
							h[unit]["PREC"] = prec
							h[unit]["CAST_RATIO"] = ratio	
							combos.append(h)							
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True	
	
												
			#L2 variations (todos)
			Flag = False
			sample = 0
			unit = "ADDER_TREE"
			SAMPLE = 10
			if(unit in VALID_UNITS):
				for prec in [16 ]:
					for out_prec in [32]:
						for core_adder_type in ["RCAAdder2"]:
							for addern_type in ["AddTreeN"]:
		
								if(Flag):
									continue
	
								h = copy.deepcopy(hc)	
	
								h["VALID_NETS"] = h[unit]["VALID_NETS"]		
								h["VALID_UNITS"] = [unit]#h[unit]["VALID_UNITS"]			
	
								h[unit]["OUT_PREC"] = out_prec
	
								h[unit]["PREC"] = prec
								h[unit]["ADDERN_TYPE"] = addern_type
								h[unit]["CORE_ADDER_TYPE"] = core_adder_type



								combos.append(h)							
								sample = sample + 1
								if( sample >= SAMPLE):
									Flag = True	
	
	
			#PE Array variations
			#2 x 2 x 5 x (1 + 3) = 80
			for unit in ["PE_ARRAY", "WEI_WINO_G", "WEI_WINO_GT", "ACT_WINO_B", "ACT_WINO_BT", "OUT_WINO", "OUT_WINO_AT"]:
				
				Flag = False
				sample = 0
				#unit = "PE_ARRAY"
				SAMPLE = 20			
				hc["VALID_UNITS"] = [unit]#hc[unit]["VALID_UNITS"]		
				if(unit in VALID_UNITS):
					for wei_prec in [8, 16]:
						for act_prec in [8, 16]:
							for radix_root in [1, 2, 4, 8, 16]:
								radix = 1<<radix_root
								if(radix_root > wei_prec or radix_root > act_prec):	
									continue
	
								for mult_type in ["ConstantMultiplier", "HighRadixMultiplier", "BitSerialMultiplier"]:	
									if(Flag):
										continue
		
									if(mult_type == "BitSerialMultiplier"):	
										for side in ['weights', 'acts', 'both']:
											if(Flag):
												continue
		
											h = copy.deepcopy(hc)	
											h[unit]["WEI_PREC"] = wei_prec
											h[unit]["ACT_PREC"] = act_prec
											h[unit]["RADIX"] = radix
											h[unit]["MULT_TYPE"] =  mult_type
											h[unit]["SIDE"] = side		
			
											h["VALID_NETS"] = h[unit]["VALID_NETS"]		
											h["VALID_UNITS"] = [unit]#h[unit]["VALID_UNITS"]			
		
											combos.append(h)							
											sample = sample + 1

											if( sample >= SAMPLE):
												Flag = True	
	
									elif(mult_type == "ConstantMultiplier"):	
										h = copy.deepcopy(hc)	
	
										h[unit]["WEI_PREC"] = wei_prec
										h[unit]["ACT_PREC"] = act_prec
										h[unit]["RADIX"] = radix
										h[unit]["MULT_TYPE"] =  mult_type
	
										combos.append(h)												
										sample = sample + 1
	
										if( sample >= SAMPLE):
											Flag = True	
	

									elif(mult_type == "HighRadixMultiplier"):	
										h = copy.deepcopy(hc)	
	
										h[unit]["WEI_PREC"] = wei_prec
										h[unit]["ACT_PREC"] = act_prec
										h[unit]["RADIX"] = radix
										h[unit]["MULT_TYPE"] =  mult_type
	
										combos.append(h)												
										sample = sample + 1
										if( sample >= SAMPLE):
											Flag = True	
										
	#print(combos)
	NUM = int(sys.argv[-1])
	
	for idx,c in enumerate(combos):
		#print(c)
		VU = c["VALID_UNITS"]
		print(idx, c["GENERAL"])
		print(idx,VU)

		for kk in c:
			if(kk in VALID_UNITS):
				print(idx,c[kk])
				pass

		#if(idx > NUM):
		#exit()

	if("DEBUG" in MODE):
		input("COMBOS OK?")	

	benchmarks = []
	
	for Wei_Sparsity in [0.1, 0.8]:
		for Act_Sparsity in [0.1 ,0.8]:	
			for batch, in_channels, out_channels, kernel_size, stride, X, Y in [
			     #[4    ,   32,         64,            3,         1,    32, 64],
#         	             [4    ,   3,         64,            7,         2,    32, 64],
			     #[4    ,   64,         64,            5,         2,    32, 64],
		   	     [4    ,   64,         64,            3,         1,    32, 32],
			     #[4    ,   32,         32,            1,         1,    32, 32],
			     #[4    ,   8,         16,            1,         1,    16, 32],	
	
			]:	

				for SIM_CYCLES in [100]:#, 100]:
					
					benchmark = {
									'SIM_PARAMS': dict(base_SIM_PARAMS),
									'network_layer': dict(base_network_layer),
									'mapping': dict(base_mapping)
								}
		
					benchmark["SIM_PARAMS"]["Randomize"] = 1
					benchmark["SIM_PARAMS"]["Wei_Sparsity"] = Wei_Sparsity
					benchmark["SIM_PARAMS"]["Act_Sparsity"] = Act_Sparsity
					benchmark["SIM_PARAMS"]["SIM_CYCLES"] = SIM_CYCLES
					benchmark["SIM_PARAMS"]["MODE"] = MODE
	
	
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
	
					#print(network)
					#print(network_layer)
					benchmark["network_layer"] = network_layer
					benchmarks.append(benchmark)
	
	
	'''
	combos = [base_hardware_config] + combos
	benchmarks = [ {
		'SIM_PARAMS': base_SIM_PARAMS,
		'network_layer': base_network_layer,
		'mapping': base_mapping,
		}] + benchmarks
	'''	

	tested = -1
	HW_NUM = int(sys.argv[-1])
	BENCH_NUM = int(sys.argv[-4])
	for inputs in combos:
		tested += 1
		if(tested < int(sys.argv[-3])):
			continue
		for benchmark in [benchmarks[i] for i in range(BENCH_NUM)]:
			print("runnign core")
			core(tested, inputs=inputs, benchmark=benchmark, MODE=MODE, core_component = WinogradConv, core_name =  "WinogradConv")	
		#tested += 1
		if(HW_NUM > 0 and tested > HW_NUM):
			exit()	













if __name__ == "__main__":

	import sys	

	MODE = sys.argv[-2]	
	combos = []

	#Hierarchy based modelling parameters
	#GENERAL
	# -> PE_ARRAY (Multiplier2)
	# -> L1_WEI_LOADER (Serializer/Deserializer + L1 SRAM)
	# -> L1_ACT_LOADER	(..)
	# -> GLOBAL_L2       (Serializer/Deserializer + L2 SRAM)
	# -> ADDER_TREE      (ADDER TREE or Serializer + Accumulator)
	# -> ACCUMUALTOR     (Accumulator w/ Reg, Accumulator w/ SRAM)
	# -> OUTPUT_LOADER   (Serializer/Deserializer + L1 SRAM)
	# -> OUTPUT_DRAM_L2_BUS   (MUX2)
	# -> L2_L1_ACT_L1_WEI_BUS  (MULTICAST)
	base_hardware_config = {

		"GENERAL": {
			"LOOP_ORDER": ["B", "N", "I",  "KX", "KY", "X", "Y"],
			"TB": 1,
			"TN": 1,
			"TI": 4,
			"TX": 1,
			"TY": 1,
			"TKX": 1,
			"TKY": 1,
	
			"CLOCK": 1,
			"cap_load": 0.1,
			"tech":"tsmc40",

			"PRE_CALC_WEIGHTS": False,

			"GENERAL_PREC": 8, #General PREC if non specified
		},
		"PE_ARRAY": {
			"VALID_NETS": ["PE_ARRAY"],
			"ACT_PREC": 8,
			"WEI_PREC": 8,

			"MULT_TYPE": "HighRadixMultiplier",
			"MULT_SIDE": "weight",
			"MULT_RADIX": 2,
			"MULT_CORE_ADDER_TYPE": "RCAAdder2",
		},
		"ADDER_TREE": {
			"VALID_NETS": ["ADDER_TREE"],
			"ADDER_TREE_CORE_ADDER_TYPE": "RCAAdder2",
			"ADDER_TREE_TYPE": "AdderTreeN",#AdderTree, i.e. Accumulator
			"ADDER_TREE_PREC": 16,
			"ADDER_TREE_DEPTH": 1, #i.e. number of cycles to output	
		},	
		"ACCUMULATOR": {
			"VALID_NETS": ["ACCUMULATOR"],
			"TYPE": "AccumulatorN",
			"CORE_ADDER_TYPE": "RCAAdder2",
			"ACCUM_PREC": 32,
		},
		"WEI_LOADER": {
			"VALID_NETS": ["L1_WEI_READ", "L1_WEI_WRITE", "L1_WEI_WRITE_NETWORK", "L1_WEI_READ_NETWORK"],
			"VALID_NETS": ["L1_WEI_READ", "L1_WEI_WRITE"],#"L1_WEI_WRITE_NETWORK", "L1_WEI_READ_NETWORK"],
			#"VALID_NETS": ["L1_WEI_WRITE_NETWORK", "L1_WEI_READ_NETWORK"],
	
			"L1_WEI_SRAM_SIZE": [16, 256],
			"L1_WEI_SRAM_TYPE": "Reg",
			"L1_WEI_TOTAL_SIZE" : 48000,		
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers	
			"LOAD_RATIO": 1,			
			"PREC": 8,
		},
		"ACT_LOADER": {
			"VALID_NETS": ["L1_ACT_READ", "L1_ACT_WRITE"],
#, "L1_ACT_WRITE_NETWORK", "L1_ACT_READ_NETWORK"],	
		#	"VALID_NETS": ["L1_ACT_WRITE_NETWORK", "L1_ACT_READ_NETWORK"],
	
			"L1_ACT_SRAM_SIZE": [16, 256],	
			"L1_ACT_SRAM_TYPE": "Reg",		
			"L1_ACT_TOTAL_SIZE" : 48000,	
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers
			"LOAD_RATIO": 1,		
			"PREC": 8,
		},
		"OUT_LOADER": {	
			"VALID_NETS": ["L1_OUT_READ", "L1_OUT_WRITE", "L1_OUT_WRITE_NETWORK", "L1_OUT_READ_NETWORK"],		
			"VALID_NETS": ["L1_OUT_READ", "L1_OUT_WRITE"],#, "L1_OUT_WRITE_NETWORK", "L1_OUT_READ_NETWORK"],		
			"L1_OUT_SRAM_SIZE": [16, 256],
			"L1_OUT_SRAM_TYPE": "Reg",
			"L1_OUT_TOTAL_SIZE" : 48000,
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers	
			"LOAD_RATIO": 1,	
			"PREC": 16,
		},

		"WEI_WINO_G": {
			"VALID_NETS": ["WEI_WINO_G_MULT", "WEI_WINO_G_ADD"],
			"IN_PREC": 16,
			"OUT_PREC": 32, 
			"MULT_TYPE": "SimpleMultiplier2",
			"MULT_RADIX": 2,
			"MULT_SIDE": "weight",
			"MULT_CORE_ADDER_TYPE": "RCAAdder2",

			"ADDERN_TYPE": "AddTreeN", #Accumulator
			"CORE_ADDER_TYPE": "RCAAdder2",
		},
		"WEI_WINO_GT": {
			"VALID_NETS": ["WEI_WINO_GT"],
			"IN_PREC": 12,
			"OUT_PREC": 16, 
			"MULT_TYPE": "SimpleMultiplier2",
			"MULT_CORE_ADDER": "RCAAdder2",
			"ADDERN_TYPE": "AddTreeN", #Accumulator
			"ADDERN_CORE_ADDER": "RCAAdder2",
		},

		"ACT_WINO_B": {
			"VALID_NETS": ["ACT_WINO_B"],
			"IN_PREC": 8,
			"OUT_PREC": 12, 
			"MULT_TYPE": "SimpleMultiplier2",
			"MULT_CORE_ADDER": "RCAAdder2",
			"ADDERN_TYPE": "AddTreeN", #Accumulator
			"ADDERN_CORE_ADDER": "RCAAdder2",
		},	
		"ACT_WINO_BT": {
			"VALID_NETS": ["ACT_WINO_B"],
			"IN_PREC": 12,
			"OUT_PREC": 16, 
			"MULT_TYPE": "SimpleMultiplier2",
			"MULT_CORE_ADDER": "RCAAdder2",
			"ADDERN_TYPE": "AddTreeN", #Accumulator
			"ADDERN_CORE_ADDER": "RCAAdder2",
		},	
		"OUT_WINO_A": {
			"VALID_NETS": ["OUT_WINO_A"],
			"IN_PREC": 16,
			"OUT_PREC": 16, 
			"MULT_TYPE": "SimpleMultiplier2",
			"MULT_CORE_ADDER": "RCAAdder2",
			"ADDERN_TYPE": "AddTreeN", #Accumulator
			"ADDERN_CORE_ADDER": "RCAAdder2",
		},
		"OUT_WINO_AT": {
			"VALID_NETS": ["OUT_WINO_AT"],
			"IN_PREC": 16,
			"OUT_PREC": 16, 
			"MULT_TYPE": "SimpleMultiplier2",
			"MULT_CORE_ADDER": "RCAAdder2",
			"ADDERN_TYPE": "AddTreeN", #Accumulator
			"ADDERN_CORE_ADDER": "RCAAdder2",
		},	
		"WEI_PE_CAST": {
			"VALID_NETS": ["WEI_PE_CAST"],			
			"CAST_RATIO": 1,	
			"PREC": 16,
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers		
		},
		"ACT_PE_CAST": {
			"VALID_NETS": ["ACT_PE_CAST"],
			#ACT Is a special case because the casting ratio, i.e. is dynamic.
			"CAST_RATIO": 1,	
			#"INTER_PE_X": False,does this exist even?
			#"INTER_PE_Y": False,
			"PREC": 12,
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers		
	
		},
		"L2": {
			"VALID_NETS": ["L2_OUT_WRITE", "L2_WEI_READ", "L2_ACT_READ", "L2_ACT_WRITE", "L2_WEI_WRITE",
		"OUTPUT_DRAM_L2_BUS",
			],
			"L2_SRAM_SIZE": [8, 64],
			"L2_SRAM_TYPE": "Reg",	
			"LOAD_RATIO": 1,#compared to max(L1_WEI_LEN, L1_ACT_LEN)	
			"WEI_PREC": 8,
			"ACT_PREC": 8,
		},

	}
	#VALID_UNITS = [k  for k in  base_hardware_config] #["PE_ARRAY"]  #[,"WEI_LOADER"]#, "WEI_PE_CAST", "ACT_PE_CAST"]#[k  for k in  base_hardware_config]#["PE_ARRAY"]
	

	VALID_UNITS = ["OUT_LOADER", "PE_ARRAY", "WEI_LOADER", "ACT_LOADER","WEI_PE_CAST", "ACT_PE_CAST"]#[k  for k in  base_hardware_config] #["PE_ARRAY"]  #[,"WEI_LOADER"]#, "WEI_PE_CAST", "ACT_PE_CAST"]#[k  for k in  base_hardware_config]#["PE_ARRAY"]
	VALID_UNITS = ["OUT_LOADER", "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]
	VALID_UNITS = ["OUT_LOADER", "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]
	
	VALID_UNITS = ["PE_ARRAY"]

	VALID_UNITS = ["WEI_WINO_G"]
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
	
	design = dict_to_str(base_hardware_config["GENERAL"])
	#Should be hierarchical

	base_SIM_PARAMS = {
	"SAVE_RESULTS": "analyzed_04_03",

		"name": base_network_layer['layer_name'],
		"root": f"generated/Arch/WinogradConv/{design}",

		"SIM_CYCLES": 1000,
		"Randomize": 1,
		"Wei_Sparsity": 0.1,
		"Act_Sparsity": 0.1,	
		'save_np':True,#False,# True,
		'MODE': MODE,
		"RUN_GOLDEN_SBT": 1,	
		'RUN_CPP': True,
		"SKIP_IF_EXISTING_GOLDEN":True,#False,# True,#don't run the golden related flow if we see the golden power is there
	}
	#SIM_PARAMS = base_SIM_PARAMS
	#base_SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])


	#core(0, inputs=inputs, benchmark=benchmark, MODE=MODE, core_component = WinogradConv, core_name =  "WinogradConv")	

	run_wino_fig6(base_hardware_config, base_mapping, base_network_layer, base_SIM_PARAMS, VALID_UNITS)


