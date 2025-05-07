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


from DSE import MulticastBlock, NetworkBlock, SRAMBlock, AdderNBlock,Multiplier2Block,MuxBlock, dict_values_to_str, valid_file
#####################################################
debug_sbt = 1

GLOBAL_RUNS = 0
START_RUN = 0#3000#656 #38#388#5#125#-1
COMPONENT_SELECT = []#"WEI_LOADER"]#"ADDER_TREE"]
PRIM_SELECT = []#"Network"]
MODES = [2]#[1,2,0]#0-golden, 1-b1, 2-b2
UNIT = "SparseConvB2"

N = 128

PREC = 8
ACT_PREC = 8
WEI_PREC = 8


WEI_SPARSITY = 0.2
WEI_BIT_ZERO = 4
ACT_SPARSITY = 0.1
ACT_BIT_ZERO = 4
ACT_PRECS = [8]
WEI_PRECS = [8]

print("WEI_SPARSITY", WEI_SPARSITY)
print("ACT_SPARSITY", ACT_SPARSITY)


######################################################
#Helpers

###############################################################
#SPARSE
#Simple Timing simulator
def SparseTimer(hardware_config, benchmark , power = True  ):
	h = hardware_config["GENERAL"]

	hp = {}	
	for bb in benchmark:
		b = benchmark[bb]
		cycles = {}
		powers = {}
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
		PE = TILE // h["SPARSE_RATIO"]
		
		INNER_TILE =  h['TI']*h['TKX']*h['TKY']



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


		#print("wei_reuse", "act_reuse")
		#print(wei_reuse, act_reuse)

	
		in_a = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = h['ACT_PREC'], N = N, REUSE = act_reuse)
		in_w = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = h['WEI_PREC'], N = N, REUSE = wei_reuse)
		in_w_orig = in_w
		in_a_orig = in_a



		in_o = [in_w[idx] *in_a[idx] for idx in range(min(len(in_w), len(in_a)))]
		in_o_orig = in_o

		OUT_SPARSITY = 1 - in_o.count(0)/len(in_o)
	
		#is compressed
		if(h['SPARSE_SIDE'] ==  "weights" ):
			sparsity_side = 1-b['WEI_SPARSITY'] #* sparsity_ratio	
			w_sparse = 0
			a_sparse = b['ACT_SPARSITY']
		elif(h['SPARSE_SIDE'] == 'inputs'):
			sparsity_side = 1-b['ACT_SPARSITY'] #* sparsity_ratio
			w_sparse = b['WEI_SPARSITY']
			a_sparse = 0
		elif(h["SPARSE_SIDE"] == "both"):
			sparsity_side = 1 - in_o.count(0)/len(in_o)
			w_sparse = b['WEI_SPARSITY']
			a_sparse = b['ACT_SPARSITY']
	
	

		sparsity = max(sparsity_side, 1/h['SPARSE_RATIO'])

		in_a = gen_in(   a_sparse , b['ACT_BIT_ZERO'], prec = h['ACT_PREC'], N = N, REUSE = act_reuse)
		in_w = gen_in(   w_sparse , b['WEI_BIT_ZERO'], prec = h['WEI_PREC'], N = N, REUSE = wei_reuse)
		#print(in_w)
		#print(in_w_orig)
		#input()
		ACT_SPARSITY = 1 - in_a.count(0)/len(in_a)
		WEI_SPARSITY = 1 - in_w.count(0)/len(in_w)
	
	

		in_o = [in_w[idx] *in_a[idx] for idx in range(min(len(in_w), len(in_a)))]



		#cut
		in_a = in_a[0:N]
		in_w = in_w[0:N]
		in_a_orig = in_a_orig[0:N]
		in_w_orig = in_w_orig[0:N]
		in_o = in_o[0:N]
		in_o_orig = in_o_orig[0:N]
	
	
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
					in_0 = in_w#.reshape((-1)).tolist()#in_w
					in_1 = in_a#.reshape((-1)).tolist()#in_a
					prec1 = hh["WEI_PREC"]
					prec2 = hh["ACT_PREC"]
					main_sparse = WEI_SPARSITY

				elif(side == "input"):
			

					side_cycle = hh["ACT_PREC"]/ratio				
					side_bits = 1 - b["ACT_BIT_ZERO"]/hh['ACT_PREC']
					in_0 = in_a#.reshape((-1)).tolist()#in_w
					in_1 = in_w#.reshape((-1)).tolist()#in_a
					prec2 = hh["WEI_PREC"]
					prec1 = hh["ACT_PREC"]
					main_sparse = ACT_SPARSITY

				else:
					side_cycle = hh["WEI_PREC"]/ratio
					side_bits = 1 - b["WEI_BIT_ZERO"]/hh['WEI_PREC']
					in_0 = in_w#.reshape((-1)).tolist()#in_w
					in_1 = in_a#.reshape((-1)).tolist()#in_a
					prec1 = hh["WEI_PREC"]
					prec2 = hh["ACT_PREC"]
					main_sparse = WEI_SPARSITY
	

				sparsity = max(1/h["SPARSE_RATIO"], main_sparse)
				#print(sparsity, PE_CYCLES, side_cycle)
				#print(side_cycle, side_bits)
				#input()
				if(hh["MULT_TYPE"] == "HighRadixMultiplier"):
					cycles[c] = sparsity * PE_CYCLES * side_cycle
					#main_sparse = b['WEI_SPARSITY']
					main_sparse  = 1 - in_w.count(0)/len(in_w)

			
				elif(hh["MULT_TYPE"] == "BitSerialMultiplier"):
					cycles[c] =sparsity * PE_CYCLES * max(1, side_cycle* side_bits)
					main_sparse = 1 - in_a.count(0)/len(in_a)

			
				else:
					print(hh['MULT_TYPE'] + " does not exist")
					exit()

				if(power):

					cc = min(len(in_0), len(in_1))
					in_0 = in_0[0:cc]
					in_1 = in_1[0:cc]
					
					res = Multiplier2Block(h, hh, in_0, in_1, prec1, prec2, side, sparsity = main_sparse,mode=MODES,PRIM_SELECT=PRIM_SELECT  )
					units = PE
					powers[c] = res['Total_Pwr']['res'][-1][-1] *units
					#input()
				
					#input("ok?")	
			
			elif(component == "ADDER_TREE"):


				if(hh["ADDERN_TYPE"] in ["AddTreeN", "SimpleAdderN"  ]):
					side_cycle = 1
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					side_cycle = INNER
				else:
					print("invalid ADDERN_TYPE", hh["ADDERN_TYPE"])
					exit()
	
				cycles[c] = PE_CYCLES/h['SPARSE_RATIO'] * side_cycle

				#POWER MODELING
				if(power):
					in_0 = in_o
					res = AdderNBlock( h, hh, in_o ,  hh["PREC"],  mode=MODES, sparsity= 1 - in_o.count(0)/len(in_o), INNER = INNER//h['SPARSE_RATIO'], PRIM_SELECT=PRIM_SELECT)


					units = OUT_TILE/h['SPARSE_RATIO']
					powers[c] = res['Total_Pwr']['res'][-1][-1] *units

	
				pass
			elif(component == "ACCUMULATOR"):
				cycles[c] = PE_CYCLES /h['SPARSE_RATIO']
				if(power):
					in_0 = in_o_orig
					in_o = in_0
					res = AdderNBlock( h, hh, in_0 ,  hh["PREC"],  mode=MODES, sparsity= 1 - in_o.count(0)/len(in_o), INNER = INNER//h['SPARSE_RATIO'], PRIM_SELECT=PRIM_SELECT)

					units = OUT_TILE
					powers[c] = res['Total_Pwr']['res'][-1][-1] *units
	
			
	
				pass	

			elif(component == "OUT_LOADER"):	
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				#cycles[c] = ACC_CYCLES*side_cycle

				cycles[c+".write"] = ACC_CYCLES/h['SPARSE_RATIO']*side_cycle
				cycles[c+".read"] = ACC_CYCLES/h['SPARSE_RATIO']*side_cycle#PE_CYCLES/wei_reuse#/h['SPARSE_RATIO']

				if(power):
					ratio = hh['LOAD_RATIO']
					OUT_SPARSITY = 1 - in_o_orig.count(0)/len(in_o_orig)
	
					res_r = SRAMBlock(h, hh, in_o, sparsity = OUT_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
					res_w = SRAMBlock(h, hh, in_o, sparsity = OUT_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)
					res = NetworkBlock(h, hh,ratio, in_o, sparsity = OUT_SPARSITY, mode=MODES, fanout = 1, PRIM_SELECT=PRIM_SELECT)
	
					if(hh["COMPRESS"]==True):
						units =  1/side_cycle * OUT_TILE/h["SPARSE_RATIO"]*hh['PREC'] #fillter for now
					else:
						units =  1/side_cycle * OUT_TILE*hh['PREC'] #fillter for now

					res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	
					powers[c] = {
						"SRAM": [res_r, res_w],
					"NETWORK": res}
	
					if(hh["COMPRESS"]==True):
						prec_in = hh['PREC']
						in_terms = OUT_TILE
						res_mux = MuxBlock(h, hh, in_0=in_w_orig, prec_in = prec_in, in_terms=in_terms, sparsity=WEI_SPARSITY, PRIM_SELECT=PRIM_SELECT)
						out_terms = in_terms/h["SPARSE_RATIO"] 
						units =  OUT_TILE * out_terms #fillter for now
						res_mux = res_mux['Total_Pwr']['res'][-1][-1] * units		
						powers[c]["CROSSBAR"] =  res_mux

				pass
			elif(component == "WEI_LOADER"):
				if(hh["COMPRESS"] == True):
					WEI_CYCLES = WEI_CYCLES * (1 - b['WEI_SPARSITY'])


				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	

				cycles[c+".write"] = WEI_CYCLES*side_cycle
				cycles[c+".read"] = PE_CYCLES*side_cycle/wei_reuse/h['SPARSE_RATIO']

				cycles[c+".crossbar"] = PE_CYCLES*side_cycle/wei_reuse/h['SPARSE_RATIO']

			

				#cycles[c+".read"] =   PE_CYCLES/wei_reuse*side_cycle

				if(power):
					ratio = hh['LOAD_RATIO']
					res_r = SRAMBlock(h, hh, in_w_orig, sparsity = WEI_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
					res_w = SRAMBlock(h, hh, in_w_orig, sparsity = WEI_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)
					res = NetworkBlock(h, hh,ratio, in_w_orig, sparsity = WEI_SPARSITY, mode = MODES, fanout = 1, PRIM_SELECT=PRIM_SELECT)	
					units =  1/side_cycle * WEI_TILE*hh['PREC'] #fillter for now
					res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	

					prec_in = h['WEI_PREC']
					in_terms = INNER_TILE
					#print(in_w_orig)
					res_mux = MuxBlock(h, hh, in_0=in_w_orig, prec_in = prec_in, in_terms=in_terms, sparsity=WEI_SPARSITY, PRIM_SELECT=PRIM_SELECT, mode = MODES)
					out_terms = in_terms/h["SPARSE_RATIO"] 
					units =  h['TN'] * out_terms #fillter for now
					res_mux = res_mux['Total_Pwr']['res'][-1][-1] * units	
			
	


					powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res, 
					"CROSSBAR": res_mux  ,}

					#If weight is compressed, need to get the zero map, zero run length encoding from the SRAM
					if(hh["COMPRESS"] == True):
						ratio = hh['LOAD_RATIO']
						res_r = SRAMBlock(h, hh, in_w_orig, sparsity = WEI_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
						res_w = SRAMBlock(h, hh, in_w_orig, sparsity = WEI_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)
						units =  1/side_cycle * WEI_TILE*hh['PREC'] #fillter for now
						res_r = res_r['Total_Pwr']['res'][-1][-1] *units / (hh['SRAM_SIZE'][0] * hh['PREC'])
						res_w = res_w['Total_Pwr']['res'][-1][-1] *units / (hh['PREC'] * hh['SRAM_SIZE'][0] )

						powers[c].update({
					"ZMAP_SRAM": [res_r, res_w], })





	


				hp[c] = 1/side_cycle * WEI_TILE*hh['PREC']
				pass			
			elif(component == "ACT_LOADER"):
				if(hh["COMPRESS"] == True):
					ACT_CYCLES = ACT_CYCLES * (1-b['ACT_SPARSITY'])


				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				cycles[c+".write"] = ACT_CYCLES*side_cycle
				cycles[c+".read"] = PE_CYCLES*side_cycle/act_reuse/h['SPARSE_RATIO']
				cycles[c+".crossbar"] = PE_CYCLES*side_cycle/act_reuse/h['SPARSE_RATIO']



				if(power):
					ratio = hh['LOAD_RATIO']
					res_r = SRAMBlock(h, hh, in_a_orig, sparsity = ACT_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
					res_w = SRAMBlock(h, hh, in_a_orig, sparsity = ACT_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)
					res = NetworkBlock(h, hh,ratio, in_a_orig, sparsity = ACT_SPARSITY, mode = MODES, fanout = 1, PRIM_SELECT=PRIM_SELECT)	
					units =  1/side_cycle * ACT_TILE*hh['PREC'] #fillter for now
					res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	

					prec_in = h['ACT_PREC']
					in_terms = INNER_TILE
					res_mux = MuxBlock(h, hh, in_0=in_a_orig, prec_in = prec_in, in_terms=in_terms, sparsity=ACT_SPARSITY, PRIM_SELECT=PRIM_SELECT, mode = MODES)
					out_terms = in_terms/h["SPARSE_RATIO"] 
					units =  h['TB']*h['TX']*h['TY'] * out_terms #fillter for now
					res_mux = res_mux['Total_Pwr']['res'][-1][-1] * units	
				


					powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res, 
					"CROSSBAR": res_mux  ,}
	


					#If weight is compressed, need to get the zero map, zero run length encoding from the SRAM
					if(hh["COMPRESS"] == True):
						ratio = hh['LOAD_RATIO']
						res_r = SRAMBlock(h, hh, in_a_orig, sparsity = ACT_SPARSITY, rw_mode = 0,mode = MODES, PRIM_SELECT=PRIM_SELECT)
						res_w = SRAMBlock(h, hh, in_a_orig, sparsity = ACT_SPARSITY , rw_mode = 1,mode = MODES, PRIM_SELECT=PRIM_SELECT)
						units =  1/side_cycle * ACT_TILE*hh['PREC'] #fillter for now
						res_r = res_r['Total_Pwr']['res'][-1][-1] *units / (hh['SRAM_SIZE'][0] * hh['PREC'])
						res_w = res_w['Total_Pwr']['res'][-1][-1] *units / (hh['PREC'] * hh['SRAM_SIZE'][0] )

						powers[c].update({
					"ZMAP_SRAM": [res_r, res_w], })





	
				cycles[c] = ACT_CYCLES* side_cycle
				hp[c] = 1/side_cycle * WEI_TILE*hh['PREC']
	
				pass
			elif(component == "WEI_PE_CAST"):

				ratio = hh['CAST_RATIO']
				cycles[c] = PE_CYCLES/wei_reuse/h['SPARSE_RATIO'] *hh['CAST_RATIO']		
				if(power):
					pe = PE
					res = MulticastBlock(h, hh, ratio, np.repeat(in_w,1), fanout = h['TB']*h['TX']*h['TY']//ratio , PRIM_SELECT=PRIM_SELECT, mode=MODES)
					units = WEI_TILE//h['SPARSE_RATIO']*ratio
					res = res['Total_Pwr']['res'][-1][-1] *units 
					powers[c] = {"NETWORK": res}	
	
				pass

			elif(component == "ACT_PE_CAST"):

				ratio = hh['CAST_RATIO']

				cycles[c] =PE_CYCLES/act_reuse/h["SPARSE_RATIO"]  *hh['CAST_RATIO']		

				if(power):
					pe = PE
					res =MulticastBlock(h, hh, ratio, np.repeat(in_a, 1), fanout = (pe//ACT_TILE)//ratio , PRIM_SELECT=PRIM_SELECT, mode = MODES)
					units = ACT_TILE//h['SPARSE_RATIO']*ratio
					res = res['Total_Pwr']['res'][-1][-1] *units 
					powers[c] = {"NETWORK": res}	



				pass
	
			elif(component == "L2"):
				#if(hh['LOAD_RATIO']< 0):
				#	side_cycle = abs(hh['LOAD_RATIO'])
				#else:
				#	side_cycle = 1/abs(hh['LOAD_RATIO'])

				cycles[c] = 0
				pwrs = []
				for busunit,tile,cycles_0 in [("ACT_LOADER", ACT_TILE, ACT_CYCLES/h['SPARSE_RATIO']), ("OUT_LOADER", OUT_TILE,ACC_CYCLES/h['SPARSE_RATIO']), ("WEI_LOADER", WEI_TILE, WEI_CYCLES/h['SPARSE_RATIO'])]:

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
	
		#print("cycles")
		




		#print(bb,cycles, max([cycles[t] for t in cycles]))
		#print(bb, hp)
		#print(powers)
		#print(cycles)
	#exit()
	return cycles, powers
	


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


	SparseConv_0 = {
		"GENERAL": {"LOOP_ORDER": ["B","I","X","Y","N", "KX", "KY"],"TB": 1,"TN": 32,"TI": 16,"TX": 1,"TY": 1,"TKX": 1,"TKY": 1,"CLOCK": 1,"cap_load": 0.1,"tech":"tsmc40","INTER_PE_X": False,"INTER_PE_Y": False, "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC, "SPARSE_RATIO": 4, "SPARSE_SIDE": "weights", },
		"PE_ARRAY": {"ACT_PREC": ACT_PREC,"WEI_PREC": WEI_PREC,"MULT_TYPE": "HighRadixMultiplier","MULT_SIDE": "input","MULT_RADIX": 2,"MULT_CORE_ADDER_TYPE": "SimpleAdder2",},
		"ADDER_TREE":{"ADDERN_TYPE": "AddTreeN","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC,"OUT_PREC": ACT_PREC+WEI_PREC,"DEPTH": 1, },	
		"ACCUMULATOR": {"ADDERN_TYPE": "Accumulator","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC, "OUT_PREC": ACT_PREC+WEI_PREC,},
		"WEI_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -4,"PREC": WEI_PREC,"COMPRESS":"none", "CROSSBAR_TYPE": "Full",},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC,"COMPRESS":"none", "CROSSBAR_TYPE": "Full"},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC+WEI_PREC,"COMPRESS":"none", "CROSSBAR_TYPE": "Full"},
		#"WEI_CROSSBAR": {"PREC": 8, "TYPE": "full"},
		#"ACT_CROSSBAR": {"PREC": 8, "TYPE": "full"},
		#"OUT_CROSSBAR": {"PREC": 8, "TYPE": "full"},
		"WEI_PE_CAST":{"CAST_RATIO": 1,"PREC": WEI_PREC,"NETWORK_TYPE": "Mux",},
		"ACT_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}
	benchmark_filter = {}
	for bb in benchmark:
		b = benchmark[bb]		
		if("Conv" in bb):
			if(1):
				#if(b['KX'] == WinoConv_0["GENERAL"]["TKX"] and b['KY'] == WinoConv_0["GENERAL"]["TKY"]):
				#print(bb)
				#print(b)
				#input()
				benchmark_filter[bb] = b
	#exit()


	print(SparseConv_0)
	time_res, power_res = SparseTimer(SparseConv_0, benchmark_filter ,power=True  )
	print(time_res)
	print(power_res)



if __name__ == "__ma2in__":
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


	SparseConv_0 = {
		"GENERAL": {"LOOP_ORDER": ["B","I","X","Y","N", "KX", "KY"],"TB": 1,"TN": 16,"TI": 16,"TX": 1,"TY": 1,"TKX": 1,"TKY": 1,"CLOCK": 1,"cap_load": 0.1,"tech":"tsmc40","INTER_PE_X": False,"INTER_PE_Y": False, "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC, "SPARSE_RATIO": 8, "SPARSE_SIDE": "weights", },
		"PE_ARRAY": {"ACT_PREC": ACT_PREC,"WEI_PREC": WEI_PREC,"MULT_TYPE": "BitSerialMultiplier","MULT_SIDE": "input","MULT_RADIX": 1<<8,"MULT_CORE_ADDER_TYPE": "SimpleAdder2",},
		"ADDER_TREE":{"ADDERN_TYPE": "AddTreeN","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC,"OUT_PREC": ACT_PREC+WEI_PREC,"DEPTH": 1, },	
		"ACCUMULATOR": {"ADDERN_TYPE": "Accumulator","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC, "OUT_PREC": ACT_PREC+WEI_PREC,},
		"WEI_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -4,"PREC": WEI_PREC,"COMPRESS":False, "CROSSBAR_TYPE": "Full",},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC,"COMPRESS":False, "CROSSBAR_TYPE": "Full"},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -1,"PREC": ACT_PREC+WEI_PREC,"COMPRESS":False, "CROSSBAR_TYPE": "Full"},
		#"WEI_CROSSBAR": {"PREC": 8, "TYPE": "full"},
		#"ACT_CROSSBAR": {"PREC": 8, "TYPE": "full"},
		#"OUT_CROSSBAR": {"PREC": 8, "TYPE": "full"},
		"WEI_PE_CAST":{"CAST_RATIO": 1,"PREC": WEI_PREC,"NETWORK_TYPE": "Mux",},
		"ACT_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	#filter benchmark for only ones that are valid
	benchmark_filter = {}
	for bb in benchmark:
		b = benchmark[bb]		
		if("Conv" in bb):
			benchmark_filter[bb] = b

	benchmark = benchmark_filter
	def ArchTimer(core, mapping, benchmarks=benchmark, FILTER=[]):
		global GLOBAL_RUNS
		global START_RUN
		global COMPONENT_SELECT

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
				base_file = valid_file(f"generated/DSE/FIRST_PASS/Conv/{UNIT}/{GEN}/{FILTER[0]}/{COMP}/{benchmark}.{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}")


				time_res, power_res = SparseTimer(base_hardware_config, {benchmark:benchmarks[benchmark]})#, FILTER=FILTER)	
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
	Conv_0 = "SparseConv_0"#"SystolicConv_0"
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
		[1, 8,   8,1,  1,  1,1],
		[1, 16,   16,1,  1,  1,1],
		[1, 12,   12,1,  1,  1,1],
		[1, 12,   8,1,  1,  1,1],	
		[1, 4,   4,2,  2,  1,1],
 		[1, 4,   4,1,  1,  2,2],
 		[1, 4,   4,2,  1,  2,1],
  		[1, 2,   2,2,  2,  2,2],
  		[2, 1,   2,2,  2,  2,2],
  		[1, 16,  1,1,  1,  1,1],  
  		[1, 4,  16,1,  1,  1,1],   
 	       	[1,8,  8,1,  1,  2,2],
        	[1,8,  8,1,  2,  1,2],	
        	[1,16,  4,1,  2,  1,2],	
       		[1,4,  16,2,  2,  1,2],			
        	[2,4,  8,2,  2,  1,1],			
	       	[2,2,  16,2,  2,  1,1],			
	       	[1,8,  32,1,  1,  1,1],			
		]

	accelerator_core = {
		"SparseConv_0": SparseConv_0
	}


	#1st pass
	#hc = accelerator_core
	hc = SparseConv_0#WinoConv_0#accelerator_core["SystolicConv_0"]
	#for clock in [1]:
		#for cap_load in [0.1]:
	for ACT_PREC in ACT_PRECS:
		for WEI_PREC in WEI_PRECS:
			for inter_x in [True,False]:
				for inter_y in [True,False]:	
					for lp in LOOP_ORDERS:
						for sparse_side in ['weights', 'inputs','both']:			
							for tb,tn, ti,tx, ty,tkx,tky in TILINGS:		
								for sparse_ratio in [2,4,8,16,32,64]:
									if(sparse_ratio > ti*tkx*tky):
										continue
									#GENERAL
									hc["GENERAL"]["LOOP_ORDER"] = lp
									hc["GENERAL"]["TB"] =  tb
									hc["GENERAL"]["TI"] =  ti
									hc["GENERAL"]["TN"] =  tn
									hc["GENERAL"]["TX"] =  tx
									hc["GENERAL"]["TY"] =  ty
									hc["GENERAL"]["TKX"] =  tkx
									hc["GENERAL"]["TKY"] =  tky			
			
									hc["GENERAL"]["SPARSE_RATIO"] =  sparse_ratio
									hc["GENERAL"]["SPARSE_SIDE"] =  sparse_side



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
													MULT_RADIX = 1<<RADIX
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
														for COMPRESS in [True, False]:
														
															hc[FILTER]['NETWORK_TYPE'] = NETWORK_TYPE
															hc[FILTER]['LOAD_RATIO'] = LOAD_RATIO
															hc[FILTER]['COMPRESS'] = COMPRESS
		
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



