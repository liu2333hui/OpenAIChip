import os
import json
import numpy as np
import pandas as pd
import itertools
from DSE import valid_file
import matplotlib.pyplot as plt
import random
from DSE_secondpass import find_inner,find_inner_wino
	
def blank(f):
	return f

def sum_a(a):
    if isinstance(a, (int, float)):  # 如果 a 是数字（如 a=1）
        return a
    elif isinstance(a, (list, tuple)):  # 如果 a 是列表或元组（如 a=[1,10]）
        return sum(a)
    else:
        raise TypeError("输入必须是数字或可迭代对象（如列表）")



def sum_nested(data):
    if isinstance(data, (int, float)):
        return data
    elif isinstance(data, (list, tuple)):
        return sum(sum_nested(item) for item in data)
    elif isinstance(data, dict):
        return sum(sum_nested(v) for v in data.values())
    else:
        return 0  # 忽略非数字类型

def sum_dict_values(data):
    total = 0
    for value in data.values():
        if isinstance(value, dict):  # 如果是嵌套字典
            total += sum_dict_values(value)
        elif isinstance(value, (list, tuple)):  # 如果是列表/元组
            total += sum(value)
        elif isinstance(value, (int, float)):  # 如果是数字
            total += value
    return total

if 1:

	WEI_SPARSITY = 0.1           
	WEI_BIT_ZERO = 0
	ACT_SPARSITY = 0.1
	ACT_BIT_ZERO = 0
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

bkeys = [k for k in benchmark.keys() if ('FC' in k or 'Conv' in k)]


#hardcode for now
def readj(ff):
	total_times = []
	total_powers = []
	for layer in bkeys:#benchmark.keys():	
		powers = []
		times = []	
		#print("LAYER", layer)
	
		for fff in ff:
		
			#if(not('FC' in layer or 'Conv' in layer)):
			#	continue
			wei = f'{layer}.{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}'

			#timing
			with open(fff+"/"+wei+".time", 'r', encoding='utf-8') as f:
				data = json.load(f)  # 返回字典或列表‌:ml-citation{ref="1,3" data="citationList"}
			#print(data[next(iter(data.keys()))])
			times.append(data[next(iter(data.keys()))])
				

			#power
			with open(fff+'/'+wei+'.ourpower', 'r', encoding='utf-8') as f:
				data = json.load(f)  # 返回字典或列表‌:ml-citation{ref="1,3" data="citationList"}

			pwr = 0
			#print(data)
			#for c in data:
			#	print(c)
			#	if isinstance(data[c], (int, float)): 
			#		pwr = data[c]
			#			break
			#		for p in data[c] :
			#			pwr = pwr + sum_a(data[c][p])
			pwr = sum_nested(data)	
			#print(pwr)
		
			#input()
			powers.append(pwr)
		
		total_time = max(times)
		power_calib = 0
		for t,p in zip(times, powers):
			power_calib += p * t / total_time	
		#print("LAYER", total_time, power_calib)
	
		total_times.append(total_time)
		total_powers.append(power_calib)
		
			

	#print(sum(total_times))
	#print(sum(total_powers)/len(total_powers))
	return sum(total_times), sum(total_powers)/len(total_powers), total_times, total_powers



