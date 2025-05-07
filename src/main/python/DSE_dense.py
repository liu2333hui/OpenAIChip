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


from DSE import MulticastBlock, NetworkBlock, SRAMBlock, AdderNBlock#,MuxBlock

#####################################################
debug_sbt = 1

GLOBAL_RUNS = 0
START_RUN = -1#388#5#125#-1
COMPONENT_SELECT = ["WEI_LOADER"]#"ADDER_TREE"]
PRIM_SELECT = ["Network"]
MODES = [1,2,0]#0-golden, 1-b1, 2-b2

N = 128

PREC = 8
ACT_PREC = 8
WEI_PREC = 8


WEI_SPARSITY = 0.99
WEI_BIT_ZERO = 3
ACT_SPARSITY = 0.5
ACT_BIT_ZERO = 3
ACT_PRECS = [8]
WEI_PRECS = [8]

print("WEI_SPARSITY", WEI_SPARSITY)
print("ACT_SPARSITY", ACT_SPARSITY)


######################################################
#Helpers

###############################################################
#SPARSE

def SparseOurModel(hardware_config, benchmark):
	N = 1024
	
	h = hardware_config["GENERAL"]

	pe = h['TI']*h['TN']*h['TKX']*h['TKY']*h['TX']*h['TY']*h['TB']

	hp = {}	
	for bb in benchmark:
		b = benchmark[bb]
		cycles = {}
		powers = {}

		#modify sparsity when there is no local re-use, or there is only reuse after a window
		wei_reuse = 1
		act_reuse = 1
		ACT  = ['B', 'I']
		if(h['INTER_PE_Y'] ):
			pass
		else:
			ACT.append("KX")
		if(h['INTER_PE_Y'] ):
			pass
		else:
			ACT.append("KY")

		wei_flag = 0
		act_flag = 0
		for var in h["LOOP_ORDER"][::-1]:
			if( wei_flag or var in ["N", "I", "KX", "KY"]):
				wei_reuse *= 1
				wei_flag = 1
			else:
				wei_reuse *= h["T"+var]

			if(act_flag or var in ACT):
				act_reuse *= 1
				act_flag = 1	
			else:	
				act_reuse *= h["T"+var]
			
		print("wei_reuse", "act_reuse")
		print(wei_reuse, act_reuse)
		input()
		in_a = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N, REUSE = act_reuse)
		in_w = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N, REUSE = wei_reuse)
		in_o = [in_w[idx] *in_a[idx] for idx in range(min(len(in_w), len(in_a)))]
	
		PE_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
			 (b['I']+h['TI']-1)//h['TI']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			




		INNER = h["TKX"]*h["TKY"]*h["TI"]

		ACC_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			

		#power cost, there is an added Parallel2Serial unit
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
		OUT_TILE = h['TB']*h["TX"]*h["TY"]*h["TN"]

		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 
	
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
					prec1 = hh["WEI_PREC"]
					prec2 = hh["ACT_PREC"]
					side_bits =1 -  b["WEI_BIT_ZERO"]/hh['WEI_PREC']
					in_0 = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N)
					in_1 = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N)
				else:
					in_0 = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N)
					in_1 = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N)
					side_cycle = hh["ACT_PREC"]/ratio				
					prec2 = hh["WEI_PREC"]
					prec1 = hh["ACT_PREC"]	
					side_bits =1 -  b["ACT_BIT_ZERO"]/hh['ACT_PREC']

				cc = min(len(in_0), len(in_1))
				in_0 = in_0[0:cc]
				in_1 = in_1[0:cc]
		
				#power model
				res = Multiplier2Block(h, hh, in_0, in_1, prec1, prec2, side, mode=modes)

				units = pe
				#powers[c] = res['Total_Pwr']['res'][-1] * units
				powers[c] = res['Total_Pwr']['res'][-1][-1] *units



			
			elif(component == "ADDER_TREE"):
			
				if(hh["ADDERN_TYPE"] == "AddTreeN"):
					side_cycle = 1
				if(hh["ADDERN_TYPE"] == "SimpleAdderN"):
					side_cycle = 1
	
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					side_cycle = INNER
				else:
					print("invalid ADDERN_TYPE", hh["ADDERN_TYPE"])
					exit()

				#power model
				if(hh["ADDERN_TYPE"] == "AddTreeN"):
					ap = AdderNPrimitive()
					input_data = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['PREC']],
					"prec_sum": [hh['OUT_PREC']],
					"terms": [INNER],
					"adderNType": [hh["ADDERN_TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					}	
					for t in range(INNER):
						input_data[f"in_{t}"] =[ in_o]
					res = ap.execute_testing(
					name = "AdderN",
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = input_data
					)
	
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					ap = AccumulatorPrimitive()
					res = ap.execute_testing(
					name = "Accumulator",
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['PREC']],
					"prec_out": [hh['OUT_PREC']],
					"terms": [1],
					"adderNType": [hh["ADDERN_TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					"in_0": [in_o],
					})

				units = pe // INNER
				#powers[c] = res['Total_Pwr']['res'][-1] * units
				powers[c] = res['Total_Pwr']['res'][-1][-1] *units




				pass
			elif(component == "ACCUMULATOR"):	
	
				ap = AccumulatorPrimitive()
				res = ap.execute_testing(
					name = "Accumulator",
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['ACCUM_PREC']],
					"prec_out": [hh['ACCUM_PREC']],
					"terms": [1],
					"adderNType": [hh["TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					"in_0": [in_a],
					})
				units = pe // INNER
				powers[c] = res['Total_Pwr']['res'][-1][-1] *units

				pass	

			elif(component == "OUT_LOADER"):	
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				ratio = hh['LOAD_RATIO']

				res_r, res_w = SRAMBlock(h, hh, in_a)
				res = NetworkBlock(h, hh,ratio, in_a)
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
	
				ratio = hh['LOAD_RATIO']

				res_r, res_w = SRAMBlock(h, hh, in_w)
				res = NetworkBlock(h, hh,ratio, in_w)
				units =  1/side_cycle * WEI_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	


				#print(res_r, res_w)
				#print(units)
				#input()	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}
				pass			
			elif(component == "ACT_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				ratio = hh['LOAD_RATIO']

				res_r, res_w = SRAMBlock(h, hh, in_a)
				res = NetworkBlock(h, hh,ratio, in_a)
				units =  1/side_cycle * ACT_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}	

			elif(component == "WEI_PE_CAST"):
				ratio = min(hh['CAST_RATIO']		, pe//WEI_TILE)
					
				fanout = (pe//WEI_TILE)//ratio	
				#print("WEI_CAST")
				#print(fanout, ratio)
				#print(WEI_TILE)
				#input()
				res = MulticastBlock(h, hh, ratio, np.repeat(in_w,1), fanout = (pe//WEI_TILE)//ratio )

				units = WEI_TILE* ratio
				res = res['Total_Pwr']['res'][-1][-1] *units 
				powers[c] = {"NETWORK": res}	
			elif(component == "ACT_PE_CAST"):
				ratio = min(hh['CAST_RATIO']		, pe//ACT_TILE)
				fanout = (pe//ACT_TILE)//ratio	#this is the maximum fanout, the real fanout is actually lower, 'diagonal' fanout, we can assume worst case for now
				#i.e. in practice, it should be ~1 2 2 2 2 1, 
				#WORST:TN*TKX*TKY 
				#APPROX: 
				#print("ACT_CAST")
				#print(fanout, ratio)
				#print(ACT_TILE)
				#input()
				res = MulticastBlock(h, hh, ratio, np.repeat(in_a, ratio), fanout = (pe//ACT_TILE)//ratio )
				units = ACT_TILE*ratio #can multiply by the array size, not the entire ACT_TILE if there are diagnoal movements
				
				res = res['Total_Pwr']['res'][-1][-1] *units 
				powers[c] = {"NETWORK": res}	
				pass
	
			elif(component == "L2"):
				pwrs = []
				for busunit,in_0,tile in [("ACT_LOADER", in_a,ACT_TILE), ("OUT_LOADER", in_o,OUT_TILE), ("WEI_LOADER", in_w,WEI_TILE)]:

					if((hh['BIT_LEN']//hh['PREC']) > tile):
						ratio = (hh['BIT_LEN']//hh['PREC']) // tile
					else:
						ratio = -tile //( hh['BIT_LEN']//hh['PREC'])

					if(ratio < 0):
						side = abs(ratio)
					else:
						side = 1/abs(ratio)
					#hh['PREC'] = h['WEI_PREC']
					res_r, res_w = SRAMBlock(h, hh, in_0)
					units =  1/side * tile #fillter for now
					#print("L2")
					#print(res_r, res_w)
					#print('ratio',ratio)
					#print('units',units)
					#print('side',side)
					#print('tile',tile)
					#input()
					res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]


					res = NetworkBlock(h, hh,ratio, in_0)
					res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	

					
					pwrs.append((res_r, res_w,res))	
				powers[c] = {
					"BUS": pwrs}

				pass
	
		#print(bb,cycles, max([cycles[t] for t in cycles]))
		#print(bb, hp)
		print(bb)
		pprint(powers)# max([cycles[t] for t in cycles]))
		#print(bb, hp)






	pass


#Simple Timing simulator
def DenseTimer(hardware_config, benchmark   ):
	h = hardware_config["GENERAL"]

	hp = {}	
	for bb in benchmark:
		b = benchmark[bb]
		cycles = {}
		PE_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
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
		OUT_TILE = h['TB']*h["TX"]*h["TY"]*h["TN"]

		TILE = h['TI']*h['TN']*h['TKX']*h['TKY']*h['TX']*h['TY']*h['TB']
		PE = TILE #// h["SPARSE_RATIO"]



		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 
	

		INNER = h["TKX"]*h["TKY"]*h["TI"]

		ACC_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			

		#power cost, there is an added Parallel2Serial unit
		if( h['INTER_PE_X']  ):
			X_CYCLES =  (b['X']+h['TX']+h['TKX']-1)//(h['TX']+h['TKX']-1)  * (b['KX']+h['TKX']-1)//h['TKX'] 
		else:
			X_CYCLES =   (b['X']+h['TX']-1)//h['TX'] 

		if( h['INTER_PE_Y']  ):
			Y_CYCLES =  (b['Y']+h['TY']+h['TKY']-1)//(h['TY']+h['TKY']-1)  * (b['KY']+h['TKY']-1)//h['TKY'] 
		else:
			Y_CYCLES =   (b['Y']+h['TY']-1)//h['TY'] 




		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 

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


		print("wei_reuse", "act_reuse")
		print(wei_reuse, act_reuse)

	
		in_a = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = h['ACT_PREC'], N = N, REUSE = act_reuse)
		in_w = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = h['WEI_PREC'], N = N, REUSE = wei_reuse)
		in_o = [in_w[idx] *in_a[idx] for idx in range(min(len(in_w), len(in_a)))]
	

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
				else:
					side_cycle = hh["ACT_PREC"]/ratio				
					side_bits = 1 - b["ACT_BIT_ZERO"]/hh['ACT_PREC']
		

				print(sparsity, PE_CYCLES, side_cycle)
				print(side_cycle, side_bits)
				input()
				if(hh["MULT_TYPE"] == "HighRadixMultiplier"):
					cycles[c] =sparsity * PE_CYCLES * side_cycle
				elif(hh["MULT_TYPE"] == "BitSerialMultiplier"):
					cycles[c] =sparsity * PE_CYCLES * max(1, side_cycle* side_bits)
				else:
					print(hh['MULT_TYPE'] + " does not exist")
					exit()
				
			
			elif(component == "ADDER_TREE"):


				if(hh["ADDERN_TYPE"] == "AddTreeN"):
					side_cycle = 1
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					side_cycle = INNER
				else:
					print("invalid ADDERN_TYPE", hh["ADDERN_TYPE"])
					exit()
	
				cycles[c] = PE_CYCLES * side_cycle
	
				pass
			elif(component == "ACCUMULATOR"):
				cycles[c] = PE_CYCLES 
	
				pass	

			elif(component == "OUT_LOADER"):	
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				#cycles[c] = ACC_CYCLES*side_cycle

				cycles[c+".write"] = ACC_CYCLES*side_cycle
				cycles[c+".read"] = ACC_CYCLES*side_cycle#PE_CYCLES/wei_reuse#/h['SPARSE_RATIO']



				pass
			elif(component == "WEI_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	

				cycles[c+".write"] = WEI_CYCLES*side_cycle
				cycles[c+".read"] = PE_CYCLES*side_cycle/wei_reuse

				cycles[c+".crossbar"] = PE_CYCLES*side_cycle/wei_reuse

			

				#cycles[c+".read"] =   PE_CYCLES/wei_reuse*side_cycle




				hp[c] = 1/side_cycle * WEI_TILE*hh['PREC']
				pass			
			elif(component == "ACT_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				cycles[c+".write"] = ACT_CYCLES*side_cycle
				cycles[c+".read"] = PE_CYCLES*side_cycle/act_reuse
				cycles[c+".crossbar"] = PE_CYCLES*side_cycle/act_reuse



	
				cycles[c] = ACT_CYCLES* side_cycle
				hp[c] = 1/side_cycle * WEI_TILE*hh['PREC']
	
				pass
			elif(component == "WEI_PE_CAST"):


				cycles[c] = PE_CYCLES/wei_reuse *hh['CAST_RATIO']		
				pass
			elif(component == "ACT_PE_CAST"):
				cycles[c] =PE_CYCLES/act_reuse  *hh['CAST_RATIO']		
				pass
	
			elif(component == "L2"):
				#if(hh['LOAD_RATIO']< 0):
				#	side_cycle = abs(hh['LOAD_RATIO'])
				#else:
				#	side_cycle = 1/abs(hh['LOAD_RATIO'])

				cycles[c] = 0
				pwrs = []
				for busunit,tile,cycles_0 in [("ACT_LOADER", ACT_TILE, ACT_CYCLES), ("OUT_LOADER", OUT_TILE,ACC_CYCLES), ("WEI_LOADER", WEI_TILE, WEI_CYCLES)]:

					if(hh['BIT_LEN']//hh['PREC'] > tile):
						ratio = hh['BIT_LEN']//hh['PREC'] // tile
					else:
						ratio = -tile //( hh['BIT_LEN']//hh['PREC'])

					if(ratio < 0):
						side = abs(ratio)
					else:
						side = 1/abs(ratio)
					cycles[c] += cycles_0*side	
					#cycles[c] = WEI_CYCLES*side_cycle + ACT_CYCLES*side_cycle + ACC_CYCLES*side_cycle		
	
		print("cycles")
		




		print(bb,cycles, max([cycles[t] for t in cycles]))
		#print(bb, hp)


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


	DenseConv_0 = {
		"GENERAL": {"LOOP_ORDER": ["B","I","X","Y","N", "KX", "KY"],"TB": 1,"TN": 16,"TI": 16,"TX": 1,"TY": 1,"TKX": 1,"TKY": 1,"CLOCK": 1,"cap_load": 0.1,"tech":"tsmc40","INTER_PE_X": False,"INTER_PE_Y": False, "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC },
		"PE_ARRAY": {"ACT_PREC": ACT_PREC,"WEI_PREC": WEI_PREC,"MULT_TYPE": "BitSerialMultiplier","MULT_SIDE": "input","MULT_RADIX": 1<<8,"MULT_CORE_ADDER_TYPE": "SimpleAdder2",},
		"ADDER_TREE":{"ADDERN_TYPE": "AddTreeN","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC,"OUT_PREC": ACT_PREC+WEI_PREC,"DEPTH": 1, },	
		"ACCUMULATOR": {"TYPE": "AccumulatorN","CORE_ADDER_TYPE": "SimpleAdder2","ACCUM_PREC": ACT_PREC+WEI_PREC,},
		"WEI_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -4,"PREC": WEI_PREC},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC+WEI_PREC},
		"WEI_PE_CAST":{"CAST_RATIO": 1,"PREC": WEI_PREC,"NETWORK_TYPE": "Mux",},
		"ACT_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	print(DenseConv_0)
	benchmark_filter = {}
	for bb in benchmark:
		b = benchmark[bb]		
		if("Conv" in bb):
			benchmark_filter[bb] = b


	DenseTimer(DenseConv_0, benchmark_filter   )
