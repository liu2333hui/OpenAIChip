import sys


from power_models.AdderNPrimitive import *
from power_models.Multiplier2Primitive import *
from power_models.MaxNPrimitive import *

from power_models.SRAMSPrimitive import *

from power_models.MuxNPrimitive import *
from power_models.DeserializerPrimitive import *
from power_models.Parallel2SerialPrimitive import *
from power_models.MulticastPrimitive import *

import pickle

import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
import json

def hua(logs_dir,
	valid_modules = {
	"Total":["total"], 
	"PE":["PE"], 
	"CASTING":["L1_WEI_MULTICAST", "L1_ACT_MULTICAST"],
	 "L1":["L1_WEI_READ", "L1_WEI_WRITE","L1_ACT_READ", "L1_ACT_WRITE"],
	 "L2": ["L2_WEI_READ", "L2_WEI_WRITE", "L2_ACT_READ", "L2_ACT_WRITE" ], 
	"ADDER TREE": ["ADDER_ACCUM"], 
 },
	valid_models = ["baseline1", "baseline2", "estimate",],
	new_results = []
):
		
	with open("generated/ML_calibration/MuxN.pkl", "rb") as f:
    		MuxN_data = pickle.load(f)

	with open("generated/ML_calibration/Multiplier2.pkl", "rb") as f: 
		Multiplier2_data = pickle.load(f) #pickle.dump(data, f)

	with open("generated/ML_calibration/AdderN.pkl", "rb") as f:
		AdderN_data = pickle.load(f)

	with open("generated/ML_calibration/MaxN.pkl", "rb") as f:
		MaxN_data = pickle.load(f)

	with open("generated/ML_calibration/Multicast.pkl", "rb") as f:
		Multicast_data = pickle.load(f)
	
	with open("generated/ML_calibration/SRAMS.pkl", "rb") as f:
		SRAMS_data = pickle.load(f)

	with open("generated/ML_calibration/Deserializer.pkl", "rb") as f:
		Deserializer_data = pickle.load(f)
	
	with open("generated/ML_calibration/Parallel2Serial.pkl", "rb") as f:
		Parallel2Serial_data = pickle.load(f)	


	print(len(Multiplier2_data['golden']))
	print(len(MuxN_data['golden']))
	print(len(AdderN_data['golden']))
	print(len(MaxN_data['golden']))
	print(len(Multicast_data['golden']))
	print(len(SRAMS_data['golden']))
	print(len(Deserializer_data['golden']))
	print(len(Parallel2Serial_data['golden']))

	#From synthesized set to represent larger space
	combos = {
		"Total":{}, 
		"PE":{}, 
		"CASTING":{},
		 "L1":{},
		 "L2": {}, 
		"ADDER TREE": {}, 
		"SYSTOLIC":{},
		"MAX POOL":{},
		"CROSSBAR":{},
		"RECONFIG LOGIC": {},
		"WINOGRAD MAPPER": {},
	}
	malias_component = {
		"PE": "PE Array",
		"L1": "L1 Buffer",
		"CASTING": "Cast Network",
		"ADDER TREE": "Accumulator",
		"SYSTOLIC": "Load Network",
		"CROSSBAR": "Crossbar",
		"WINOGRAD MAPPER": "Wino Map",
		"RECONFIG LOGIC": "Reconfig. Logic",
		"MAX POOL": "Max Tree",


		"Total_Direct": "Dense Cores",
		"Total_Wino": "Wino. Cores",
		"Total_Sparse": "Sparse Cores",
		"Total_Reconfig": "Multi-Dataflow Cores",
		"Total_Transformer": "Transformer Cores"





	}
	valid_models = ['estimate', 'baseline1', 'baseline2']#, 'baseline3', 'baseline4']	
	malias_title = {
		"estimate": "OSCAR",
		"baseline1": "Maestro-like",
		"baseline2": "Maestro-like",

		"baseline4": "Accelergy-like",

		"baseline3": "Accelergy-like",

		"golden": 'golden',
		"our": 'OSCAR (Full Model)',
		"accelergy": 'Accelergy-like',
		"maestro": 'Maestro-like',
						
		"our_none": 'OSCAR (Hardware Only)',
		"our_toggle": 'OSCAR (Toggle Only)',
		"our_bits": 'OSCAR (Bits Only)',
	


	}

	malias = {
		"estimate": "Our Method",
		"baseline1": "Maestro-like",
		"baseline2": "Maestro-like",

		"baseline4": "Accelergy-like",

		"baseline3": "Accelergy-like",

		"golden": 'golden',
		"our": 'our',
		"accelergy": 'accelergy',
		"maestro": 'maestro',
						
		"our_none": 'our_none',
		"our_toggle": 'our_toggle',
		"our_bits": 'our_bits',
	


	}

	plot_mode = 2
	#methods = ['maestro', 'accelergy', 'our_none', 'our_toggle', 'our_bits', 'our']
	if(plot_mode == 2):
		methods = ['maestro', 'accelergy', 'our_none', 'our']	
		N = 100


	if(plot_mode == 1):
		methods = ['maestro', 'accelergy', 'our']	
		N = 1000




	UNIT = [64, 128, 256, 512]

	#Vary PE
	import random
	#print(Multiplier2_data)
	#import matplotlib.pyplot as plt
	#plt.scatter(Multiplier2_data['baseline3'], Multiplier2_data['golden_baseline3'])	
	#plt.show()

	#N = 200
	for units in UNIT:#range(UNIT):
		#units = 1<<n
		#random_index = random.randint(0, N)  # 生成随机索引
		#for b in Multiplier2_data:
		random_index = random.sample(range(len(Multiplier2_data['golden'])), k=N)
		for b in methods:
				
			if(b not in combos["PE"]):
				combos["PE"][b] =[]#units*np.array(Multiplier2_data[b])[random_index]
				combos["PE"][b+".golden"] =[]#units*np.array(Multiplier2_data[b])[random_index]
			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'

			#print("UNITS", units)

			combos["PE"][b] = np.concatenate((combos["PE"][b], units*np.array(Multiplier2_data[b])[random_index]	))
			combos["PE"][b+'.golden'] = np.concatenate((combos["PE"][b+'.golden'], units*np.array(Multiplier2_data[golden])[random_index]	))




			#combos["PE"][b] = np.concatenate((combos["PE"][b], np.array(units*(Multiplier2_data[b])[random_index])	))
			#combos["PE"][b+".golden"] = np.concatenate((combos["PE"][b+".golden"], np.array(units*Multiplier2_data[golden][random_index])	))


	print(combos["PE"].keys())
	#print(combos["PE"]['baseline3'])
	#import matplotlib.pyplot as plt
	#plt.scatter(combos["PE"]['baseline3'], combos["PE"]['baseline3.golden'])	
	#plt.show()
	#input()

	#N = 200
	#N = 100
	for units in UNIT:
		#units = 1<<n
		#random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(MuxN_data['golden'])), k=N)

		for b in methods:
			if(b not in combos["CROSSBAR"]):
				combos["CROSSBAR"][b] = []	
				combos["CROSSBAR"][b+'.golden'] = []	
	
	
			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'


	
			combos["CROSSBAR"][b] = np.concatenate((combos["CROSSBAR"][b], units*np.array(MuxN_data[b])[random_index]	))
			combos["CROSSBAR"][b+'.golden'] = np.concatenate((combos["CROSSBAR"][b+'.golden'], units*np.array(MuxN_data[golden])[random_index]	))




	#N = 100
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(MuxN_data['golden'])), k=N)


		for b in methods:
			if(b not in combos["RECONFIG LOGIC"]):
				combos["RECONFIG LOGIC"][b] = []	
				combos["RECONFIG LOGIC"][b+'.golden'] = []	
	
				
			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'




			combos["RECONFIG LOGIC"][b] = np.concatenate((combos["RECONFIG LOGIC"][b], units*np.array(MuxN_data[b])[random_index]	))
			combos["RECONFIG LOGIC"][b+".golden"] = np.concatenate((combos["RECONFIG LOGIC"][b+".golden"], units*np.array(MuxN_data[golden])[random_index]	))




			#combos["RECONFIG LOGIC"][b] += units*MuxN_data[b][random_index]	

	#N = 100
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(AdderN_data[b])), k=N)

		for b in methods:
			if(b not in combos["ADDER TREE"]):
				combos["ADDER TREE"][b] = []		
				combos["ADDER TREE"][b+'.golden'] = []		
	

			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'


	
			combos["ADDER TREE"][b] = np.concatenate((combos["ADDER TREE"][b], units*np.array(AdderN_data[b])[random_index]	))
			combos["ADDER TREE"][b+'.golden'] = np.concatenate((combos["ADDER TREE"][b+'.golden'], units*np.array(AdderN_data[golden])[random_index]	))




			#combos["ADDER TREE"][b] += units*AdderN_data[b][random_index]	

	#N = 100
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(AdderN_data['golden'])), k=N)


		for b in MuxN_data:

			if(b not in combos["WINOGRAD MAPPER"]):
				combos["WINOGRAD MAPPER"][b] = []		
				combos["WINOGRAD MAPPER"][b+'.golden'] = []		
	
			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'


	
			combos["WINOGRAD MAPPER"][b+'.golden'] = np.concatenate((combos["WINOGRAD MAPPER"][b+'.golden'], units*np.array(AdderN_data[golden])[random_index]	))
			combos["WINOGRAD MAPPER"][b] = np.concatenate((combos["WINOGRAD MAPPER"][b], units*np.array(AdderN_data[b])[random_index]	))




			#c#ombos["WINOGRAD MAPPER"][b] += units*AdderN_data[b][random_index]	

	#N = 100
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(MaxN_data[b])), k=N)

		for b in methods:
			if(b not in combos["MAX POOL"]):
				combos["MAX POOL"][b] = []			
				combos["MAX POOL"][b+'.golden'] = []			
	
	
			combos["MAX POOL"][b] = np.concatenate((combos["MAX POOL"][b], units*np.array(MaxN_data[b])[random_index]	))

			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'


			combos["MAX POOL"][b+'.golden'] = np.concatenate((combos["MAX POOL"][b+'.golden'], units*np.array(MaxN_data[golden])[random_index]	))


	
			#combos["MAX POOL"][b] += units*MaxN_data[b][random_index]	

	#N = 100
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(Multicast_data['golden'])), k=N)
	
		for b in Multicast_data:
			if(b == 'golden_baseline3' or b == 'golden_baseline4'):
				continue
			#if('golden' in b):
			#	continue
			#print(Multicast_data.keys())
			#input()
			if(b not in combos["CASTING"]):
				combos["CASTING"][b] = []			
				combos["CASTING"][b+'.golden'] = []			
	
			#combos["CASTING"][b] += units*Multicast_data[b][random_index]	
			combos["CASTING"][b] = np.concatenate((combos["CASTING"][b], units*np.array(Multicast_data[b])[random_index]	))
			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'

			print(len(Multicast_data[golden]), len(Multicast_data[b]))
			combos["CASTING"][b+'.golden'] = np.concatenate((combos["CASTING"][b+'.golden'], units*np.array(Multicast_data[golden])[random_index]	))





	#N = 100
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(SRAMS_data['golden'])), k=N)

		for b in methods:
			if(b not in combos["L1"]):
				combos["L1"][b] = []				
				combos["L1"][b+'.golden'] = []				


			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'

			if(N>len(SRAMS_data[golden])):
				N = len(SRAMS_data[golden])-1	
	
			combos["L1"][b] = np.concatenate((combos["L1"][b], units*np.array(SRAMS_data[b])[random_index]	))


	
			combos["L1"][b+'.golden'] = np.concatenate((combos["L1"][b+'.golden'], units*np.array(SRAMS_data[golden])[random_index]	))




			#combos["L1"][b] = units*SRAMS_data[b][random_index]	

	#N = 100
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(SRAMS_data['golden'])), k=N)

		for b in methods:
			if(b not in combos["L2"]):
				combos["L2"][b] = []				
				combos["L2"][b+'.golden'] = []						

			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'



			combos["L2"][b] = np.concatenate((combos["L2"][b], units*np.array(SRAMS_data[b])[random_index]	))


			combos["L2"][b+'.golden'] = np.concatenate((combos["L2"][b+'.golden'], units*np.array(SRAMS_data[golden])[random_index]	))



			#combos["L2"][b] = units*SRAMS_data[b][random_index]	


	#N = 100
	#N = 200
	for units in UNIT:
		#units = 1<<n
		random_index = random.randint(0, N)  # 生成随机索引

		random_index = random.sample(range(len(Deserializer_data['golden'])), k=N)

		for b in methods:
			if(b not in combos["SYSTOLIC"]):
				combos["SYSTOLIC"][b] = []				
				combos["SYSTOLIC"][b+'.golden'] = []				
	
	
			if(b in ['baseline3', 'baseline4']):
				golden = "golden_"+b
			else:
				golden = 'golden'



			combos["SYSTOLIC"][b] = np.concatenate((combos["SYSTOLIC"][b], units*np.array(Deserializer_data[b])[random_index]	))
			combos["SYSTOLIC"][b+'.golden'] = np.concatenate((combos["SYSTOLIC"][b+'.golden'], units*np.array(Deserializer_data[golden])[random_index]	))




			#combos["SYSTOLIC"][b] =  units*Deserializer_data[b][random_index] + units*Parallel2Serial_data[b][random_index]	

	#####Total_Direct
	#PE, L1, L2, Casting, Adder Tree, Systolic, Max Pool
	combos['Total_Direct'] = {}
	N = 100
	SAMPLE = 10
	UNIT = [1]#64, 128]
	U = 512
	for units in UNIT:	

		for s in range(SAMPLE):
			MuxN_idx = random.sample(range(len(MuxN_data['golden'])), k=N)
			Multiplier2_idx = random.sample(range(len(Multiplier2_data['golden'])), k=N)
			AdderN_idx = random.sample(range(len(AdderN_data['golden'])), k=N)
			MaxN_idx = random.sample(range(len(MaxN_data['golden'])), k=N)
			Multicast_idx = random.sample(range(len(Multicast_data['golden'])), k=N)
			SRAMS_idx = random.sample(range(len(SRAMS_data['golden'])), k=N)
			Deserializer_idx = random.sample(range(len(Deserializer_data['golden'])), k=N)
			Parallel2Serial_idx = random.sample(range(len(Parallel2Serial_data['golden'])), k=N)

			units1 = random.sample(range(U), k=N)
			units2 = random.sample(range(U), k=N)
			units3 = random.sample(range(U), k=N)
			units4 = random.sample(range(U), k=N)
			units5 = random.sample(range(U), k=N)
			units6 = random.sample(range(U), k=N)
			units7 = random.sample(range(U), k=N)
			units8 = random.sample(range(U), k=N)
			
			for b in methods:
				if(b not in combos["Total_Direct"]):
					combos["Total_Direct"][b] = []				
					combos["Total_Direct"][b+'.golden'] = []				

				total = units1*np.array(Deserializer_data[b])[Deserializer_idx] \
				    +   units2*np.array(Parallel2Serial_data[b])[Parallel2Serial_idx] \
				    +   units3*np.array(SRAMS_data[b])[SRAMS_idx] \
				    +   units4*np.array(Multicast_data[b])[Multicast_idx] \
				    +   units5*np.array(MaxN_data[b])[MaxN_idx] \
				    +   units6*np.array(AdderN_data[b])[AdderN_idx] \
				    +   units7*np.array(Multiplier2_data[b])[Multiplier2_idx] \
				 #   +   units8*np.array(MuxN_data[b])[MuxN_idx] \
	
				golden_total = units1*np.array(Deserializer_data['golden'])[Deserializer_idx] \
				    +   units2*np.array(Parallel2Serial_data['golden'])[Parallel2Serial_idx] \
				    +   units3*np.array(SRAMS_data['golden'])[SRAMS_idx] \
				    +   units4*np.array(Multicast_data['golden'])[Multicast_idx] \
				    +   units5*np.array(MaxN_data['golden'])[MaxN_idx] \
				    +   units6*np.array(AdderN_data['golden'])[AdderN_idx] \
				    +   units7*np.array(Multiplier2_data['golden'])[Multiplier2_idx] \
				  #  +   units*np.array(MuxN_data['golden'])[MuxN_idx] \
	

				combos["Total_Direct"][b] = np.concatenate((combos["Total_Direct"][b], total   	))
				combos["Total_Direct"][b+'.golden'] = np.concatenate((combos["Total_Direct"][b+'.golden'], golden_total	))




	#####Total_Direct
	#PE, L1, L2, Casting, Adder Tree, Systolic, Max Pool
	combos['Total_Direct'] = {}
	N = 100
	SAMPLE = 1
	UNIT = [64, 128, 256, 512]
	for units in UNIT:	

		for s in range(SAMPLE):
			MuxN_idx = random.sample(range(len(MuxN_data['golden'])), k=N)
			Multiplier2_idx = random.sample(range(len(Multiplier2_data['golden'])), k=N)
			AdderN_idx = random.sample(range(len(AdderN_data['golden'])), k=N)
			MaxN_idx = random.sample(range(len(MaxN_data['golden'])), k=N)
			Multicast_idx = random.sample(range(len(Multicast_data['golden'])), k=N)
			SRAMS_idx = random.sample(range(len(SRAMS_data['golden'])), k=N)
			Deserializer_idx = random.sample(range(len(Deserializer_data['golden'])), k=N)
			Parallel2Serial_idx = random.sample(range(len(Parallel2Serial_data['golden'])), k=N)
			for b in methods:
				if(b not in combos["Total_Direct"]):
					combos["Total_Direct"][b] = []				
					combos["Total_Direct"][b+'.golden'] = []				

				total = units*np.array(Deserializer_data[b])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data[b])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data[b])[SRAMS_idx] \
				    +   units*np.array(Multicast_data[b])[Multicast_idx] \
				    +   units*np.array(MaxN_data[b])[MaxN_idx] \
				    +   units*np.array(AdderN_data[b])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data[b])[Multiplier2_idx] \
				 #   +   units*np.array(MuxN_data[b])[MuxN_idx] \
	
				golden_total = units*np.array(Deserializer_data['golden'])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data['golden'])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data['golden'])[SRAMS_idx] \
				    +   units*np.array(Multicast_data['golden'])[Multicast_idx] \
				    +   units*np.array(MaxN_data['golden'])[MaxN_idx] \
				    +   units*np.array(AdderN_data['golden'])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data['golden'])[Multiplier2_idx] \
				  #  +   units*np.array(MuxN_data['golden'])[MuxN_idx] \
	

				combos["Total_Direct"][b] = np.concatenate((combos["Total_Direct"][b], total   	))
				combos["Total_Direct"][b+'.golden'] = np.concatenate((combos["Total_Direct"][b+'.golden'], golden_total	))



	
	#####Total_Sparse
	#PE, L1, L2, Casting, Adder Tree, Syystolic, Max Pool
	name = "Total_Sparse"
	#PE, L1, L2, Casting, Adder Tree, Systolic, Max Pool
	combos[name] = {}
	N = 100
	SAMPLE = 1
	for units in UNIT:	

		for s in range(SAMPLE):
			MuxN_idx = random.sample(range(len(MuxN_data['golden'])), k=N)
			Multiplier2_idx = random.sample(range(len(Multiplier2_data['golden'])), k=N)
			AdderN_idx = random.sample(range(len(AdderN_data['golden'])), k=N)
			MaxN_idx = random.sample(range(len(MaxN_data['golden'])), k=N)
			Multicast_idx = random.sample(range(len(Multicast_data['golden'])), k=N)
			SRAMS_idx = random.sample(range(len(SRAMS_data['golden'])), k=N)
			Deserializer_idx = random.sample(range(len(Deserializer_data['golden'])), k=N)
			Parallel2Serial_idx = random.sample(range(len(Parallel2Serial_data['golden'])), k=N)
			for b in methods:
				if(b not in combos[name]):
					combos[name][b] = []				
					combos[name][b+'.golden'] = []				

				total = units*np.array(Deserializer_data[b])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data[b])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data[b])[SRAMS_idx] \
				    +   units*np.array(Multicast_data[b])[Multicast_idx] \
				    +   units*np.array(MaxN_data[b])[MaxN_idx] \
				    +   units*np.array(AdderN_data[b])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data[b])[Multiplier2_idx] \
				    +  32* units*np.array(MuxN_data[b])[MuxN_idx] \
	
				golden_total = units*np.array(Deserializer_data['golden'])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data['golden'])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data['golden'])[SRAMS_idx] \
				    +   units*np.array(Multicast_data['golden'])[Multicast_idx] \
				    +   units*np.array(MaxN_data['golden'])[MaxN_idx] \
				    +   units*np.array(AdderN_data['golden'])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data['golden'])[Multiplier2_idx] \
				    +  32*units*np.array(MuxN_data['golden'])[MuxN_idx] \
	

				combos[name][b] = np.concatenate((combos[name][b], total   	))
				combos[name][b+'.golden'] = np.concatenate((combos[name][b+'.golden'], golden_total	))



	#####Total_Sparse
	#PE, L1, L2, Casting, Adder Tree, Syystolic, Max Pool
	name = "Total_Transformer"
	#PE, L1, L2, Casting, Adder Tree, Systolic, Max Pool
	combos[name] = {}
	N = 100
	SAMPLE = 1
	for units in UNIT:	

		for s in range(SAMPLE):
			MuxN_idx = random.sample(range(len(MuxN_data['golden'])), k=N)
			Multiplier2_idx = random.sample(range(len(Multiplier2_data['golden'])), k=N)
			AdderN_idx = random.sample(range(len(AdderN_data['golden'])), k=N)
			MaxN_idx = random.sample(range(len(MaxN_data['golden'])), k=N)
			Multicast_idx = random.sample(range(len(Multicast_data['golden'])), k=N)
			SRAMS_idx = random.sample(range(len(SRAMS_data['golden'])), k=N)
			Deserializer_idx = random.sample(range(len(Deserializer_data['golden'])), k=N)
			Parallel2Serial_idx = random.sample(range(len(Parallel2Serial_data['golden'])), k=N)
			for b in methods:
				if(b not in combos[name]):
					combos[name][b] = []				
					combos[name][b+'.golden'] = []				

				total = units*np.array(Deserializer_data[b])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data[b])[Parallel2Serial_idx] \
				    +  2* units*np.array(SRAMS_data[b])[SRAMS_idx] \
				    +   units*np.array(Multicast_data[b])[Multicast_idx] \
				    +   units*np.array(MaxN_data[b])[MaxN_idx] \
				    +   2*units*np.array(AdderN_data[b])[AdderN_idx] \
				    +   3*units*np.array(Multiplier2_data[b])[Multiplier2_idx] \
				 #   +  32* units*np.array(MuxN_data[b])[MuxN_idx] \
	
				golden_total = units*np.array(Deserializer_data['golden'])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data['golden'])[Parallel2Serial_idx] \
				    +   2*units*np.array(SRAMS_data['golden'])[SRAMS_idx] \
				    +   units*np.array(Multicast_data['golden'])[Multicast_idx] \
				    +   units*np.array(MaxN_data['golden'])[MaxN_idx] \
				    +  2* units*np.array(AdderN_data['golden'])[AdderN_idx] \
				    + 3*  units*np.array(Multiplier2_data['golden'])[Multiplier2_idx] \
				#    +  32*units*np.array(MuxN_data['golden'])[MuxN_idx] \
	

				combos[name][b] = np.concatenate((combos[name][b], total   	))
				combos[name][b+'.golden'] = np.concatenate((combos[name][b+'.golden'], golden_total	))






	#####Total_Wino
	#PE, L1, L2, Casting, Adder Tree, Syystolic, Max Pool
	name = "Total_Wino"
	#PE, L1, L2, Casting, Adder Tree, Systolic, Max Pool
	combos[name] = {}
	N = 100
	SAMPLE = 1
	for units in UNIT:	

		for s in range(SAMPLE):
			MuxN_idx = random.sample(range(len(MuxN_data['golden'])), k=N)
			Multiplier2_idx = random.sample(range(len(Multiplier2_data['golden'])), k=N)
			AdderN_idx = random.sample(range(len(AdderN_data['golden'])), k=N)
			MaxN_idx = random.sample(range(len(MaxN_data['golden'])), k=N)
			Multicast_idx = random.sample(range(len(Multicast_data['golden'])), k=N)
			SRAMS_idx = random.sample(range(len(SRAMS_data['golden'])), k=N)
			Deserializer_idx = random.sample(range(len(Deserializer_data['golden'])), k=N)
			Parallel2Serial_idx = random.sample(range(len(Parallel2Serial_data['golden'])), k=N)
			for b in methods:
				if(b not in combos[name]):
					combos[name][b] = []				
					combos[name][b+'.golden'] = []				

				total = units*np.array(Deserializer_data[b])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data[b])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data[b])[SRAMS_idx] \
				    +   units*np.array(Multicast_data[b])[Multicast_idx] \
				    +   units*np.array(MaxN_data[b])[MaxN_idx] \
				    +  6* units*np.array(AdderN_data[b])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data[b])[Multiplier2_idx] \
			#	    +  3* units*np.array(MuxN_data[b])[MuxN_idx] \
	
				golden_total = units*np.array(Deserializer_data['golden'])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data['golden'])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data['golden'])[SRAMS_idx] \
				    +   units*np.array(Multicast_data['golden'])[Multicast_idx] \
				    +   units*np.array(MaxN_data['golden'])[MaxN_idx] \
				    +   6*units*np.array(AdderN_data['golden'])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data['golden'])[Multiplier2_idx] \
			#	    +   units*np.array(MuxN_data['golden'])[MuxN_idx] \
	

				combos[name][b] = np.concatenate((combos[name][b], total   	))
				combos[name][b+'.golden'] = np.concatenate((combos[name][b+'.golden'], golden_total	))





	#####Total_Reconfig
	#PE, L1, L2, Casting, Adder Tree, Syystolic, Max Pool
	name = "Total_Reconfig"
	#PE, L1, L2, Casting, Adder Tree, Systolic, Max Pool
	combos[name] = {}
	N = 100
	SAMPLE = 1
	for units in UNIT:	

		for s in range(SAMPLE):
			MuxN_idx = random.sample(range(len(MuxN_data['golden'])), k=N)
			Multiplier2_idx = random.sample(range(len(Multiplier2_data['golden'])), k=N)
			AdderN_idx = random.sample(range(len(AdderN_data['golden'])), k=N)
			MaxN_idx = random.sample(range(len(MaxN_data['golden'])), k=N)
			Multicast_idx = random.sample(range(len(Multicast_data['golden'])), k=N)
			SRAMS_idx = random.sample(range(len(SRAMS_data['golden'])), k=N)
			Deserializer_idx = random.sample(range(len(Deserializer_data['golden'])), k=N)
			Parallel2Serial_idx = random.sample(range(len(Parallel2Serial_data['golden'])), k=N)
			for b in methods:
				if(b not in combos[name]):
					combos[name][b] = []				
					combos[name][b+'.golden'] = []				

				total = units*np.array(Deserializer_data[b])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data[b])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data[b])[SRAMS_idx] \
				    +   units*np.array(Multicast_data[b])[Multicast_idx] \
				    +   units*np.array(MaxN_data[b])[MaxN_idx] \
				    +   units*np.array(AdderN_data[b])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data[b])[Multiplier2_idx] \
				    +  8* units*np.array(MuxN_data[b])[MuxN_idx] \
	
				golden_total = units*np.array(Deserializer_data['golden'])[Deserializer_idx] \
				    +   units*np.array(Parallel2Serial_data['golden'])[Parallel2Serial_idx] \
				    +   units*np.array(SRAMS_data['golden'])[SRAMS_idx] \
				    +   units*np.array(Multicast_data['golden'])[Multicast_idx] \
				    +   units*np.array(MaxN_data['golden'])[MaxN_idx] \
				    +   units*np.array(AdderN_data['golden'])[AdderN_idx] \
				    +   units*np.array(Multiplier2_data['golden'])[Multiplier2_idx] \
				    +   8*units*np.array(MuxN_data['golden'])[MuxN_idx] \
	

				combos[name][b] = np.concatenate((combos[name][b], total   	))
				combos[name][b+'.golden'] = np.concatenate((combos[name][b+'.golden'], golden_total	))


	##############3
	#Generate Total
	#N = 200
	for units in UNIT:
		#units = 1<<n
		ramodels = len(valid_models)
	#methods = ['estimate', 'baseline1', 'baseline2', 'baseline3', 'baseline4']
	##########################
	####PLOTTING DIMENSIONS
	#methods = ['baseline2', 'baseline3', 'estimate']
	if(plot_mode == 1):
		combos ={ k: combos[k]  for k in  combos.keys() if k not in ['Total_Direct', 'Total_Wino', 'Total_Sparse', "Total", "RECONFIG LOGIC", "L2", "Total_Reconfig", "Total_Transformer"] }
	#plot_mode = 1
	if(plot_mode == 2):
		combos ={ k: combos[k]  for k in  combos.keys() if k in ["Total_Direct","Total_Wino", "Total_Sparse", "Total_Reconfig", "Total_Transformer"]}# "Total_Wino" ] }	
	#plot_mode = 2
	#########################



	print(combos)
	#input()
	
	
	models = len(methods)# ['estimate', 'baseline1', 'baseline2', 'baseline3', 'baseline4'])

	modules = len(combos.keys())


	if(plot_mode == 2):
		DIM = 2
		fig, axes = plt.subplots(nrows=models//DIM, ncols=DIM, figsize=(9, 8)) 
		#axes[-1, 0 ].set_xlabel("Ground Truth (mW)")
	else:	
		fig, axes = plt.subplots(nrows=models, ncols=modules, figsize=(13, 6.5)) 

	#all_data[0].to_csv('output.csv', index=False)


	if(plot_mode == 2):
		


		for idx,method in enumerate(methods):
			#prepare the R and MAPE	
			g = []
			m = []
			for hidx,components in enumerate(combos):
				golden = combos[components].get(method+'.golden', combos[components].get('golden', "-1"))
				model_estimate = combos[components][method]
				m.append(model_estimate)
				g.append(golden)
	
			g = np.array([item for sublist in g for item in sublist])
			m = np.array([item for sublist in m for item in sublist])



			#print(axes)
			power_mse = mean_squared_error( m  , g   )
			power_r = r2_score( m  , g  )


			relative_errors = np.abs((m - g) )
			power_abs = np.mean(relative_errors)
	

			relative_errors = np.abs((model_estimate - golden) / (golden+1e-19))
			relative_errors = [r for r in relative_errors if r < 1.0]
					
			power_relative = np.mean(relative_errors)
	 
			text = "MAPE:%.1f" %(100*power_relative)   +  "%"  +"\nR:%.2f"  %(power_r)#f'MSE: {mse:.2f}\nR: {r:.2f}'
			axes[idx//DIM, idx % DIM].legend(loc='lower right',fontsize=10)


			axes[idx//DIM,idx%DIM].text(0.05, 0.95, text, transform=axes[idx//DIM,idx%DIM].transAxes, fontsize=10,
 		           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

			
		for idx,method in enumerate(methods):

			#plot based on type of unit
			for hidx,components in enumerate(combos):
				print(components, methods, combos[components])
				print(combos[components].keys())
				print(method)
				golden = combos[components].get(method+'.golden', combos[components].get('golden', "-1"))
				print(len(golden)	)
				#golden = combos[components]['golden']
				model_estimate = combos[components][method]

				print(len(golden)	)
				print(len(model_estimate)	)



				#print("MODEL_ESTIMATE", components, method, model_estimate)
				axes[idx//DIM, idx % DIM].scatter(1000*golden, 1000*model_estimate, label=malias_component[components], marker='.', alpha =0.3)	#full reconfig flows
				axes[idx//DIM, idx % DIM].legend(loc='lower right',fontsize=8)


	
	
				#axes[idx//DIM, idx % DIM].legend(loc='lower right',fontsize=8)

				#power_mse = mean_squared_error( model_estimate  , golden  )
				#power_r = r2_score( model_estimate  , golden  )


				#relative_errors = np.abs((model_estimate - golden) )
				#power_abs = np.mean(relative_errors)
	

				#relative_errors = np.abs((model_estimate - golden) / (golden+1e-19))
				#relative_errors = [r for r in relative_errors if r < 1.0]
				#print(np.max(relative_errors))
				#print(np.min(relative_errors))	
				#input()
					
				power_relative = np.mean(relative_errors)
	 
				#if(hidx == 0):	
					#text = "MAPE:%.1f" %(100*power_relative)   +  "%"  +"\nR:%.2f"  %(power_r)#f'MSE: {mse:.2f}\nR: {r:.2f}'
					#axes[idx//DIM,idx%DIM].text(0.05, 0.95, text, transform=axes[idx//DIM,idx%DIM].transAxes, fontsize=8,
# 		           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))


				axes[idx//DIM,idx%DIM].plot(1000*golden, 1000*golden, 'r')
	
				ax = axes[idx//DIM,idx%DIM]
				ax.set_aspect('equal')
				#ax.set_xlim(0, 1000)
				#ax.set_ylim(0, 1000)

				ax.set_xlim(0, 1000)
				ax.set_ylim(0, 1200)
				#axes[idx, hidx].set_xlim(0, min(50, np.max(golden)*1000))
				#axes[idx, hidx].set_ylim(0, min(50*1.2, np.max(golden)*1200))



				#if(idx == 0):
				#axes[idx//3,idx%3].set_title(method)	
				ax.set_title(malias_title[method])	

				axes[idx//DIM, idx%DIM].set_xlabel(f'Golden Power (mW)')
				if(hidx == 0):
					axes[idx//DIM,idx%DIM].set_ylabel(f'Predicted Power (mW)')
					#axes[idx].set_ylabel(f'Model Power (mW)')
	
					
					i = idx
					#axes[idx//2,1].text(-0.35, -0.55, f'({chr(ord("a")+i)}) {malias_title[method]}', ha='center', va='bottom', transform=axes[idx//2, 1].transAxes, fontsize=12)
					#axes[idx//2,1].text(-0.35, -0.35, f'Ground Truth (mW)', ha='center', va='bottom', transform=axes[idx//2,1].transAxes, fontsize=10)




 


		fig.subplots_adjust(left=0.06, right=0.96, bottom=0.10, top=0.96, wspace=0.2, hspace=0.3)
		#fig.subplots_adjust(left=0.06, right=0.96, bottom=0.12, top=0.96, wspace=0.5, hspace=0.7)



		#plt.axis('equal')  # 确保数据区域比例一致

		from DSE import valid_file
		#plt.savefig(valid_file('generated/images/total.svg'),format='svg', dpi = 300	)
		plt.savefig(valid_file('generated/images/total.png'),format='png', dpi = 300	)



		plt.show()


		return

	#look at folders and designs
	all_data = []#pd.DataFrame()
	for res in logs_dir:
		for root, dirs, files in os.walk(res):
			for dir_name in dirs:
				design_dir = os.path.join(root, dir_name)
				collection = pd.DataFrame()
				for file_name in os.listdir(design_dir):	
					file_path = os.path.join(design_dir, file_name)
					df = pd.read_csv(file_path, sep='\t')
							
					#all_data = pd.concat([all_data, df], ignore_index=True)
					collection = pd.concat([collection, df], ignore_index=True)	
				if(not collection.empty):
					all_data.append(collection)

	merge_data = pd.DataFrame()
	for mod_df in all_data:
		merge_data = pd.concat([merge_data, mod_df], ignore_index=True)	

	#first pass (golden)
	print(merge_data)
	#for mod_df in merge_data:	
	mod_df = merge_data.fillna(0)
	#axes[-1, len(combos)//2 ].set_xlabel("golden (W)")



	#axes[-1, len(combos)//2 ].set_xlabel("Ground Truth (mW)")



	#print(mod_df)
	if True:
		for hidx, hardware in enumerate(valid_modules):
			keys = valid_modules[hardware]	
			print("keys", keys)
			print("mod_df", mod_df)
			if(len(keys) == 1):
				
				golden = mod_df[[k+"_golden_pwr" for k in keys]]
			else:
				golden = np.sum(np.array(mod_df[[k+"_golden_pwr" for k in keys]]), axis=-1)
			for idx, mm in enumerate(valid_models):
				if(idx == 0):
					axes[idx, hidx].set_title(hardware)	
				if(hidx == 0):
					axes[idx, hidx].set_ylabel(f'{malias[mm]} (mW)')
	
					
				
				golden = np.array(golden)

				#errors
				if(len(keys) == 1):
					model_estimate = mod_df[[k+"_"+mm+"_pwr" for k in keys]]
				else:
					model_estimate = np.sum(np.array(mod_df[[k+"_"+mm+"_pwr" for k in keys]]), axis=-1)
				model_estimate = np.array(model_estimate)
	
				power_mse = mean_squared_error( model_estimate  , golden  )
				power_r = r2_score( model_estimate  , golden  )

				relative_errors = np.abs((model_estimate - golden) / (golden+1e-19))
				relative_errors = [r for r in relative_errors if r < 1.0]	
				power_relative = np.mean(relative_errors)

	 
				#text = "MSE:%f\nR:%f\nErr:%f" %(power_mse, power_r, power_relative)#f'MSE: {mse:.2f}\nR: {r:.2f}'
				#axes[idx, hidx].text(0.05, 0.95, text, transform=axes[idx,hidx].transAxes, fontsize=8,
 #           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))


				axes[idx, hidx].plot(golden, golden, 'r')

	#second pass (against golden)
	for mod_df in all_data:
		
		for hidx, hardware in enumerate(valid_modules):

			keys = valid_modules[hardware]	
			if(keys[0]+"_golden_pwr" not in mod_df.columns ):
				continue
			print(mod_df[keys[0]+"_golden_pwr"])
			if(len(keys) == 1):
				golden = mod_df[[k+"_golden_pwr" for k in keys]]
			else:
				golden = np.sum(np.array(mod_df[[k+"_golden_pwr" for k in keys]]), axis=-1)
	
			for idx, mm in enumerate(valid_models):
				if(len(keys) == 1):
					model_estimate = mod_df[[k+"_"+mm+"_pwr" for k in keys]]
				else:
					model_estimate = np.sum(np.array(mod_df[[k+"_"+mm+"_pwr" for k in keys]]), axis=-1)
				golden = np.array(golden)
				model_estimate = np.array(model_estimate)
				
				#axes[idx, hidx].scatter(golden, model_estimate)	
	
 

	#third pass (against larger space)
	print(combos)
	for idx,method in enumerate(methods):
	
		print(method)

		for hidx,components in enumerate(combos):
			#print(components, methods, combos[components])
			#print(combos[components])
			golden = combos[components].get(method+'.golden', combos[components].get('golden', -1))
			#golden = combos[components]['golden']
			model_estimate = combos[components][method]
			print("MODEL_ESTIMATE", components, method, model_estimate)
			axes[idx, hidx].scatter(1000*golden, 1000*model_estimate, marker='.',color='b', alpha = 0.2)	#full reconfig flows


			power_mse = mean_squared_error( model_estimate  , golden  )
			power_r = r2_score( model_estimate  , golden  )


			relative_errors = np.abs((model_estimate - golden) )
			power_abs = np.mean(relative_errors)
	

			relative_errors = np.abs((model_estimate - golden) / (golden+1e-19))
			relative_errors = [r for r in relative_errors if r < 1.0]
			power_relative = np.mean(relative_errors)
			#print(np.max(relative_errors))
			#print(np.min(relative_errors))
			#input()
	 
			text = "MAPE:%.1f" %(100*power_relative)   +  "%"  +"\nR:%.2f"  %(power_r)#f'MSE: {mse:.2f}\nR: {r:.2f}'
			axes[idx, hidx].text(0.05, 0.95, text, transform=axes[idx,hidx].transAxes, fontsize=10,
 	           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))


			axes[idx, hidx].plot(1000*golden, 1000*golden, 'r')

			if(not("WINO" in components or "ADDER" in components)):
				axes[idx, hidx].set_xlim(0, min(500, np.max(golden)*1000))
				axes[idx, hidx].set_ylim(0, min(500*1.2, np.max(golden)*1200))
			else:
				axes[idx, hidx].set_xlim(0, min(50, np.max(golden)*1000))
				axes[idx, hidx].set_ylim(0, min(50*1.2, np.max(golden)*1200))



			axes[idx, hidx].set_aspect('equal')
		
			
	


			if(idx == 0):
				axes[idx, hidx].set_title(malias_component[components])	

			if(hidx == 0):
				#axes[idx, hidx].set_ylabel(f'{malias[method]} (mW)')
				axes[idx, hidx].set_ylabel(f'Predicted Power (mW)')
	
					
				i = idx
				axes[idx,len(combos)//2].text(-0.35, -0.55, f'({chr(ord("a")+i)}) {malias_title[method]}', ha='center', va='bottom', transform=axes[idx,len(combos)//2].transAxes, fontsize=12)
				axes[idx,len(combos)//2].text(-0.35, -0.35, f'Ground Truth (mW)', ha='center', va='bottom', transform=axes[idx,len(combos)//2].transAxes, fontsize=10)



			
	

 


	fig.subplots_adjust(left=0.06, right=0.96, bottom=0.12, top=0.96, wspace=0.5, hspace=0.3)

	#plt.axis('equal')  # 确保数据区域比例一致
	#plt.#tight_layout()  # 避免标签被裁剪


	from DSE import valid_file
	plt.savefig(valid_file('generated/images/components.png'), dpi=300	)
	#plt.savefig(valid_file('generated/images/total.svg'),format='svg', dpi = 300	)


	plt.show()




def collect():

	out_features = ["Total_Pwr"]
	train = 1


	data = Multiplier2PrimitiveTest(out_features = out_features, train = train)
	with open("generated/ML_calibration/Multiplier2.pkl", "wb") as f: 
		pickle.dump(data, f)



	data = MuxNPrimitiveTest(out_features = out_features, train = train)
	print(data)
	with open("generated/ML_calibration/MuxN.pkl", "wb") as f:
		pickle.dump(data, f)

	data = AdderNPrimitiveTest(out_features = out_features, train = train)
	with open("generated/ML_calibration/AdderN.pkl", "wb") as f:
		pickle.dump(data, f)

	data = MaxNPrimitiveTest(out_features = out_features, train = train)
	with open("generated/ML_calibration/MaxN.pkl", "wb") as f:
		pickle.dump(data, f)

	data = MulticastPrimitiveTest(out_features = out_features, train = train)
	with open("generated/ML_calibration/Multicast.pkl", "wb") as f:
		pickle.dump(data, f)
	
	data = SRAMSPrimitiveTest(out_features = out_features, train = train)
	with open("generated/ML_calibration/SRAMS.pkl", "wb") as f:
		pickle.dump(data, f)

	data = DeserializerPrimitiveTest(out_features = out_features, train = train)
	with open("generated/ML_calibration/Deserializer.pkl", "wb") as f:
		pickle.dump(data, f)
	
	data = Parallel2SerialPrimitiveTest(out_features = out_features, train = train)	
	with open("generated/ML_calibration/Parallel2Serial.pkl", "wb") as f:
		pickle.dump(data, f)


	
if __name__ == "__main__":
	#collect()
	#FLOW 1
	results_folder = [
		#"generated/Architecture/SimpleArch/log_full_0321_50",
	"generated/Architecture/SimpleArch/log_full_0320",
"generated/Architecture/SimpleArch/log_accumulator_0320",
"generated/Architecture/SimpleArch/log_accumulator","generated/Architecture/SimpleArch/logs"]
	valid_modules = {"Total":["total"], "PE":["PE"], "INTERCONNECT":["L1_WEI_MULTICAST", "L1_ACT_MULTICAST"], "L1":["L1_WEI_READ", "L1_WEI_WRITE","L1_ACT_READ", "L1_ACT_WRITE"], "L2": ["L2_WEI_READ", "L2_WEI_WRITE", "L2_ACT_READ", "L2_ACT_WRITE" ], "ADDER TREE": [ "ADDER_TREE"]}#,"ACCUM":["ACCUMULATOR"]  }
	valid_models = ["baseline1", "baseline2", "estimate",]


	#FLOW 2
	hua(results_folder, valid_modules=valid_modules, valid_models=valid_models)
	#	new_model = results_folder)
