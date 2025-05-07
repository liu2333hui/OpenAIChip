import os
import json
import numpy as np
import pandas as pd
import itertools
from DSE import valid_file
import matplotlib.pyplot as plt
import random
from DSE_secondpass import find_inner,find_inner_wino
from pprint import pprint
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




#OUTPUT DSE results
#Several methods, one for each type and then we have a final one for reconfigurable designs
if __name__ == "__main__":

	############################
	START_IDX = 155
	SAMPLE = 1000
	OVERWRITE = True


	MODE = "time"#time" #TIME, POWER, ENERGY
	############################
	#conv_units = [1,2,3,4,5,6,7,8]	
	conv_units = {}
	import matplotlib.pyplot as plt
	plt.yscale('log')
	dfs = []
	for orig_base, base3, save, unit in zip(
		[ "generated/DSE/SECOND_PASS/Conv/SystolicConv/0.1_0.1_0_0"   ,
			   "generated/DSE/SECOND_PASS/Conv/WinogradConv/0.1_0.1_4_4"   ,
			   "generated/DSE/SECOND_PASS/Conv/SparseConv/0.2_0.1_4_4"], 	
		["generated/DSE/FIRST_PASS/Conv/SystolicConv",
		"generated/DSE/FIRST_PASS/Conv/WinogradConv",
		"generated/DSE/FIRST_PASS/Conv/SparseConv",],
		["generated/DSE/THIRD_PASS/Conv/SystolicConvPareto.csv",
		"generated/DSE/THIRD_PASS/Conv/WinogradConvPareto.csv",
		"generated/DSE/THIRD_PASS/Conv/SparseConvPareto.csv"],
		["SystolicConv",
		"WinogradConv",
		"SparseConv"]
	):
		if(unit == "SparseConv"):
			continue
		if(unit == "WinogradConv" or unit == "SparseConv"):
			continue
	
		pareto = pd.read_csv(save)	
		#save the paretos	
		conv_units[unit] = pareto
		dfs.append(pareto)

	df = pd.concat(dfs)
	#print(df)
	#input()

	#print(df.columns)
	#print(df['Conv5_1_pwr'])
	#print(conv_units)

	#print(df.iloc[50].isna())
	df_id = [i for i in range(len(df))]
	#input()


	def get_unit(design_pwrs, design_times, unit, name, mode, wl):
		design_pwrs[unit] = []
		design_times[unit] = []
		fdir = f"generated/DSE/FOURTH_PASS/{mode}/{wl}/Conv/"
		lowest_energy = -1
		for i in os.listdir(   fdir  ):
			if(name in i):
	
				fdir + "/" + i
				point = pd.read_csv(     fdir + "/"  + i    ) 	
				design_pwrs[unit].append(  point['total_pwr']    )
				#print(point.columns)
				design_times[unit].append( point['total_time']    )
				#input()
				energy = float(point['total_pwr'].iloc[0])*float(point['total_time'].iloc[0])
				#print(energy)
				if(lowest_energy < 0 or energy < lowest_energy):
					lowest_energy = energy
					best_design = point
		return point	
	designs = []
	N = 10000
	SAMPLE = 50
	mode = "AVG"
	wl = "0.1_0.1_0_0"

	design_pwrs = {}
	design_times = {}
	#load baseline 1
	unit = 'b1'
	name = "SystolicConvB1"
	best=get_unit(design_pwrs, design_times, unit, name, mode, wl)
	print("BEST ",name)
	pprint(best.iloc[0])
	print()
	#load baseline 2
	unit = 'b2'
	name = "SystolicConvB2"
	best=get_unit(design_pwrs, design_times, unit, name, mode, wl)
	print("BEST ",name)
	pprint(best.iloc[0])
	print()

	#load Systolic Our
	unit = 'our'
	name = "SystolicConvOurGolden"
	best=get_unit(design_pwrs, design_times, unit, name, mode, wl)
	print("BEST ",name)
	pprint(best.iloc[0])
	print()

	
	#plt.scatter(np.array(design_pwrs['b2'])*10000, np.array(design_times['b2']))						
	for num in design_pwrs:
		#5 is for calibrated to cap load = 1
		plt.scatter(np.array(design_pwrs[num])*5000, np.array(design_times[num]) )
	

	plt.legend([key for key in design_pwrs.keys()])
	plt.yscale('linear')

	plt.show()
	input('R U OK?')
	#for num in design_pwrs:
	#	#5 is for calibrated to cap load = 1
	#	plt.scatter(np.array(design_pwrs[num])*10000, np.array(design_times[num]) )

	benchmark = get_benchmark(WEI_SPARSITY=0.1, ACT_SPARSITY=0.1, WEI_BIT_ZERO=0, ACT_BIT_ZERO=0)
	l = 0
	k = 0

	#df_id = len(design_pwrs['our'])

	import random	
	for n in [1,2,4,16,2, 4, 8, 16][::1]:
		design_pwrs[n] = []
		design_times[n] = []
		k = 0		
		perms = []
		kkk = 0
		for p in itertools.permutations(df_id, n):
			perms.append(p)
			if(kkk > N):
				break
			kkk = kkk+1
		for p in random.sample(perms, k = min(len(perms),SAMPLE)):
			k = k + 1
			if((k + 1) % SAMPLE == 0):
				break
	
			mapping = {}
			#print(p)
			#input()
			valid_design = True
			for b in benchmark:
				#choose one of the conv units by index
				#mapping is simple greedy strategy
				#choose hardware with "best" energy for the 
				di = []
				for pp in p:
					#print(df.iloc[pp])	
					pwr  =  df.iloc[pp][b+"_pwr"]
					time = df.iloc[pp][b+"_time"]
					if(not np.isnan(  pwr   ) ):
						if(MODE == "power"):
							di.append(pwr)
						elif(MODE == "time"):
							di.append(time)
						elif(MODE == "energy"):
							di.append(pwr*time)
						else:
							print("optimized strategy mode none")
							exit()
						#di.append(pwr*time)
						#print(df.iloc[pp])
						#input()
						#pass
					else:
						#di.append(8e100)
						pass
					
						#print(df.iloc[pp][b+"_pwr"])
						#input()
				if(len(di) == 0):
					valid_design = False
					continue

				idx = np.argmin(di)
				#print(di)
				#print(idx)
				mapping[b] = idx
			print(mapping)
			#input()
			if(valid_design):
				pwrs = []
				times = []
				for b in mapping:
					idx = mapping[b]
					pwrs.append(df.iloc[p[idx]][b+"_pwr"])
					times.append(df.iloc[p[idx]][b+"_time"])
				design_pwrs[n].append(sum(pwrs)/len(pwrs))
				design_times[n].append(sum(times))
				#design.append(p)

				l = l + 1
				pass				
			else:
				continue	


			if(np.isnan(sum(times))):
				continue

			#print(pwrs)
			#print(times)
			#print(design_pwrs)
			#print(design_times)
			#input()
	
			#print(l)
			if((l + 1) % N == 0):

				pass


		SAMPLE = 50
		B = 40
		plt.scatter(np.array(design_pwrs['b1'])*4*5000, np.array(design_times['b1'])/B,alpha=0.5)
		plt.scatter(np.array(design_pwrs['b2'])*4*5000, np.array(design_times['b2'])/B,alpha=0.5)
				
		p = []
		t = []
		for num in design_pwrs:
			if num not in ['b1', 'b2', 'our']:
				p += design_pwrs[num]
				t += design_times[num]




		plt.scatter(np.array(p[::3])*4*5000, np.array(t[::3])/B, alpha=0.5)
		plt.legend(['Maestro-like', "Accelergy-like", "OSCAR"],fontsize=14)#[key for key in design_pwrs.keys()])
		plt.yscale('log')

		plt.xlabel("Averaged Power (mW)", fontsize=14)
		plt.ylabel("Total Cycles", fontsize=14)

		plt.xlim(0, 700)

		plt.ylim(1e6, 1e9)
		
		plt.rcParams.update({
    'font.size': 12,          # 基础字号
    'axes.titlesize': 14,    # 标题字号
    'axes.labelsize': 12,    # 坐标轴标签字号
    'xtick.labelsize': 10,   # X轴刻度字号
    'ytick.labelsize': 10,   # Y轴刻度字号
    'legend.fontsize': 11    # 图例字号
})

		
		plt.savefig(f"generated/images/DSE.{n}.png", dpi=300)
		plt.show()

		continue
		#end permutations
		import matplotlib.pyplot as plt	
		print(design_pwrs)

		
		
		for num in design_pwrs:
			#5 is for calibrated to cap load = 1
			plt.scatter(np.array(design_pwrs[num])*2*5000, np.array(design_times[num])/B )
		plt.xlabel("Averaged Power (mW)")
		plt.ylabel("Total Cycles")
		plt.legend([key for key in design_pwrs.keys()])
		plt.yscale('log')
		plt.show()


	#loop number of reconv
	
		
	'''
	for n in [2]:#, 2, 4]: #number of variable dataflows
		#instead of iterating through all possible, choose best units
		#300 choose 1 choose 2	
		#get combinations of reconfigurable units
		for p in itertools.permutations(conv_units, n):
			#layers
			mapping = {

			}		
			#perform greedy mapping
			for b in benchmark:
				if("Conv" in b):
					#choose one of the conv units by index
					#mapping is simple greedy strategy
					#choose hardware with "best" energy for the 
					for i in range(n):
						print('eval energy ', b,":->",i)
						#mapping[b] = i
						#get max
					mapping[b] = random.randint(0, n)
			#add steering logic and muxes
			STEERING_LOGIC = {}
			for unit in p:
				#get units (and possibly area)
				#perform resource sharing identification
			p1=evaluate_power(STEERING_LOGIC)
			p2=evaluate_power(core_architecture)
			total_power = p1+p2	
			print("done power of ", mapping, p)



	'''
	exit()	
	import random	
	for n in [1,2,4,16,2, 4, 8, 16][::1]:
		design_pwrs[n] = []
		design_times[n] = []
		k = 0		
		perms = []
		kkk = 0
		for p in itertools.permutations(df_id, n):
			perms.append(p)
			if(kkk > N):
				break
			kkk = kkk+1
		for p in random.sample(perms, k = min(len(perms),SAMPLE)):
			k = k + 1
			if((k + 1) % SAMPLE == 0):
				break
	
			mapping = {}
			#print(p)
			#input()
			valid_design = True
			for b in benchmark:
				#choose one of the conv units by index
				#mapping is simple greedy strategy
				#choose hardware with "best" energy for the 
				di = []
				for pp in p:
					#print(df.iloc[pp])	
					pwr  =  df.iloc[pp][b+"_pwr"]
					time = df.iloc[pp][b+"_time"]
					if(not np.isnan(  pwr   ) ):
						if(MODE == "power"):
							di.append(pwr)
						elif(MODE == "time"):
							di.append(time)
						elif(MODE == "energy"):
							di.append(pwr*time)
						else:
							print("optimized strategy mode none")
							exit()
						#di.append(pwr*time)
						#print(df.iloc[pp])
						#input()
						#pass
					else:
						#di.append(8e100)
						pass
					
						#print(df.iloc[pp][b+"_pwr"])
						#input()
				if(len(di) == 0):
					valid_design = False
					continue

				idx = np.argmin(di)
				#print(di)
				#print(idx)
				mapping[b] = idx
			print(mapping)
			#input()
			if(valid_design):
				pwrs = []
				times = []
				for b in mapping:
					idx = mapping[b]
					pwrs.append(df.iloc[p[idx]][b+"_pwr"])
					times.append(df.iloc[p[idx]][b+"_time"])
				design_pwrs[n].append(sum(pwrs)/len(pwrs))
				design_times[n].append(sum(times))
				#design.append(p)

				l = l + 1
				pass				
			else:
				continue	


			if(np.isnan(sum(times))):
				continue

			#print(pwrs)
			#print(times)
			#print(design_pwrs)
			#print(design_times)
			#input()
	
			#print(l)
			if((l + 1) % N == 0):

				for num in design_pwrs:
					plt.scatter(design_pwrs[num], design_times[num])
				plt.legend([key for key in design_pwrs.keys()])
				plt.yscale('log')

				plt.show()
		#end permutations
		import matplotlib.pyplot as plt	
		print(design_pwrs)

		
		
		for num in design_pwrs:
			#5 is for calibrated to cap load = 1
			plt.scatter(np.array(design_pwrs[num])*5000, np.array(design_times[num]) )
		plt.xlabel("Averaged Power (mW)")
		plt.ylabel("Total Cycles")
		plt.legend([key for key in design_pwrs.keys()])
		plt.yscale('log')
		plt.show()


	#loop number of reconv
	
		
	'''
	for n in [2]:#, 2, 4]: #number of variable dataflows
		#instead of iterating through all possible, choose best units
		#300 choose 1 choose 2	
		#get combinations of reconfigurable units
		for p in itertools.permutations(conv_units, n):
			#layers
			mapping = {

			}		
			#perform greedy mapping
			for b in benchmark:
				if("Conv" in b):
					#choose one of the conv units by index
					#mapping is simple greedy strategy
					#choose hardware with "best" energy for the 
					for i in range(n):
						print('eval energy ', b,":->",i)
						#mapping[b] = i
						#get max
					mapping[b] = random.randint(0, n)
			#add steering logic and muxes
			STEERING_LOGIC = {}
			for unit in p:
				#get units (and possibly area)
				#perform resource sharing identification
			p1=evaluate_power(STEERING_LOGIC)
			p2=evaluate_power(core_architecture)
			total_power = p1+p2	
			print("done power of ", mapping, p)



	'''
