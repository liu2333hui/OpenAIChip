#
#from GeneralModel import GeneralPrimitiveModel
#from re import S
#from typing import ClassVar
from power_models.GeneralModel import GeneralPrimitiveModel
#from GeneralModel import GeneralPrimitiveModel

import numpy as np

class AccumulatorPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			#check for the reset of the accumulator (todos -not critical for now)
			

			max_seq_len = len(str(row['in_0']).split(","))
			if 'reset' in row:
				pass
			else:
				row['reset'] = max_seq_len*[0]
			

			res = []
			s = 0
			for v in str(row['in_0']).split(","):
				s += int(float(v))
				res.append(s)
			return ','.join([str(r) for r in res[1:]] + ["0"])

		df['out_0'] = df.apply(
			fn
		, axis = 1)
		#print(df)

def rapid_toggle(arr):
	toggle = []
	prev = arr[0]
	for i in arr[1:]:
		toggle.append(bin(prev ^ i).count('1'))
		prev = i
	toggle.append(bin(arr[-1] ^ arr[0]).count('1'))
	return toggle, sum(toggle)/len(toggle) 

if __name__ == "__main__":
	# A = 3
	# in_val = [A, (1<<16) - A]*10
	# accum = [0]
	# for i in in_val:
	# 	accum.append( (accum[-1] + i ) % (1 << 16))
	# print(accum)
	# print(in_val)
	# print(rapid_toggle(accum))
	# print(rapid_toggle(in_val))
	# exit(0)
	pass

def AccumulatorPrimitiveTest(train = 1, out_features = 'Total_Pwr'):



	#Testing Case
	ap = AccumulatorPrimitive()
	name = "Accumulator"
	#	out_features = ['Total_Pwr']

	from pathlib import Path

	# 指定目录路径
	directory = Path('generated/Accumulator')
	train_sets =list(directory.rglob('1744*.txt'))
	train_sets = train_sets + list(directory.rglob('174188*.txt'))
	train_sets = train_sets + [f"generated/{name}/tsmc40_dataset.txt"]
	#train_sets = []
	train_sets = train_sets + ['generated/Accumulator/1741890485579.txt', f'generated/Accumulator/1741889481655.txt']
	
	#Training Mode
	if(train):
		return ap.execute_train(name = name, 
			hardware_features = ['prec_in', 'prec_out', 'terms'],
			# data_features = ['toggles_out_0', 'toggles_in_0'],
			# train_sets = [f"generated/{name}/tsmc40_dataset.txt",
			# 	f"generated/{name}/tsmc40_simple.txt"],
			data_features =['toggles_out_0', 'toggles_in_0'],
			#data_features = ['toggles_out_0', 'toggles_in_0'],
	
			train_sets =train_sets,# [f"generated/{name}/tsmc40_dataset.txt"],
			out_features = out_features,
			in_scaling = [1e5],
			out_scaling = [1e10],
			test_size = 0.01,
			delimiter='\t'
		)

	#Evaluation Mode
	in_0 = [[8888,9999, 666, 666] + [912839]+7*[1]]
	#in_0 = []
	#for i in range(len(inputs)-1):
	#	in_0.append([inputs[i], inputs[i+1]])	
	res = ap.execute_testing(
		name = name,
		out_features = out_features,
		input_data = {
			"CLOCK": [1],
			"cap_load": [1.0],
			"prec_in" : [16],
			"prec_out": [16],
			"terms": [1],
			# "in_0": [np.repeat([2,12392, 1<<15], 10) ]
			"in_0": in_0#[  [  8888,9999, 1, 1, 1, 0 ] ]
		}
	)
	print(res)