def inner(base, sample):
	if 1:
		p = []
		t = []
		combo = []
		t_per_layer = []
		p_per_layer = []

		l = 0
		flag = False	
		for f1,wei_pe_cast in enumerate(os.listdir(base+"/WEI_PE_CAST")):
			for f2,wei_loader in enumerate(os.listdir(base+"/WEI_LOADER")):
				for f3,pe_array in enumerate(os.listdir(base+"/PE_ARRAY")):
					for f4,out_loader in enumerate(os.listdir(base+"/OUT_LOADER")):
						for f5,L2 in enumerate(os.listdir(base+"/L2")):
							for f6,adder_tree in enumerate(os.listdir(base+"/ADDER_TREE")):	
								for f7,act_pe_cast in enumerate(os.listdir(base+"/ACT_PE_CAST")):
									for f8,act_loader in enumerate(os.listdir(base+"/ACT_LOADER")):
										for f9,accumulator in enumerate(os.listdir(base+"/ACCUMULATOR")):
											if(flag):
												return l, p, t, combo, p_per_layer, t_per_layer
												continue

											if((l + 1) % (sample//10) == 0):
				
												print(l)
											l = l+1
											if(l > sample):
												flag = True
											#continue

											c1 = blank(base+"/WEI_PE_CAST/"+wei_pe_cast)	
											c2 = blank(base+"/WEI_LOADER/"+wei_loader)	
											c3 = blank(base+"/PE_ARRAY/"+pe_array)	
											c4 = blank(base+"/OUT_LOADER/"+out_loader)	
											c5 = blank(base+"/L2/"+L2)	
											c6 = blank(base+"/ADDER_TREE/"+adder_tree)	
											c7 = blank(base+"/ACT_PE_CAST/"+act_pe_cast)	
											c8 = blank(base+"/ACT_LOADER/"+act_loader)	
											c9 = blank(base+"/ACCUMULATOR/"+accumulator)	

											total_time,total_power, times, powers = readj([c1,c2,c3,c4,c5,c6,c7,c8,c9])
											#print(1e-9*total_time, total_power)
											combo.append("_".join([str(fff) for fff in [f1,f2,f3,f4,f5,f6,f7,f8,f9]]))
											p.append(total_power)
											t.append(total_time)
											t_per_layer.append(times)
											p_per_layer.append(powers)

											continue
											#print(l)
											if((l+1) % 10000 == 0):
												import matplotlib.pyplot as plt
												plt.scatter(p,t)
												plt.show()


# 寻找帕累托前沿
def find_pareto_points(df):
    points = df.values
    is_pareto = np.ones(points.shape, dtype=bool)
    for i, (a, b) in enumerate(points):
        if is_pareto[i]:
            dominated = (points[:, 0] >= a) & (points[:, 1] >= b) & \
                        ((points[:, 0] > a) | (points[:, 1] > b))
            is_pareto[dominated] = False
    return df[is_pareto]

def find_pareto_points(df, category):
    points = df[category].values
    is_pareto = np.ones(len(points), dtype=bool)  # 修正为一维布尔数组‌:ml-citation{ref="5" data="citationList"}
    for i, (a, b) in enumerate(points):
        if is_pareto[i]:
            dominated = (points[:, 0] >= a) & (points[:, 1] >= b) & \
                       ((points[:, 0] > a) | (points[:, 1] > b))
            is_pareto &= ~dominated  # 直接更新布尔数组‌:ml-citation{ref="5" data="citationList"}
    return df[is_pareto]




#OUTPUT DSE results
#Several methods, one for each type and then we have a final one for reconfigurable designs
if __name__ == "__main__":

	############################
	START_IDX = 155
	SAMPLE = 1000
	OVERWRITE = True
	#UNIT = "SystolicConvOur"
	#UNIT = "SystolicConvOurGolden"
	#UNIT = "SystolicConvOurGolden"
	#UNIT = "WinogradConv"
	UNIT = "SparseConv"






	
	#UNIT = "SystolicConvB1"
	#UNIT = "SystolicConvB2"
	#UNIT = "SystolicConvB2"
	
	MODE = ""
	#MODE = "AVG"
	
	
	#WORKLOAD = "0.5_0.5_3_3"
	#WORKLOAD = "0.1_0.1_0_0"
	#WORKLOAD = "0.1_0.1_4_4"
	WORKLOAD = "0.2_0.1_4_4"

	############################

	conv_units = [1,2,3,4,5,6,7,8]

	#in this experient, only play with varying the conv unit reconfig


	#GREEDY APPROACH
	# from conv units, say 300,000 pick paraeto curve ~10 for example
	# out of 10
	#find several pareto points

	#(TODOS) add winograd, sparse architectures as well
	import matplotlib.pyplot as plt
	wei = f'{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}'		
	for orig_base, base3, save in zip(
		[ 
	f"generated/DSE/SECOND_PASS{MODE}/Conv/{UNIT}/{WORKLOAD}"   ,

			  ], 
			[
	f"generated/DSE/FIRST_PASS/Conv/{UNIT}",




			],

			[
	f"generated/DSE/THIRD_PASS/Conv/{UNIT}Pareto.csv",
			]

):
		tt = []
		pp = []

		dfs = []
						#print(df_read)
			#input()
			#print(df_read['out_terms'])
			#adhoc fix
			

		#orig_base = orig_base + "/" + wei
		for g_idx,general in enumerate(os.listdir(orig_base)):
			csv_out = valid_file(f"{orig_base}/{general}")
			print('csv_out',csv_out)
			#print(os.path.exists(csv_out))
			#input()
			if(os.path.exists(csv_out)):			
				dff = pd.read_csv(csv_out)#, mode="a", header=False, index=False	
				dff['name'] = '.'.join(general.split(".")[0:-1])


				dff['avg_time'] = dff['total_time']/ ((len(dff.columns)-3)/2)  

				#print(dff)
				dfs.append(dff)

				#print(df)
				#print((len(df.columns)-3)//2)
				#input()
				#exit()
				#df = dff[['total_pwr', 'total_time']]	
				df = dff
				'''
				print(df)
				pareto_front = find_pareto_points(df, ['total_pwr', 'total_time'])

				
				# 可视化
				plt.scatter(df['total_pwr'], df['total_time'], alpha=0.5)
				plt.scatter(pareto_front['total_pwr'], pareto_front['total_time'], 
			            color='red', label='Pareto Front')
				plt.xlabel('Objective A')
				plt.ylabel('Objective B')
				plt.legend()
				plt.show()
				'''

				pp = pp + df['total_pwr'].tolist()   
				tt = tt + (df['total_time']/ ((len(df.columns)-3)/2)  ).tolist()
				#print(f"skipping {g_idx}")	
				#print(f"add df from {csv_out}")	
		

		df = pd.concat(dfs)
		#print(df)
		pareto_front = find_pareto_points(df, ['total_pwr', 'avg_time'])

		#input()
		#print(pareto_front)
		#print(base3)
		
		def get_designs(row):
			#print("ROW")
			#print(row)
			#print(row['name'])
			#print(base3)
			if("Winograd" in base3):
				found = find_inner_wino(base3+ "/"+row["name"]  ,  row['combo'])	
			else:
				found = find_inner(base3+ "/"+row["name"]  ,  row['combo'])
			#TODOS elif Sparse
			#print(found)
			return found
			

		pareto_front["component"] = pareto_front.apply( get_designs, axis=1)

		print(pareto_front[['component', 'combo']])
		pareto_front.to_csv(valid_file(save), index=False, encoding='utf-8')
		#input()


		plt.scatter(df['total_pwr'], df['avg_time'], alpha=0.5)
		plt.scatter(pareto_front['total_pwr'], pareto_front['avg_time'], 
			            color='red', label='Pareto Front')
		plt.xlabel('Objective A')
		plt.ylabel('Objective B')
		plt.legend()
		plt.show()
	

		plt.scatter(tt, pp)

	plt.xlim(0, 1e8)
	plt.ylim(0, 0.1)
	plt.show()
				
	'''
	print(benchmark.keys())
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
if __name__ == "__main2__":

	############################
	START_IDX = 155
	SAMPLE = 1000
	OVERWRITE = True
	############################

	conv_units = [1,2,3,4,5,6,7,8]

	#in this experient, only play with varying the conv unit reconfig


	#GREEDY APPROACH
	# from conv units, say 300,000 pick paraeto curve ~10 for example
	# out of 10
	#find several pareto points

	#(TODOS) add winograd, sparse architectures as well
	import matplotlib.pyplot as plt
	wei = f'{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}'		
	for orig_base, base3, save in zip([ "generated/DSE/SECOND_PASS/Conv/SystolicConv/0.1_0.1_0_0"   ,
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
			]

):
		tt = []
		pp = []

		dfs = []
						#print(df_read)
			#input()
			#print(df_read['out_terms'])
			#adhoc fix
			

		#orig_base = orig_base + "/" + wei
		for g_idx,general in enumerate(os.listdir(orig_base)):
			csv_out = valid_file(f"{orig_base}/{general}")
			print('csv_out',csv_out)
			#print(os.path.exists(csv_out))
			#input()
			if(os.path.exists(csv_out)):			
				dff = pd.read_csv(csv_out)#, mode="a", header=False, index=False	
				dff['name'] = '.'.join(general.split(".")[0:-1])


				dff['avg_time'] = dff['total_time']/ ((len(dff.columns)-3)/2)  

				#print(dff)
				dfs.append(dff)

				#print(df)
				#print((len(df.columns)-3)//2)
				#input()
				#exit()
				#df = dff[['total_pwr', 'total_time']]	
				df = dff
				'''
				print(df)
				pareto_front = find_pareto_points(df, ['total_pwr', 'total_time'])

				
				# 可视化
				plt.scatter(df['total_pwr'], df['total_time'], alpha=0.5)
				plt.scatter(pareto_front['total_pwr'], pareto_front['total_time'], 
			            color='red', label='Pareto Front')
				plt.xlabel('Objective A')
				plt.ylabel('Objective B')
				plt.legend()
				plt.show()
				'''

				pp = pp + df['total_pwr'].tolist()   
				tt = tt + (df['total_time']/ ((len(df.columns)-3)/2)  ).tolist()
				#print(f"skipping {g_idx}")	
				#print(f"add df from {csv_out}")	
		

		df = pd.concat(dfs)
		#print(df)
		pareto_front = find_pareto_points(df, ['total_pwr', 'avg_time'])

		#input()
		#print(pareto_front)
		#print(base3)
		
		def get_designs(row):
			#print("ROW")
			#print(row)
			#print(row['name'])
			#print(base3)
			if("Winograd" in base3):
				found = find_inner_wino(base3+ "/"+row["name"]  ,  row['combo'])	
			else:
				found = find_inner(base3+ "/"+row["name"]  ,  row['combo'])
			#TODOS elif Sparse
			#print(found)
			return found
			

		pareto_front["component"] = pareto_front.apply( get_designs, axis=1)

		print(pareto_front[['component', 'combo']])
		pareto_front.to_csv(valid_file(save), index=False, encoding='utf-8')
		#input()


		plt.scatter(df['total_pwr'], df['avg_time'], alpha=0.5)
		plt.scatter(pareto_front['total_pwr'], pareto_front['avg_time'], 
			            color='red', label='Pareto Front')
		plt.xlabel('Objective A')
		plt.ylabel('Objective B')
		plt.legend()
		plt.show()
	

		plt.scatter(tt, pp)

	plt.xlim(0, 1e8)
	plt.ylim(0, 0.1)
	plt.show()
				
	'''
	print(benchmark.keys())
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
