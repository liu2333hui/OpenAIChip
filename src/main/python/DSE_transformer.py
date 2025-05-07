import warnings
from sympy.utilities.exceptions import SymPyDeprecationWarning
warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)  # 仅屏蔽目标警告


import numpy as np
from pprint import pprint
import copy
import pandas as pd
SBT = "/afs/ee.ust.hk/staff/ee/jaymok/.local/share/coursier/bin/sbt"
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
from power_models.Parallel2SerialPrimitive import Parallel2SerialPrimitive
from power_models.MulticastPrimitive import MulticastPrimitive
from toggle import gen_in
import os
import json


from DSE import Multiplier2Block, MulticastBlock, NetworkBlock, SRAMBlock, AdderNBlock,valid_file#,MuxBlock

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


#####################################################
debug_sbt = 1

GLOBAL_RUNS = 0
START_RUN = 2416#967#690# 413 #388#5#125#-1
COMPONENT_SELECT = []#"WEI_LOADER"]#"ADDER_TREE"]
PRIM_SELECT = []#"Network"]
MODES = []#[1,2,0]#0-golden, 1-b1, 2-b2

N = 32

PREC = 8
ACT_PREC = 8
WEI_PREC = 8


WEI_SPARSITY = 0.1
WEI_BIT_ZERO = 4
ACT_SPARSITY = 0.1
ACT_BIT_ZERO = 4
ACT_PRECS = [8]
WEI_PRECS = [8]

print("WEI_SPARSITY", WEI_SPARSITY)
print("ACT_SPARSITY", ACT_SPARSITY)


######################################################
#Helpers
def bitzero(A):
	bits = []
	for i in A:
		bits.append(bin(i).count("1"))
	return bits


###############################################################

def SoftmaxBlock(h, hh, in_0, prec, softmax_type = "", mode=[], PRIM_SELECT=[]):
	if(softmax_type == "LUT"):
	
	elif(softmax_type == "CORDIC"):
	
	

