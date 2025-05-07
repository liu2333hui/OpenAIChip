import os
import json
import numpy as np
import pandas as pd

from DSE import valid_file
import matplotlib.pyplot as plt
	

#POWER_MODE = "MAX"
POWER_MODE = "AVG"

#4 cases
MODE = 2#3
#low sparsity, low bit zero
if(MODE == 0):
	WEI_SPARSITY = 0.1           
	WEI_BIT_ZERO = 0
	ACT_SPARSITY = 0.1
	ACT_BIT_ZERO = 0
#high sparsity, low bit zero
if(MODE == 1):
	WEI_SPARSITY = 0.8          
	WEI_BIT_ZERO = 0
	ACT_SPARSITY = 0.8
	ACT_BIT_ZERO = 0
#high sparsity, high bit zero
if(MODE == 2):
	WEI_SPARSITY = 0.5      
	WEI_BIT_ZERO = 3
	ACT_SPARSITY = 0.5
	ACT_BIT_ZERO = 3
#low sparsity, high bit zero
if(MODE == 3):
	WEI_SPARSITY = 0.1     
	WEI_BIT_ZERO = 4
	ACT_SPARSITY = 0.1
	ACT_BIT_ZERO = 4
#low sparsity, high bit zero
if(MODE == 4):
	WEI_SPARSITY = 0.2       
	WEI_BIT_ZERO = 4
	ACT_SPARSITY = 0.1
	ACT_BIT_ZERO = 4



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

#bkeys = [k for k in benchmark.keys() if ('FC' in k or 'Conv' in k)]
bkeys = [k for k in benchmark.keys() if ('Conv' in k)]



#hardcode for now
def readj(ff):
	total_times = []
	total_powers = []
	layers_valid = []
	for layer in bkeys:#benchmark.keys():	
		powers = []
		times = []	
		#print("LAYER", layer)
			
		for fff in ff:
		

			#if(not('FC' in layer or 'Conv' in layer)):
			#	continue
			wei = f'{layer}.{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}'
	
			
			if(not os.path.exists(fff+"/"+wei+".time")):
				#print(fff, wei)
				continue
				#layers_valid.append(layer)	


			#timing
			with open(fff+"/"+wei+".time", 'r', encoding='utf-8') as f:
				data = json.load(f)  # 返回字典或列表‌:ml-citation{ref="1,3" data="citationList"}
			#print(data[next(iter(data.keys()))])
			if(type(data) == list):
				data = data[0]
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
		

		if(not os.path.exists(fff+"/"+wei+".time")):
			pass
			#layers_valid.append(layer)	
		else:
	
			layers_valid.append(layer)	

			total_time = max(times)
			power_calib = 0
			for t,p in zip(times, powers):
				if(POWER_MODE == "MAX"):		
					power_calib += p 
				elif(POWER_MODE == "AVG"):
					power_calib += p * t / total_time		
				else:
					print("INVALID POWER MODE", POWER_MODE)
					exit()
			#print("LAYER", total_time, power_calib)
		
			total_times.append(total_time)
			total_powers.append(power_calib)
		
			

	#print(sum(total_times))
	#print(sum(total_powers)/len(total_powers))
	#print(total_powers, layers_valid)
	#input("OK?")
	return sum(total_times), sum(total_powers)/len(total_powers), total_times, total_powers, layers_valid

def find_inner_wino(base, find_combo):
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
											for f10,wino_a in enumerate(os.listdir(base+"/WINO_A")):
												for f11,wino_at in enumerate(os.listdir(base+"/WINO_AT")):
													for f12,wino_bt in enumerate(os.listdir(base+"/WINO_BT")):
														for f13,wino_b in enumerate(os.listdir(base+"/WINO_B")):
															for f14,wino_g in enumerate(os.listdir(base+"/WINO_G")):
																for f15,wino_gt in enumerate(os.listdir(base+"/WINO_GT")):


																	c1 = blank(base+"/WEI_PE_CAST/"+wei_pe_cast)	
																	c2 = blank(base+"/WEI_LOADER/"+wei_loader)	
																	c3 = blank(base+"/PE_ARRAY/"+pe_array)	
																	c4 = blank(base+"/OUT_LOADER/"+out_loader)	
																	c5 = blank(base+"/L2/"+L2)	
																	c6 = blank(base+"/ADDER_TREE/"+adder_tree)	
																	c7 = blank(base+"/ACT_PE_CAST/"+act_pe_cast)	
																	c8 = blank(base+"/ACT_LOADER/"+act_loader)	
																	c9 = blank(base+"/ACCUMULATOR/"+accumulator)	
																	c10 = blank(base+"/WINO_AT/"+wino_at)	
																	c11 = blank(base+"/WINO_A/"+wino_a)	
																	c12 = blank(base+"/WINO_G/"+wino_g)	
																	c13 = blank(base+"/WINO_GT/"+wino_gt)	
																	c14 = blank(base+"/WINO_B/"+wino_b)	
																	c15 = blank(base+"/WINO_BT/"+wino_bt)	
	
																	combo = "_".join([str(fff) for fff in [f1,f2,f3,f4,f5,f6,f7,f8,f9, f10, f11, f12, f13, f14, f15]])

																	if(combo == find_combo):
																		return [c1,c2,c3,c4,c5,c6,c7,c8,c9, c10,c11,c12,c13,c14,c15]
	




