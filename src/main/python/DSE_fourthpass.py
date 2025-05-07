#based on the pareto, get the designs from the golden flow
import os
import json
import numpy as np
import pandas as pd
import itertools
from DSE import valid_file, SystolicTimer,SystolicOurModel, dict_values_to_str
import matplotlib.pyplot as plt
import random
from DSE_secondpass import find_inner,find_inner_wino
WEI_PREC = 8
ACT_PREC = 8	
PREC = 8
POWER_MODE = "AVG"
def sum_nested(data):
    if isinstance(data, (int, float)):
        return data
    elif isinstance(data, (list, tuple)):
        return sum(sum_nested(item) for item in data)
    elif isinstance(data, dict):
        return sum(sum_nested(v) for v in data.values())
    else:
        return 0  # 忽略非数字类型




def get_benchmark(WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO):

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

	benchmark.update(Bottleneck(2,56,64,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(3,56,256,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(4,28,512,256,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(5,14,1024,512,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)

	benchmark_filter = {}
	for bb in benchmark:
		b = benchmark[bb]		
		if("Conv" in bb):
			#if(b['KX'] == WinoConv_0["GENERAL"]["TKX"] and b['KY'] == WinoConv_0["GENERAL"]["TKY"]):
			#print(bb)
			#print(b)
			#input()
			benchmark_filter[bb] = b
	


	return benchmark_filter

def get_systolic_comp(component, config):
	SystolicConv_0 = {
		"GENERAL": {"LOOP_ORDER": ["B","I","X","Y","KX","KY","N"],"TB": 1,"TN": 16,"TI": 16,"TX": 1,"TY": 1,"TKX": 1,"TKY": 1,"CLOCK": 1,"cap_load": 0.1,"tech":"tsmc40","INTER_PE_X": False,"INTER_PE_Y": False, "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC},
		"PE_ARRAY": {"ACT_PREC": ACT_PREC,"WEI_PREC": WEI_PREC,"MULT_TYPE": "BitSerialMultiplier","MULT_SIDE": "input","MULT_RADIX": 1<<8,"MULT_CORE_ADDER_TYPE": "SimpleAdder2",},
		"ADDER_TREE":{"ADDERN_TYPE": "AddTreeN","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC,"OUT_PREC": ACT_PREC+WEI_PREC,"DEPTH": 1, },	
		"ACCUMULATOR": {"TYPE": "Accumulator","CORE_ADDER_TYPE": "SimpleAdder2","ACCUM_PREC": ACT_PREC+WEI_PREC,},
		"WEI_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": WEI_PREC,},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC+WEI_PREC,},
		"WEI_PE_CAST":{"CAST_RATIO": 1,"PREC": WEI_PREC,"NETWORK_TYPE": "Mux",},
		"ACT_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC},
		}

	#print(component, config)
	specs= SystolicConv_0[component]
	#print(specs)
	cc = config.split("_")
	c_idx = 0
	#print(specs)
	#for s in specs:
	#	print(type(specs[s]),specs[s],s)
	#input("OK?")
	for s_idx,s in enumerate(specs):
		#if(s == "SRAM_SIZE" or s == in "LOOP_ORDER"):
		#	olen(s)
		x = specs[s]
		#	print(s,x)
		if type(x) is int :    # 判断字符串
			specs[s] = int(cc[c_idx])
			c_idx += 1	
		elif type(x) is str:    # 判断字符串
			specs[s] = cc[c_idx]
			c_idx += 1
		elif type(x) is float :    # 判断字符串
			specs[s] = float(cc[c_idx])
			c_idx += 1
		elif type(x) is bool:    # 判断字符串
			specs[s] = bool(cc[c_idx])
			c_idx += 1

		elif type(x) is list: # 判断列表
			#print('ist list')
			l = []
			for k in range(len(x)):
				#print(s, cc[c_idx], end=",")
				if(type(x[0]) is int):
					l.append(int(cc[c_idx]))
				else:
					l.append(cc[c_idx])
				c_idx += 1
			specs[s] = l#cc[c_idx]
			#print()
		else:
			print(x,' unknown')
			exit()
		#print(s, cc[c_idx])
		#print(s, c)
		#input()
	#print(SystolicConv_0)	
	return specs

#OUTPUT DSE results
#Several methods, one for each type and then we have a final one for reconfigurable designs
if __name__ == "__main2__":

	############################
	START_IDX = 155
	SAMPLE = 1000
	OVERWRITE = True
	############################

	#GREEDY APPROACH
	# from conv units, say 300,000 pick paraeto curve ~10 for example
	# out of 10
	#find several pareto points

	#(TODOS) add winograd, sparse architectures as well
	import matplotlib.pyplot as plt
	for orig_base, base3, save, unit in zip([ "generated/DSE/SECOND_PASS/Conv/SystolicConv/0.1_0.1_0_0"   ,
			   "generated/DSE/SECOND_PASS/Conv/WinogradConv/0.1_0.1_4_4"   ,
			   "generated/DSE/SECOND_PASS/Conv/SparseConv/0.2_0.1_4_4"
			  ], 
			[
	"generated/DSE/FIRST_PASS/Conv/SystolicConv",
	"generated/DSE/FIRST_PASS/Conv/WinogradConv",
	"generated/DSE/FIRST_PASS/Conv/SparseConv",
			],

			[
	"generated/DSE/THIRD_PASS/Conv/SystolicConvPareto.csv",
	"generated/DSE/THIRD_PASS/Conv/WinogradConvPareto.csv",
	"generated/DSE/THIRD_PASS/Conv/SparseConvPareto.csv"
			],
	["SystolicConv",
	"WinogradConv",
	"SparseConv"]

):
		#{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}
		benchie = orig_base.split("/")[-1].split("_")
		WEI_SPARSITY = float(benchie[0])
		ACT_SPARSITY = float(benchie[1])
		WEI_BIT_ZERO = int(benchie[2])
		ACT_BIT_ZERO = int(benchie[3])

		#get_benchmark(	
		benchmark = get_benchmark(WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)

		
		pareto = pd.read_csv(save)	
		

		#get the golden
		def get_golden(row):
			#print(row)
			#print(row['component'])
			comp = row['component'].replace("'","").replace("[","").replace("]","").replace(" ","").split(",")
			general = row['name']
			#print(general, row['combo'])
			#input()
			gen_specs = get_systolic_comp("GENERAL", general)
			#print(specs)
			for c in comp:
				config = c.split("/")[-1]
				component = c.split("/")[-2]
				if(unit == "SystolicConv"):
					#map from c to 
					#config parser
					
					specs = get_systolic_comp(component, config)
					#print(specs)
					
					hc = {}
					hc.update({
						"GENERAL": gen_specs,
						component: specs,
					})
					#print(hc)

					print(hc)
					res = SystolicOurModel(hardware_config=hc, benchmark=benchmark, modes = [3])
					#print(res)
					#input()				

				else:
					pass	
			input("one-design")
		pareto.apply(get_golden, axis=1)
		exit()


if __name__ == "__main__":

	############################
	START_IDX = 155
	SAMPLE = 1000
	OVERWRITE = True
	#UNIT = "SystolicConvOur"
	#UNIT = "SystolicConvB2"
	#UNIT = "SystolicConvB1"
	UNIT = "SystolicConvOurGolden"
	#UNIT = "WinogradConv"
	#UNIT = "SparseConv"



	
	SECOND = "SECOND_PASS"
	#WORK_LOAD = "0.5_0.5_3_3"
	WORK_LOAD = "0.1_0.1_0_0"

	############################

	#GREEDY APPROACH
	# from conv units, say 300,000 pick paraeto curve ~10 for example
	# out of 10
	#find several pareto points

	#(TODOS) add winograd, sparse architectures as well
	import matplotlib.pyplot as plt
	for orig_base, base3, save, unit in zip([ 
		f"generated/DSE/{SECOND}/Conv/{UNIT}/{WORK_LOAD}"   ,
			  ], 
			[
		f"generated/DSE/FIRST_PASS/Conv/{UNIT}",
			],

			[
		f"generated/DSE/THIRD_PASS/Conv/{UNIT}Pareto.csv",
			],
	["SystolicConv",
	]

):
		#{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}
		benchie = orig_base.split("/")[-1].split("_")
		WEI_SPARSITY = float(benchie[0])
		ACT_SPARSITY = float(benchie[1])
		WEI_BIT_ZERO = int(benchie[2])
		ACT_BIT_ZERO = int(benchie[3])

		#get_benchmark(	
		benchmark = get_benchmark(WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)

		
		pareto = pd.read_csv(save)	
		
		

		#get the golden
		#def get_golden(row):
		df = pareto
		print(len(df))
		#input()
		for index, row in df.iterrows():
			save_powers = {}
			save_times = {}

			#print(row)
			#print(row['component'])
			comp = row['component'].replace("'","").replace("[","").replace("]","").replace(" ","").split(",")
			general = row['name']
			#print(general, row['combo'])
			#input()
			gen_specs = get_systolic_comp("GENERAL", general)
			#print(specs)

			design = {"GENERAL": dict_values_to_str(gen_specs)}
			full_pwr = {}
			full_times = {}
			for c in comp:
				config = c.split("/")[-1]
				component = c.split("/")[-2]
				if(unit == "SystolicConv"):
					#map from c to 
					#config parser
					
					specs = get_systolic_comp(component, config)
					#print(specs)
					
					hc = {}
					hc.update({
						"GENERAL": gen_specs,
						component: specs,
					})
					design.update({component: dict_values_to_str( specs)})
					#print(hc)

					#print(hc)
					res = SystolicOurModel(hardware_config=hc, benchmark=benchmark, modes = [3])
					time = SystolicTimer(hardware_config=hc, benchmark=benchmark   )

					#print("sim result")
					#print(time)
					#print(res)
					power_calib = 0

					
					for b_idx,b in enumerate(res):
						if(component not in full_pwr):
							full_pwr[component] = {}
							full_times[component] = {}
						full_pwr[component][b] = sum_nested(res[b]	)
						full_times[component][b] =sum_nested( time[b_idx])
						
					print(full_pwr)
					print(full_times)
					
					#parse time and res
					
					#pwr = sum_nested(data)	
					#full_pwr.append(pwr)
					#full_times.append(sum_nested(
					continue
				
					#input()
					for t,p in zip(times, powers):
						if(POWER_MODE == "MAX"):		
							power_calib += p 
						elif(POWER_MODE == "AVG"):
							power_calib += p * t / total_time		
						else:
							print("INVALID POWER MODE", POWER_MODE)
						exit()
		

					
				else:
					pass	

			#time to b
			#full_times_per_layer = [ b: full_times[c][b]   for b in  full_times[c]])   for c in full_times]
			full_times_per_layer = {}		
			ftpl = full_times_per_layer
			ppl = {}
			for c in full_pwr:
				for b in full_pwr[c]:
					t = full_times[c][b]
					p = full_pwr[c][b]
					if(b not in ftpl):
						ftpl[b] = []
						ppl[b] = []
					ftpl[b].append(t)
					ppl[b].append(p)


			#print(full_times_per_layer)	
			#print(ppl)
			#input()	
			total_time = []
			total_pwr = []
			total_t = 0
			total_p = 0
			for b in ppl:
				pp = np.array(ppl[b])
				tt = np.array(ftpl[b])
				max_t = np.max(tt)
				
				if(POWER_MODE == "MAX"):		
					power_calib = np.sum(pp)
				elif(POWER_MODE == "AVG"):
					power_calib =np.sum( pp * tt / max_t)
				else:
					print("INVALID POWER MODE", POWER_MODE)
					exit()	
				#total_time[b] = max_t
				#total_pwr[b] = power_calib
					
				total_p += power_calib
				total_t += max_t			
	
				save_powers[b+"_pwr"] = [ power_calib  ]

				save_times[b+"_time"] = [ max_t  ]

			save_times['total_time'] = total_t #/ len(ppl)
			save_powers['total_pwr'] = total_p / len(ppl)#np.sum(save_powers[b+"_pwr"])
			#df_times = pd.DataFrame(save_times)
			#df_powers = pd.DataFrame(save_powers)
			
			gen = {}
			gen.update(save_times)
			gen.update(save_powers)

			gen.update(design)
				
			print(gen)
			df = pd.DataFrame( gen )
			print("DF")
			print(df)
			#input()
			
			
			#df_times.to_csv( valid_file( save.replace("THIRD_PASS", f"FOURTH_PASS{POWER_MODE}"  ) ) )
			#df_powers.to_csv(valid_file( save.replace("THIRD_PASS", f"FOURTH_PASS{POWER_MODE}"  ) ))
			#df.to_csv(valid_file( save.replace("THIRD_PASS", f"FOURTH_PASS{POWER_MODE}"  )+str( index)     ))

			df.to_csv(valid_file( save.replace("THIRD_PASS", f"FOURTH_PASS/{POWER_MODE}/{WORK_LOAD}/"  )+str( index)     ))



			
			#print(save_powers)
			#print(save_times)

			#print(df_powers)
			#print(df_times)
			#input()	
				
			#print(total_time)
			#print(total_pwr)

			if("total_time" not in save_times):
				pass

			if("total_pwrs" not in save_powers):
				pass
				
			#input()
			
				
			#save_params
			#return {"time": total_time, "power": total_pwr}
			#input("one-design")
		#res = pareto.apply(get_golden, axis=1)
	
		print(res)
		exit()

if __name__ == "__main2__":

	############################
	START_IDX = 155
	SAMPLE = 1000
	OVERWRITE = True
	############################

	#GREEDY APPROACH
	# from conv units, say 300,000 pick paraeto curve ~10 for example
	# out of 10
	#find several pareto points

	#(TODOS) add winograd, sparse architectures as well
	import matplotlib.pyplot as plt
	for orig_base, base3, save, unit in zip([ "generated/DSE/SECOND_PASSAVG/Conv/SystolicConvB2/0.5_0.5_3_3"   ,
			  ], 
			[
	"generated/DSE/FIRST_PASS/Conv/SystolicConvB2",
			],

			[
	"generated/DSE/THIRD_PASS/Conv/SystolicConvB2Pareto.csv",
			],
	["SystolicConv",
	]

):
		#{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}
		benchie = orig_base.split("/")[-1].split("_")
		WEI_SPARSITY = float(benchie[0])
		ACT_SPARSITY = float(benchie[1])
		WEI_BIT_ZERO = int(benchie[2])
		ACT_BIT_ZERO = int(benchie[3])

		#get_benchmark(	
		benchmark = get_benchmark(WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)

		
		pareto = pd.read_csv(save)	
		
		

		#get the golden
		#def get_golden(row):
		df = pareto
		print(len(df))
		#input()
		for index, row in df.iterrows():
			save_powers = {}
			save_times = {}

			#print(row)
			#print(row['component'])
			comp = row['component'].replace("'","").replace("[","").replace("]","").replace(" ","").split(",")
			general = row['name']
			#print(general, row['combo'])
			#input()
			gen_specs = get_systolic_comp("GENERAL", general)
			#print(specs)

			full_pwr = {}
			full_times = {}
			for c in comp:
				config = c.split("/")[-1]
				component = c.split("/")[-2]
				if(unit == "SystolicConv"):
					#map from c to 
					#config parser
					
					specs = get_systolic_comp(component, config)
					#print(specs)
					
					hc = {}
					hc.update({
						"GENERAL": gen_specs,
						component: specs,
					})
					#print(hc)

					#print(hc)
					res = SystolicOurModel(hardware_config=hc, benchmark=benchmark, modes = [3])
					time = SystolicTimer(hardware_config=hc, benchmark=benchmark   )

					#print("sim result")
					#print(time)
					#print(res)
					power_calib = 0

					
					for b_idx,b in enumerate(res):
						if(component not in full_pwr):
							full_pwr[component] = {}
							full_times[component] = {}
						full_pwr[component][b] = sum_nested(res[b]	)
						full_times[component][b] =sum_nested( time[b_idx])
						
					print(full_pwr)
					print(full_times)
					
					#parse time and res
					
					#pwr = sum_nested(data)	
					#full_pwr.append(pwr)
					#full_times.append(sum_nested(
					continue
				
					#input()
					for t,p in zip(times, powers):
						if(POWER_MODE == "MAX"):		
							power_calib += p 
						elif(POWER_MODE == "AVG"):
							power_calib += p * t / total_time		
						else:
							print("INVALID POWER MODE", POWER_MODE)
						exit()
		

					
				else:
					pass	

			#time to b
			#full_times_per_layer = [ b: full_times[c][b]   for b in  full_times[c]])   for c in full_times]
			full_times_per_layer = {}		
			ftpl = full_times_per_layer
			ppl = {}
			for c in full_pwr:
				for b in full_pwr[c]:
					t = full_times[c][b]
					p = full_pwr[c][b]
					if(b not in ftpl):
						ftpl[b] = []
						ppl[b] = []
					ftpl[b].append(t)
					ppl[b].append(p)


			#print(full_times_per_layer)	
			#print(ppl)
			#input()	
			total_time = []
			total_pwr = []
			total_t = 0
			total_p = 0
			for b in ppl:
				pp = np.array(ppl[b])
				tt = np.array(ftpl[b])
				max_t = np.max(tt)
				
				if(POWER_MODE == "MAX"):		
					power_calib = np.sum(pp)
				elif(POWER_MODE == "AVG"):
					power_calib =np.sum( pp * tt / max_t)
				else:
					print("INVALID POWER MODE", POWER_MODE)
					exit()	
				#total_time[b] = max_t
				#total_pwr[b] = power_calib
					
				total_p += power_calib
				total_t += max_t			
	
				save_powers[b+"_pwr"] = [ power_calib  ]

				save_times[b+"_time"] = [ max_t  ]

			save_times['total_time'] = total_t #/ len(ppl)
			save_powers['total_pwr'] = total_p / len(ppl)#np.sum(save_powers[b+"_pwr"])
			#df_times = pd.DataFrame(save_times)
			#df_powers = pd.DataFrame(save_powers)
			
			gen = {}
			gen.update(save_times)
			gen.update(save_powers)
			gen.update(design)
			df = pd.DataFrame( gen )

			
			
			#df_times.to_csv( valid_file( save.replace("THIRD_PASS", f"FOURTH_PASS{POWER_MODE}"  ) ) )
			#df_powers.to_csv(valid_file( save.replace("THIRD_PASS", f"FOURTH_PASS{POWER_MODE}"  ) ))
			df.to_csv(valid_file( save.replace("THIRD_PASS", f"FOURTH_PASS/{POWER_MODE}/{WORK_LOAD}/"  )+str( index)     ))


			
			#print(save_powers)
			#print(save_times)

			#print(df_powers)
			#print(df_times)
			#input()	
				
			#print(total_time)
			#print(total_pwr)

			if("total_time" not in save_times):
				pass

			if("total_pwrs" not in save_powers):
				pass
				
			#input()
			
				
			#save_params
			#return {"time": total_time, "power": total_pwr}
			#input("one-design")
		#res = pareto.apply(get_golden, axis=1)
	
		print(res)
		exit()