#Simple Timing simulator
def WinoTimer(hardware_config, benchmark  , power=True ):
	#	print(hardware_config)
	h = hardware_config["GENERAL"]
	
	hp = {}	
	for bb in benchmark:


		b = benchmark[bb]
		cycles = {}
		PE_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			 (b['I']+h['TI']-1)//h['TI']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB']	

		if(not  h['INTER_PE_X']  ):
			X_CYCLES =  (b['X']+h['TX']+h['TKX']-1)//(h['TX']+h['TKX']-1)  * (b['KX']+h['TKX']-1)//h['TKX'] 
			X_TILE = (h['TX'] + h['TKX'] - 1)
		else:
			X_CYCLES =   (b['X']+h['TX']-1)//h['TX'] 
			X_TILE = h['TX']

		if(not  h['INTER_PE_Y']  ):
			Y_CYCLES =  (b['Y']+h['TY']+h['TKY']-1)//(h['TY']+h['TKY']-1)  * (b['KY']+h['TKY']-1)//h['TKY'] 
			Y_TILE = (h['TY'] + h['TKY'] - 1)
		else:
			Y_CYCLES =   (b['Y']+h['TY']-1)//h['TY'] 
			Y_TILE = h['TY']

		WEI_TILE = h['TN']*h["TKX"]*h["TKY"]*h["TI"]

		ACT_TILE = h['TB']*X_TILE*Y_TILE*h["TI"]
		OUT_TILE = h['TB']*h["TN"]

		TILE = h['TI']*h['TN']*(h['TX']+h['TKX']-1)*(h['TY']+h['TKY']-1)*h['TB']
		PE = TILE 



		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 
	

		INNER = h["TI"]

		ACC_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			

		#power cost, there is an added Parallel2Serial unit
		if( not h['INTER_PE_X']  ):
			X_CYCLES =  (b['X']+h['TX']+h['TKX']-1)//(h['TX']+h['TKX']-1)  * (b['KX']+h['TKX']-1)//h['TKX'] 
		else:
			X_CYCLES =   (b['X']+h['TX']-1)//h['TX'] 

		if(not  h['INTER_PE_Y']  ):
			Y_CYCLES =  (b['Y']+h['TY']+h['TKY']-1)//(h['TY']+h['TKY']-1)  * (b['KY']+h['TKY']-1)//h['TKY'] 
		else:
			Y_CYCLES =   (b['Y']+h['TY']-1)//h['TY'] 




		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 

		if(h["PRE_COMPUTE_WEIGHTS"]):
			WEI_CYCLES = 	(h['TX'] + b['KX'] - 1 +h['TKX']-1)/h['TKX']  *  	(h['TX'] + b['KX'] -1+h['TKX']-1)/h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 

			WEI_TILE = h['TN']*(h['TX'] + h["TKX"]-1)*(h['TY'] + h["TKY"] - 1)*h["TI"]
			SKIP_WEI_MAP =True
		else:
			SKIP_WEI_MAP = False	


		#reuse calculate from loop order
		wei_reuse = 1
		act_reuse = 1
		out_reuse = 1
		ACT  = ['B', 'I']
		if(h['INTER_PE_Y'] ):
			pass
		else:
			ACT.append("X")
		if(h['INTER_PE_Y'] ):
			pass
		else:
			ACT.append("Y")

		wei_flag = 0
		act_flag = 0
		out_flag = 0
		OUT = ["B", "N", "X", "Y"]
		for var in h["LOOP_ORDER"][::-1]:
			if( wei_flag or var in ["N", "I", "KX", "KY"]):
				wei_reuse *= 1
				wei_flag = 1
			else:
				wei_reuse *= (b[var]+h["T"+var])/h["T"+var] #I, N, KX, KY

			if(act_flag or var in ACT):
				act_reuse *= 1
				act_flag = 1	
			else:	
				act_reuse *= (b[var]+h["T"+var])/h["T"+var]

			if(out_flag or var in OUT):
				out_reuse *= 1
				out_flag = 1	
			else:	
				out_reuse *= (b[var]+h["T"+var])/h["T"+var]

	
		in_a = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = h['ACT_PREC'], N = N*(h['TX']+h['TKX']-1)*(h['TKY']+h['TY']-1), REUSE = act_reuse)
		in_w = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = h['WEI_PREC'], N = N*h['TKX']*h['TKY'], REUSE = wei_reuse)
		in_a =  [r for idx,r in enumerate(in_a) if(idx <= N*(h['TX']+h['TKX']-1)**2-1)]
		in_w =  [r for idx,r in enumerate(in_w) if(idx <= N*h['TKX']**2-1)]



		in_orig = [in_w[idx] *in_a[idx] for idx in range(min(len(in_w), len(in_a)))]
		in_o = in_orig
	
		
		#print(len(in_w))
		#print(len(in_a))

		import wincnn
		wino_AT,wino_G,wino_BT,wino_f = wincnn.cookToomFilter([0,1,-1,2,-2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, -9, 10, -10],
                    h['TX'], h['TKX'])
		MU = max([gg.denominator for gg in np.array(wino_G).reshape(-1)])
		MU_A = max([gg.denominator for gg in np.array(wino_AT).reshape(-1)])
		wino_G = np.array(MU*wino_G).astype('int')
		wino_A = np.array(wino_AT).transpose()
		wino_GT = np.array(wino_G).transpose()
		wino_B = np.array(wino_BT).transpose()
		wino_BT = np.array(wino_BT)
		wino_AT = np.array(wino_AT)
	
		#print("in_w")
		#print(np.array(in_w).shape)
		weights = np.array(in_w).reshape((1, -1, h['TKX'],h['TKX']))
		input_data = np.array(in_a).reshape((1, -1, h['TX']+h['TKX']-1, h['TKY']+h['TY']-1))

		G_WEI = np.zeros((weights.shape[0], weights.shape[1],
			wino_G.shape[0], weights.shape[3] ))
		orig_shape = G_WEI.shape 
		G_WEI = np.matmul(wino_G, weights.reshape((-1, weights.shape[2], weights.shape[3]))	).reshape(  orig_shape)

		G_WEI_GT = np.zeros((weights.shape[0], weights.shape[1],
			wino_G.shape[0], wino_GT.shape[1] ))
		orig_shape = G_WEI_GT.shape
	

		G_WEI_GT = np.matmul(G_WEI.reshape((-1, G_WEI.shape[3])), wino_GT	).reshape(  orig_shape)
	

		inputs = input_data

		B_ACT = np.zeros(inputs.shape)

		orig_shape = B_ACT.shape 

		B_ACT = np.matmul(wino_B, inputs.reshape((-1, inputs.shape[-2], inputs.shape[-1]))	).reshape(  orig_shape)

		B_ACT_BT = np.zeros((inputs.shape)) #np.zeros((weights.shape[0], weights.shape[1],
		orig_shape = B_ACT_BT.shape
		B_ACT_BT = np.matmul(B_ACT.reshape((-1, B_ACT.shape[-1])), wino_BT	).reshape(  orig_shape)

	
		PE_OUT = [G_WEI_GT.reshape((-1))[idx] *B_ACT_BT.reshape((-1))[idx] for idx in range(min(len(G_WEI_GT.reshape((-1))), len(B_ACT_BT.reshape((-1)))))]
		PE_OUT = np.array(PE_OUT).reshape(   (-1,(h['TKX'] + h['TX'] - 1) , (h['TKX'] + h['TX'] - 1)  ) )
		#print(PE_OUT.shape)

		#print(wino_A.shape)
		#print(wino_A.shape)
		A_OUT = np.matmul(wino_AT, PE_OUT.reshape((-1, inputs.shape[-2], inputs.shape[-1]))	).reshape(   (-1,(h['TKX'] + h['TX'] - 1) ,  h['TX'])  ) 
		
		sections =  h['TX']
		padded_arr = np.pad(PE_OUT, (0, sections - len(PE_OUT)  % sections), mode='constant', constant_values=0)
		PE_OUT = padded_arr.reshape((-1, h['TX']))


		A_OUT_AT = np.zeros((PE_OUT.shape)) #np.zeros((weights.shape[0], weights.shape[1],
		orig_shape = A_OUT_AT.shape
		A_OUT_AT = np.matmul(A_OUT.reshape((-1, A_OUT.shape[-1])), wino_AT	)

		pe = PE
		#print("WINOGRAD TRANSFORM SHAPES")
		print(B_ACT.shape, B_ACT_BT.shape)
		print(G_WEI.shape, G_WEI_GT.shape)
		print(A_OUT.shape, A_OUT_AT.shape)	
		#input()
	
		ACT_SPARSITY = b['ACT_SPARSITY']
		WEI_SPARSITY = b['WEI_SPARSITY']
		OUT_SPARSITY = 1 - in_orig.count(0)/len(in_orig)





		#is compressed

		powers = {}
		##################################################################	
		for component in hardware_config:
			c = component
			hh = hardware_config[component] 
			#print(bb,component)
			if(component == "PE_ARRAY"):
				side = hh["MULT_SIDE"]
				radix = hh['MULT_RADIX']
				ratio = np.log2(radix)
				if(side == "weight"):
					side_cycle = hh["WEI_PREC"]/ratio
					side_bits = 1 - b["WEI_BIT_ZERO"]/hh['WEI_PREC']
					in_0 = G_WEI_GT.reshape((-1)).tolist()#in_w
					in_1 = B_ACT_BT.reshape((-1)).tolist()#in_a
					prec1 = hh["WEI_PREC"]
					prec2 = hh["ACT_PREC"]
					main_sparse = b['WEI_SPARSITY']
				elif(side == "input"):
					side_cycle = hh["ACT_PREC"]/ratio				
					side_bits = 1 - b["ACT_BIT_ZERO"]/hh['ACT_PREC']
		
					in_0 = B_ACT_BT.reshape((-1)).tolist()#in_a
					in_1 = G_WEI_GT.reshape((-1)).tolist()#in_w

					prec1 = hh["ACT_PREC"]
					
					prec2 = hh["WEI_PREC"]
					main_sparse = b['ACT_SPARSITY']
				else:
					print("invalid mult side")
					exit()

				#print(bitzeros,side_cycle, side_bits)
				#print(side_cycle * side_bits)
				#input()
				if(hh["MULT_TYPE"] == "HighRadixMultiplier"):
					cycles[c] = PE_CYCLES * side_cycle
				elif(hh["MULT_TYPE"] == "BitSerialMultiplier"):
					cycles[c] = PE_CYCLES * max(1, side_cycle* side_bits)
				else:
					print(hh['MULT_TYPE'] + " does not exist")
					exit()




				#POWER MODELING
				if(power):
					cc = min(len(in_0), len(in_1))
					in_0 = in_0[0:cc]
					in_1 = in_1[0:cc]
					#print(in_0)
					#print(in_1)	
					bitzeros = sum(bitzero(in_0))/len(bitzero(in_0))
					#power x ideal_time / scaled_time
					time_scaler = bitzero(in_0)
		
					#power model
					res = Multiplier2Block(h, hh, in_0, in_1, prec1, prec2, side, sparsity = main_sparse,mode=MODES,PRIM_SELECT=PRIM_SELECT  )
					#print(res)
					units = PE
					powers[c] = res['Total_Pwr']['res'][-1][-1] *units
					#input()
				
			
			elif(component == "ADDER_TREE"):

				in_0 = B_ACT_BT.reshape((-1)).tolist()#in_a
				in_1 = G_WEI_GT.reshape((-1)).tolist()#in_w
				in_o = [in_0[idx] *in_1[idx] for idx in range(min(len(in_0), len(in_1)))]

				if(hh["ADDERN_TYPE"] == "AddTreeN"):
					side_cycle = 1
				elif(hh["ADDERN_TYPE"] == "SimpleAdderN"):
					side_cycle = 1
	
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					side_cycle = INNER
				else:
					print("invalid ADDERN_TYPE", hh["ADDERN_TYPE"])
					exit()
	
				cycles[c] = PE_CYCLES * side_cycle

				#POWER MODELING
				if(power):
					cc = min(len(in_0), len(in_1))
					in_0 = in_o
					res = AdderNBlock( h, hh, in_o ,  hh["PREC"],  mode=MODES, sparsity= 1 - in_o.count(0)/len(in_o), INNER = max(2,INNER), PRIM_SELECT=PRIM_SELECT)


					units = OUT_TILE
					powers[c] = res['Total_Pwr']['res'][-1][-1] *units
					#input()
	
				pass
			elif(component == "ACCUMULATOR"):
				cycles[c] = PE_CYCLES 
	
				if(power):
					#cc = min(len(in_0), len(in_1))
					in_0 = in_orig
					in_o = in_0
					res = AdderNBlock( h, hh, in_0 ,  hh["PREC"],  mode=MODES, sparsity= 1 - in_o.count(0)/len(in_o), INNER = INNER, PRIM_SELECT=PRIM_SELECT)

					units = OUT_TILE
					powers[c] = res['Total_Pwr']['res'][-1][-1] *units
	
				pass	

			elif(component == "OUT_LOADER"):	
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				#cycles[c] = ACC_CYCLES*side_cycle

				cycles[c+".write"] = ACC_CYCLES*side_cycle
				cycles[c+".read"] = ACC_CYCLES*side_cycle#PE_CYCLES/wei_reuse#/h['SPARSE_RATIO']

				ratio = hh['LOAD_RATIO']
				OUT_SPARSITY = 1 - in_orig.count(0)/len(in_orig)

	
				res_r = SRAMBlock(h, hh, in_orig, sparsity = OUT_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
				res_w = SRAMBlock(h, hh, in_orig, sparsity = OUT_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)

				res = NetworkBlock(h, hh,ratio, in_orig, sparsity = OUT_SPARSITY, mode=MODES, fanout = 1, PRIM_SELECT=PRIM_SELECT)
	
				units =  1/side_cycle * OUT_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}
	


				pass
			elif(component == "WEI_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	

				cycles[c+".write"] = WEI_CYCLES*side_cycle
				cycles[c+".read"] = PE_CYCLES*side_cycle/wei_reuse
				#cycles[c+".read"] =   PE_CYCLES/wei_reuse*side_cycle
				WEI_SPARSITY = b['WEI_SPARSITY']
				hp[c] = 1/side_cycle * WEI_TILE*hh['PREC']


				ratio = hh['LOAD_RATIO']

				res_r = SRAMBlock(h, hh, in_orig, sparsity = WEI_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
				res_w = SRAMBlock(h, hh, in_orig, sparsity = WEI_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)

				res = NetworkBlock(h, hh,ratio, in_orig, sparsity = WEI_SPARSITY, mode = MODES, fanout = 1, PRIM_SELECT=PRIM_SELECT)

	
				units =  1/side_cycle * WEI_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}
	



				pass			
			elif(component == "ACT_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	

				cycles[c+".write"] = ACT_CYCLES*side_cycle
				cycles[c+".read"] = PE_CYCLES*side_cycle/act_reuse
	
				cycles[c] = ACT_CYCLES* side_cycle
	
				ACT_SPARSITY = b['ACT_SPARSITY']
				hp[c] = 1/side_cycle * ACT_TILE*hh['PREC']

				ratio = hh['LOAD_RATIO']


				res_r = SRAMBlock(h, hh, in_orig, sparsity = ACT_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
				res_w = SRAMBlock(h, hh, in_orig, sparsity = ACT_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)

				res = NetworkBlock(h, hh,ratio, in_orig, sparsity = ACT_SPARSITY, mode = MODES, fanout = 1, PRIM_SELECT=PRIM_SELECT)

	
				units =  1/side_cycle * ACT_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}
	
				pass
			elif(component == "WEI_PE_CAST"):


				ratio = hh['CAST_RATIO']


				cycles[c] = PE_CYCLES/wei_reuse *hh['CAST_RATIO']		


				if(power):
					res = MulticastBlock(h, hh, ratio, np.repeat(in_w,1), fanout = (pe//WEI_TILE)//ratio , PRIM_SELECT=PRIM_SELECT, mode=MODES)
					units = WEI_TILE*ratio
					res = res['Total_Pwr']['res'][-1][-1] *units 
					powers[c] = {"NETWORK": res}	
	
				pass
			elif(component == "ACT_PE_CAST"):
				cycles[c] =PE_CYCLES/act_reuse  *hh['CAST_RATIO']		
				#(todos) worst case here, the fanout may have to be adjusted to optimize for diagonal systolic arrays
				ratio = hh['CAST_RATIO']



				if(power):
					res =MulticastBlock(h, hh, ratio, np.repeat(in_a, 1), fanout = (pe//ACT_TILE)//ratio , PRIM_SELECT=PRIM_SELECT, mode = MODES)
					units = ACT_TILE*ratio
					res = res['Total_Pwr']['res'][-1][-1] *units 
					powers[c] = {"NETWORK": res}	


				pass

	
			elif(component in ["WINO_G", "WINO_GT", "WINO_B", "WINO_BT", "WINO_A", "WINO_AT"]):
				if(component in ["WINO_G", "WINO_GT"] and SKIP_WEI_MAP ):
					cycles[c] = 0
					powers[c] = 0

				#Multiplier part
				#maybe just skip
				#Adder part
				if(hh["ADDERN_TYPE"] == "AddTreeN"):
					side_cycle = 1
				elif(hh["ADDERN_TYPE"] == "SimpleAdderN"):
					side_cycle = 1
	
				elif(hh["ADDERN_TYPE"] == "Accumulator"):


					side_cycle = INNER
				else:
					print("invalid ADDERN_TYPE", hh["ADDERN_TYPE"])
					exit()	
				#cycles[c] = PE_CYCLES * side_cycle
				#ycles[c] = PE_CYCLES/wei_reuse*side_cycle 

				reuse_m = {
					"WINO_G": wei_reuse,
					"WINO_GT": wei_reuse,
					"WINO_B": act_reuse,
					"WINO_BT": act_reuse,
					"WINO_A": 1,
					"WINO_AT": 1,
				}
				m = {
					"WINO_G": G_WEI,
					"WINO_GT": G_WEI_GT,
					"WINO_B": B_ACT,
					"WINO_BT": B_ACT_BT,
					"WINO_A": A_OUT,
					"WINO_AT": A_OUT_AT,
				}
				inner = {
					"WINO_G": h['TKX'],
					"WINO_GT": h['TKX'],
					"WINO_B": h['TKX']+h['TX']-1,
					"WINO_BT": h['TKX']+h["TX"]-1,
					"WINO_A": h['TKX']+h["TX"]-1,
					"WINO_AT": h['TKX']+h["TX"]-1,
				}
				units_m = {
					"WINO_G": h['TN']*h['TI']*h['TKX']*(h['TKX']+h['TX']-1),
					"WINO_GT":h['TN']*h['TI']*(h['TKX']+h['TX']-1)**2,
					"WINO_B": h['TB']*h['TI']*(h['TKX']+h['TX']-1)**2,
					"WINO_BT": h['TB']*h['TI']*(h['TKX']+h['TX']-1)**2,
					"WINO_A": h['TB']*h['TI']*(h['TKX']+h['TX']-1)*h['TX'],
					"WINO_AT": h['TB']*h['TI']*h['TX']*h['TX'],
			
				}
				cycles[c] = PE_CYCLES/reuse_m[component]*side_cycle 
				#POWER MODELING
				if(power):
					#print(len(in_0), len(in_0))
					#input()

					in_0 = m[component].reshape((-1)).tolist()
					in_0 = in_0[0:N]
					res = AdderNBlock( h, hh, in_0 ,  hh["OUT_PREC"],  mode=MODES, sparsity= 1 - in_0.count(0)/len(in_0), INNER = inner[component], PRIM_SELECT=PRIM_SELECT)
					units = units_m[component]
					powers[c] = res['Total_Pwr']['res'][-1][-1] *units
					
						

			elif(component == "L2"):
				#if(hh['LOAD_RATIO']< 0):
				#	side_cycle = abs(hh['LOAD_RATIO'])
				#else:
				#	side_cycle = 1/abs(hh['LOAD_RATIO'])

				cycles[c] = 0
				pwrs = []
				for busunit,tile,cycles_0,in_0,sparsity in [("ACT_LOADER", ACT_TILE, ACT_CYCLES,in_a ,ACT_SPARSITY), ("OUT_LOADER", OUT_TILE,ACC_CYCLES, in_o, OUT_SPARSITY), ("WEI_LOADER", WEI_TILE, WEI_CYCLES, in_w, WEI_SPARSITY)]:

					if(hh['BIT_LEN']//hh['PREC'] > tile):
						ratio = hh['BIT_LEN']//hh['PREC'] // tile
					else:
						ratio = -tile //( hh['BIT_LEN']//hh['PREC'])

					if(ratio < 0):
						side = abs(ratio)
					else:
						side = 1/abs(ratio)

					cycles[c] += cycles_0*side	
					if(power):
						res_r = SRAMBlock(h, hh, in_0, sparsity = ACT_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
						res_w = SRAMBlock(h, hh, in_0, sparsity = ACT_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)

						units =  1/side * tile #fillter for now

						res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
						res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]

			
					#res = NetworkBlock(h, hh,ratio, in_0, sparsity = sparsity, mode = modes, fanout = 1)
						res = NetworkBlock(h, hh,ratio, in_0, sparsity = sparsity, mode = MODES, fanout = 1, PRIM_SELECT=PRIM_SELECT)

						res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	

					
						pwrs.append((res_r, res_w,res))	
				if(power):
					powers[c] = {
					"BUS": pwrs}




					#cycles[c] = WEI_CYCLES*side_cycle + ACT_CYCLES*side_cycle + ACC_CYCLES*side_cycle		
	
		#print("cycles")
		

		#print(bb,cycles, max([cycles[t] for t in cycles]))
		#print(powers)
		#exit()
		#print(bb, hp)
	return cycles, powers
	

if __name__ == "__main__2":

	

	B = 4
	benchmark = {
		"Conv1": {
			"X":224,"Y":224,"N":64,"I":3,"KX":7,"KY":7,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		"AvgPool1": {
			"X":7,"Y":7,"N":1024,"KX":7,"KY":7,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		"MaxPool1": {
			"X":112,"Y":112,"N":64,"KX":3,"KY":3,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},

		"FC": {
			"X":1,"Y":1,"N":1000,"I":1024,"KX":1,"KY":1,"B":B,
			"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
	}

	def Bottleneck(n,X,N,I,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO):
		Y = X
		return {
		f"Conv{n}_1": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_2": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_3": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_4": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Element{n}_4": {
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_5": {
			"X":X,"Y":Y,"N":N,"I":I,"KX":1,"KY":1,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},

		}


	benchmark.update(Bottleneck(2,56,64,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(3,56,256,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(4,28,512,256,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(5,14,1024,512,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)


	WinoConv_0 = {
		"GENERAL": {"LOOP_ORDER": ["B","I","X","Y","N"],"TB": 1,"TN": 4,"TI": 4,"TX": 2,"TY": 2,"TKX": 3,"TKY": 3,"CLOCK": 1,"cap_load": 0.1,"tech":"tsmc40","INTER_PE_X": False,"INTER_PE_Y": False, "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC, "PRE_COMPUTE_WEIGHTS": False, },
		"PE_ARRAY": {"ACT_PREC": ACT_PREC,"WEI_PREC": WEI_PREC,"MULT_TYPE": "BitSerialMultiplier","MULT_SIDE": "weight","MULT_RADIX": 1<<2,"MULT_CORE_ADDER_TYPE": "SimpleAdder2",},
		"ADDER_TREE":{"ADDERN_TYPE": "AddTreeN","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC,"OUT_PREC": ACT_PREC+WEI_PREC,"DEPTH": 1, },	

		#6 WINOGRAD MAPPERS, or MULT_ADD Components
		"WINO_G":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_GT":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_B":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_BT":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_A":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_AT":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		
		"ACCUMULATOR": {"ADDERN_TYPE": "Accumulator","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC, "OUT_PREC": ACT_PREC+WEI_PREC},
		"WEI_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": WEI_PREC,},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC,},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC+WEI_PREC,},
		"WEI_PE_CAST":{"CAST_RATIO": 1,"PREC": WEI_PREC,"NETWORK_TYPE": "Mux",},
		"ACT_PE_CAST": {"CAST_RATIO": 1,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"NETWORK_TYPE": "Mux", "SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	#print(WinoConv_0)
	#filter benchmark for only ones that are valid
	print(benchmark)
	benchmark_filter = {}
	for bb in benchmark:
		b = benchmark[bb]		
		if("Conv" in bb):
			if(b['KX'] == WinoConv_0["GENERAL"]["TKX"] and b['KY'] == WinoConv_0["GENERAL"]["TKY"]):
				#print(bb)
				#print(b)
				#input()
				benchmark_filter[bb] = b
	#exit()


	WinoTimer(WinoConv_0, benchmark_filter  , power =True )






if __name__ == "__main__":
	B = 4
	benchmark = {
		"Conv1": {
			"X":224,"Y":224,"N":64,"I":3,"KX":7,"KY":7,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		"AvgPool1": {
			"X":7,"Y":7,"N":1024,"KX":7,"KY":7,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		"MaxPool1": {
			"X":112,"Y":112,"N":64,"KX":3,"KY":3,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},

		"FC": {
			"X":1,"Y":1,"N":1000,"I":1024,"KX":1,"KY":1,"B":B,
			"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
	}

	def Bottleneck(n,X,N,I,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO):
		Y = X
		return {
		f"Conv{n}_1": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_2": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_3": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_4": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Element{n}_4": {
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_5": {
			"X":X,"Y":Y,"N":N,"I":I,"KX":1,"KY":1,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},

		}


	benchmark.update(Bottleneck(2,56,64,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(3,56,256,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(4,28,512,256,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(5,14,1024,512,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)


	WinoConv_0 = {
		"GENERAL": {"LOOP_ORDER": ["B","I","X","Y","N"],"TB": 1,"TN": 4,"TI": 4,"TX": 2,"TY": 2,"TKX": 3,"TKY": 3,"CLOCK": 1,"cap_load": 0.1,"tech":"tsmc40","INTER_PE_X": False,"INTER_PE_Y": False, "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC, "PRE_COMPUTE_WEIGHTS": False, },
		"PE_ARRAY": {"ACT_PREC": ACT_PREC,"WEI_PREC": WEI_PREC,"MULT_TYPE": "BitSerialMultiplier","MULT_SIDE": "weight","MULT_RADIX": 1<<2,"MULT_CORE_ADDER_TYPE": "SimpleAdder2",},
		"ADDER_TREE":{"ADDERN_TYPE": "AddTreeN","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC,"OUT_PREC": ACT_PREC+WEI_PREC,"DEPTH": 1, },	

		#6 WINOGRAD MAPPERS, or MULT_ADD Components
		"WINO_G":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_GT":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_B":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_BT":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_A":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		"WINO_AT":  {"ADDERN_TYPE": "AddTreeN", "CORE_ADDER_TYPE": "SimpleAdder2", "PREC": WEI_PREC, "OUT_PREC": 2*WEI_PREC, "MULT_TYPE": "ConstantMultiplier", "MULT_SIDE": "weight", "MULT_RADIX": 2, "MULT_CORE_ADDER_TYPE": "SimpleAdder2"} ,
		
		"ACCUMULATOR": {"ADDERN_TYPE": "Accumulator","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC, "OUT_PREC": ACT_PREC+WEI_PREC},
		"WEI_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": WEI_PREC,},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC,},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC+WEI_PREC,},
		"WEI_PE_CAST":{"CAST_RATIO": 1,"PREC": WEI_PREC,"NETWORK_TYPE": "Mux",},
		"ACT_PE_CAST": {"CAST_RATIO": 1,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"NETWORK_TYPE": "Mux", "SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	#print(WinoConv_0)
	#filter benchmark for only ones that are valid
	benchmark_filter = {}
	for bb in benchmark:
		b = benchmark[bb]		
		if("Conv" in bb):
			if(b['KX'] == WinoConv_0["GENERAL"]["TKX"] and b['KY'] == WinoConv_0["GENERAL"]["TKY"]):
				#print(bb)
				#print(b)
				#input()
				benchmark_filter[bb] = b

	benchmark = benchmark_filter
	def ArchTimer(core, mapping, benchmarks=benchmark, FILTER=[]):
		global GLOBAL_RUNS
		global START_RUN
		global COMPONENT_SELECT
		#print(FILTER[0])
		#print(COMPONENT_SELECT)
		#input()

		if(len(COMPONENT_SELECT) != 0 and FILTER[0] not in COMPONENT_SELECT):
			return -1#continue
		GLOBAL_RUNS += 1
		if(START_RUN > GLOBAL_RUNS):
			return
		#Get Area	
		#Get Timing and Power
		res = {}
		for benchmark in benchmarks:
			if 1:
				base_hardware_config = core[mapping[benchmark]]	

				#filtering if necessary
				if(len(FILTER) == 0):
					pass
				else:
					base_hardware_config = {k: v for k, v in base_hardware_config.items() if k in FILTER + ["GENERAL"]}

				#(TODOS), when there are multiple components in one-run, not FILTER
				GEN =  dict_values_to_str(base_hardware_config["GENERAL"])
				COMP = dict_values_to_str(base_hardware_config[FILTER[0]])
				base_file = valid_file(f"generated/DSE/FIRST_PASS/Conv/WinogradConv/{GEN}/{FILTER[0]}/{COMP}/{benchmark}.{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}")


				time_res, power_res = WinoTimer(base_hardware_config, {benchmark:benchmarks[benchmark]})#, FILTER=FILTER)	
				time_file = valid_file(f"{base_file}.time")
				with open(time_file  , "w", encoding="utf-8") as f:
					json.dump(time_res, f, indent=4)

				#print("our model")
				#input()
				#power_res = SystolicOurModel(base_hardware_config, {benchmark:benchmarks[benchmark]}, modes = MODES)# FILTER=FILTER)	
				our_file = valid_file(f"{base_file}.ourpower")
				with open(our_file  , "w", encoding="utf-8") as f:
					json.dump(power_res, f, indent=4)

				##baseline1(todos)
				#baseline2(todos)
				#print(f"done {benchmark} {FILTER[0]} {GEN} {COMP}")
				#res[benchmark] = {"time": time_res, "power": power_res}#unit_res, for sharing purposes
		
		#post analysis? sum up the total benchmark results?
		print(f"done {GLOBAL_RUNS} FULL LOAD {FILTER[0]} {GEN} {COMP}")
		#print(res)
		#input()	
		#exit()	
		return res

	#ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark)


	################################################################################
	# DSE 1st PASS - SYSTOLIC CONV UNIT
	################################################################################
	Conv_0 = "WinoConv_0"#"SystolicConv_0"
	MAPPING = {
		"Conv1": Conv_0,
		"MaxPool1": "MaxPool_0",
		"Conv2_1": Conv_0,
		"Conv2_2": Conv_0,
		"Conv2_3": Conv_0,
		"Conv2_4": Conv_0,
		"Element2_4": "Elementwise_0",
		"Conv2_5": Conv_0,
		"Conv3_1": Conv_0,
		"Conv3_2": Conv_0,
		"Conv3_3": Conv_0,
		"Conv3_4": Conv_0,
		"Element3_4": "Elementwise_0",
		"Conv3_5": Conv_0,	
		"Conv4_1": Conv_0,
		"Conv4_2": Conv_0,
		"Conv4_3": Conv_0,
		"Conv4_4": Conv_0,
		"Element4_4": "Elementwise_0",
		"Conv4_5": Conv_0,	
		"Conv5_1": Conv_0,
		"Conv5_2": Conv_0,
		"Conv5_3": Conv_0,
		"Conv5_4": Conv_0,
		"Element5_4": "Elementwise_0",
		"Conv5_5": Conv_0,	
		"AvgPool1": "AvgPool_0",
		"FC": Conv_0,	
	}


	LOOP_ORDERS = [
				["B", "N", "I", "KX", "KY", "X", "Y"],
					["B", "N", "Y", "X", "I", "KX", "KY"],
					["B", "Y", "X", "KY", "KX", "I", "N"],
					["B", "Y", "X", "KY", "KX", "N", "I"],	
					["KY", "KX", "I", "X", "Y", "B", "N"],
					["I", "N", "KX", "KY", "Y", "X", "B"],
					["I","B", "N", "X", "Y", "KX", "KY"],	
					["B",  "KX", "KY",  "N", "I","X", "Y", ],	
	]

	#tb,tn,  ti,tx, ty,tkx,tky in 	
	TILINGS = [#64 pe case
		[1, 8,   8,2,  2,  3,3],
		[1, 16,   16,2,  2,  3,3],
		[1, 12,   12,2,  2,  3,3],
		[1, 12,   8,2,  2,  3,3],	
		[1, 4,   4,4,  4,  3,3],
 		[1, 4,   4,3,  3,  3,3],
 		[1, 4,   4,4,  4,  3,3],
  		[1, 2,   2,5,  5,  3,3],
  		[2, 1,   2,6,  6,  3,3],
  		[1, 16,  1,2,  2,  3,3],  
  		[1, 4,  16,2,  2,  3,3],   
 	       	[1,8,  8,2,  2,  3,3],
        	[1,8,  8,2,  2,  3,3],	
        	[1,16,  4,2,  2,  3,3],	
       		[1,4,  16,2,  2,  3,3],			
        	[2,4,  8,2,  2,  3,3],			
	       	[2,2,  16,2,  2,  3,3],			
	       	#[1,8,  32,2,  2,  3,3],			]
		]
	accelerator_core = {
		"WinoConv_0": WinoConv_0,
	}


	#1st pass
	#hc = accelerator_core
	hc = WinoConv_0#accelerator_core["SystolicConv_0"]
	for clock in [1]:
		#for cap_load in [0.1]:
		for WEI_COMPRESS in [False, True]:
			for ACT_PREC in ACT_PRECS:
				for WEI_PREC in WEI_PRECS:
					for inter_x in [True,False]:
						for inter_y in [True,False]:	
							for lp in LOOP_ORDERS:
								for tb,tn, ti,tx, ty,tkx,tky in TILINGS:		
									#GENERAL
									hc["GENERAL"]["LOOP_ORDER"] = lp
									hc["GENERAL"]["TB"] =  tb
									hc["GENERAL"]["TI"] =  ti
									hc["GENERAL"]["TN"] =  tn
									hc["GENERAL"]["TX"] =  tx
									hc["GENERAL"]["TY"] =  ty
									hc["GENERAL"]["TKX"] =  tkx
									hc["GENERAL"]["TKY"] =  tky			
			
									hc["GENERAL"]["PRE_COMPUTE_WEIGHTS"] =  WEI_COMPRESS

									hc["GENERAL"]["INTER_PE_X"] =  inter_x
									hc["GENERAL"]["INTER_PE_Y"] =  inter_y
			
									#component-level pass
									#use accelerator_core as the base
									#1.1. PE_ARRAY
									FILTER = "PE_ARRAY"
									for MULT_TYPE in ["BitSerialMultiplier", "HighRadixMultiplier"]:
										for MULT_SIDE in ["weight", "input"]:
											for MULT_CORE_ADDER_TYPE in ["SimpleAdder2"]:
												for RADIX in range(1,1+WEI_PREC):
													MULT_RADIX = 2<<RADIX
													hc[FILTER]['MULT_TYPE'] = MULT_TYPE
													hc[FILTER]['MULT_SIDE'] = MULT_SIDE
													hc[FILTER]['MULT_CORE_ADDER_TYPE'] = MULT_CORE_ADDER_TYPE
													hc[FILTER]['MULT_RADIX'] = MULT_RADIX
							
													ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])
										


									#1.2. ADDER_TREE
									FILTER = "ADDER_TREE"
									for ADDERN_TYPE in ["SimpleAdderN","AddTreeN", "Accumulator"]:
										for CORE_ADDER_TYPE in ["SimpleAdder2"]:
											hc[FILTER]['CORE_ADDER_TYPE'] = CORE_ADDER_TYPE
											hc[FILTER]['ADDERN_TYPE'] = ADDERN_TYPE
											ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])
											


									#1.2. WINO
									FILTER = "WINO_GT"
									for FILTER in ["WINO_GT", "WINO_G", "WINO_B", "WINO_BT", "WINO_AT", "WINO_A"]:
										for ADDERN_TYPE in ["SimpleAdderN","AddTreeN", "Accumulator"]:
											hc[FILTER]['CORE_ADDER_TYPE'] = CORE_ADDER_TYPE
											hc[FILTER]['ADDERN_TYPE'] = ADDERN_TYPE
											ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])
	
										
									#1.3. ACCUMULATOR
									FILTER = "ACCUMULATOR"
									for CORE_ADDER_TYPE in ["SimpleAdder2","RCAAdder2"]:
										hc[FILTER]['CORE_ADDER_TYPE'] = CORE_ADDER_TYPE
										ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])
									#1.4-5-6 WEI_LOADER
									def LOADER(FILTER):										
										for SRAM_SIZE in [[16,256]]:
											for SRAM_TYPE in ["Reg"]:
												for NETWORK_TYPE in ["Mux", "Shift"]:
													for LOAD_RATIO in [-2,-32,-16, -8, -4, -2, 1, 2, 4]:			
														
														hc[FILTER]['NETWORK_TYPE'] = NETWORK_TYPE
														hc[FILTER]['LOAD_RATIO'] = LOAD_RATIO
	
														ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])

	
									LOADER("WEI_LOADER")
									LOADER("OUT_LOADER")
									LOADER("ACT_LOADER")						
									#1.7 BROADCASTING NETWORK
									def CASTING(FILTER):										
										for NETWORK_TYPE in ["Mux", "Shift"]:
											for CAST_RATIO in [1, 2, 4, 8, 16, 32]:			
												hc[FILTER]['NETWORK_TYPE'] = NETWORK_TYPE
												hc[FILTER]['CAST_RATIO'] = CAST_RATIO	
												ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])

									CASTING("WEI_PE_CAST")
									CASTING("ACT_PE_CAST")
							
									#1.8 L2
									FILTER = "L2"
									for BIT_LEN in [64, 128, 256, 512, 1024]:
										hc[FILTER]['BIT_LEN'] = BIT_LEN
										ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])


	#END first pass of SYstolic Unit
	################################################################################
	# DSE 1st PASS - WINOGRAD CONV UNIT
	################################################################################
	

	################################################################################
	# DSE 1st PASS - SPARSE CONV UNIT
	################################################################################	





	################################################################################
	# DSE 2nd PASS - WINOGRAD CONV UNIT
	# 2nd pass
	# combinational recovery
	################################################################################
	









	#our power
	#SystolicTimer(base_hardware_config, benchmark)	
	#SystolicOurModel(base_hardware_config, benchmark)
	#input()
	#timing model
	#SystolicTimer(base_hardware_config, benchmark)
	
	