def inner_wino(base, sample):
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
											for f10,wino_a in enumerate(os.listdir(base+"/WINO_A")):
												for f11,wino_at in enumerate(os.listdir(base+"/WINO_AT")):
													for f12,wino_bt in enumerate(os.listdir(base+"/WINO_BT")):
														for f13,wino_b in enumerate(os.listdir(base+"/WINO_B")):
															for f14,wino_g in enumerate(os.listdir(base+"/WINO_G")):
																for f15,wino_gt in enumerate(os.listdir(base+"/WINO_GT")):


																	if(flag):
																		return l, p, t, combo, p_per_layer, t_per_layer, valid_layers
																		continue
	
																	if((l + 1) % (sample//10) == 0):					
																		print(l	)
																	l = l+1
																	if(l > sample):
																		flag = True

																	c1 = blank(base+"/WEI_PE_CAST/"+wei_pe_cast)	
																	c2 = blank(base+"/WEI_LOADER/"+wei_loader)	
																	c3 = blank(base+"/PE_ARRAY/"+pe_array)	
																	c4 = blank(base+"/OUT_LOADER/"+out_loader)	
																	c5 = blank(base+"/L2/"+L2)	
																	c6 = blank(base+"/ADDER_TREE/"+adder_tree)	
																	c7 = blank(base+"/ACT_PE_CAST/"+act_pe_cast)	
																	c8 = blank(base+"/ACT_LOADER/"+act_loader)	
																	c9 = blank(base+"/ACCUMULATOR/"+accumulator)	
																	c10 = blank(base+"/WINO_AT/"+wino_at)	
																	c11 = blank(base+"/WINO_A/"+wino_a)	
																	c12 = blank(base+"/WINO_G/"+wino_g)	
																	c13 = blank(base+"/WINO_GT/"+wino_gt)	
																	c14 = blank(base+"/WINO_B/"+wino_b)	
																	c15 = blank(base+"/WINO_BT/"+wino_bt)	
	
				
																	total_time,total_power, times, powers, valid_layers = readj([c1,c2,c3,c4,c5,c6,c7,c8,c9, c10, c11, c12, c13, c14, c15])
																	#print(1e-9*total_time, total_power)
																	combo.append("_".join([str(fff) for fff in [f1,f2,f3,f4,f5,f6,f7,f8,f9, f10, f11, f12, f13, f14, f15]]))
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


def find_inner(base, find_combo = ""):
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
											c1 = blank(base+"/WEI_PE_CAST/"+wei_pe_cast)	
											c2 = blank(base+"/WEI_LOADER/"+wei_loader)	
											c3 = blank(base+"/PE_ARRAY/"+pe_array)	
											c4 = blank(base+"/OUT_LOADER/"+out_loader)	
											c5 = blank(base+"/L2/"+L2)	
											c6 = blank(base+"/ADDER_TREE/"+adder_tree)	
											c7 = blank(base+"/ACT_PE_CAST/"+act_pe_cast)	
											c8 = blank(base+"/ACT_LOADER/"+act_loader)	
											c9 = blank(base+"/ACCUMULATOR/"+accumulator)	

											combo = "_".join([str(fff) for fff in [f1,f2,f3,f4,f5,f6,f7,f8,f9]])
											if(combo == find_combo):
												return [c1,c2,c3,c4,c5,c6,c7,c8,c9]
											continue
	

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
												return l, p, t, combo, p_per_layer, t_per_layer, valid_layers
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

											total_time,total_power, times, powers, valid_layers = readj([c1,c2,c3,c4,c5,c6,c7,c8,c9])
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




#WinoConv
if __name__ == "__main2__":

	############################
	START_IDX = 0
	SAMPLE = 1000
	OVERWRITE = True
	TYPE = "WinogradConv"	
	############################

	#unit-based hierarchical flatenning
	#systolic
	orig_base = f"generated/DSE/FIRST_PASS/Conv/{TYPE}"
	l = 0
	sample = SAMPLE
	total = 0
	total_l = 0
	pp = []
	tt = []
	cc = []
	for g_idx,general in enumerate(os.listdir(orig_base)):
		wei = f'{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}'

		if(g_idx < START_IDX):
			#print(f"skipping {g_idx}")	
			csv_out = valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/{TYPE}/{wei}/{general}.csv")
			if(os.path.exists(csv_out)):			
				df = pd.read_csv(csv_out)#, mode="a", header=False, index=False)	
				pp = pp + df['total_pwr'].tolist()
				tt = tt + df['total_time'].tolist()
				print(f"skipping {g_idx}")	

				print(f"add df from {csv_out}")
			continue	

		base = orig_base + "/" + general
	
		if(len(os.listdir(base)) != 15) :
			print("skip ", base)
			continue
			
		l,p,t,combo, p_per_layer, t_per_layer, valid_layers  = inner_wino(base, sample)

		p_per_layer = np.array(p_per_layer).transpose().tolist()
		t_per_layer = np.array(t_per_layer).transpose().tolist()
	
		#print(len(p_per_layer))#, t_per_layer)
		#input("DONE")

		data = {"combo": combo, "total_time": t, "total_pwr": p }
		print(valid_layers)
		#print(p_per_layer)
		#for b_idx, b in enumerate(bkeys):
		for b_idx,b in enumerate(valid_layers):
			data[b+"_pwr"] = p_per_layer[b_idx]
			data[b+"_time"] = t_per_layer[b_idx]

		#print(data)


		#data.update(p_per_layer)
		#data.update(t_per_layer)
		df = pd.DataFrame(data)
		#print(df)
		#input()
		#exit()
		csv_out = valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/{TYPE}/{wei}/{general}.csv")
		if(OVERWRITE):
			df.to_csv(csv_out, index=False)
		else:
			if(os.path.exists(csv_out)):			
				df.to_csv(csv_out, mode="a", header=False, index=False)	
			else:
				df.to_csv(csv_out, index=False)

		continue
		pp = pp + p
		tt = tt + t
		#cc = cc + combo	

		total_l = total_l + l	

		#print(f"done g_idx = {g_idx}")
		png = valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/{TYPE}/DSE/{g_idx}.png")
	
		plt.scatter(pp,tt)
		#plt.show()
		plt.savefig(png)#valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/SystolicConv/DSE/{g_idx}.png"))

		#print("done")
		print(f"done save fig g_idx = {g_idx}")
		#input("continue?")
		#exit()



#SystolicConv
if __name__ == "__main__":

	############################
	START_IDX = 0
	SAMPLE = 5000
	OVERWRITE = True
	TYPE = "SystolicConvOur"	
	#TYPE = "SparseConv"	
	
	need_fig = False
	############################



	#unit-based hierarchical flatenning
	#systolic
	orig_base = f"generated/DSE/FIRST_PASS/Conv/{TYPE}"
	l = 0
	sample = SAMPLE
	total = 0
	total_l = 0
	pp = []
	tt = []
	cc = []
	for g_idx,general in enumerate(os.listdir(orig_base)):
		wei = f'{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}'

		if(g_idx < START_IDX):
			#print(f"skipping {g_idx}")	
			csv_out = valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/{TYPE}/{wei}/{general}.csv")
			if(os.path.exists(csv_out)):			
				df = pd.read_csv(csv_out)#, mode="a", header=False, index=False)	
				pp = pp + df['total_pwr'].tolist()
				tt = tt + df['total_time'].tolist()
				print(f"skipping {g_idx}")	

				print(f"add df from {csv_out}")
			continue
				


	

		base = orig_base + "/" + general
	
		if(len(os.listdir(base)) != 9) :
			print("skip ", base)
			continue
	
		l,p,t,combo, p_per_layer, t_per_layer,valid_layers  = inner(base, sample)

		p_per_layer = np.array(p_per_layer).transpose().tolist()
		t_per_layer = np.array(t_per_layer).transpose().tolist()
	
		#print(len(p_per_layer))#, t_per_layer)
		#input("DONE")

		data = {"combo": combo, "total_time": t, "total_pwr": p }
		print(valid_layers)
		for b_idx,b in enumerate(valid_layers):
			data[b+"_pwr"] = p_per_layer[b_idx]
			data[b+"_time"] = t_per_layer[b_idx]


		#for b_idx, b in enumerate(bkeys):
		#	data[b+"_pwr"] = p_per_layer[b_idx]
		#	data[b+"_time"] = t_per_layer[b_idx]

		#print(data)

		

		#data.update(p_per_layer)
		#data.update(t_per_layer)
		df = pd.DataFrame(data)
		#print(df)
		#input()
		#exit()
		csv_out = valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/{TYPE}/{wei}/{general}.csv")
		if(OVERWRITE):
			df.to_csv(csv_out, index=False)
		else:
			if(os.path.exists(csv_out)):			
				df.to_csv(csv_out, mode="a", header=False, index=False)	
			else:
				df.to_csv(csv_out, index=False)
		continue

		pp = pp + p
		tt = tt + t
		#cc = cc + combo	

		total_l = total_l + l	

		if(need_fig):
			pass
		else:
			continue
		#print(f"done g_idx = {g_idx}")
		png = valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/{TYPE}/DSE/{g_idx}.png")
	
		plt.scatter(pp,tt)
		#plt.show()
		plt.savefig(png)#valid_file(f"generated/DSE/SECOND_PASS{POWER_MODE}/Conv/SystolicConv/DSE/{g_idx}.png"))

		#print("done")
		print(f"done save fig g_idx = {g_idx}")
		#input("continue?")
		#exit()

