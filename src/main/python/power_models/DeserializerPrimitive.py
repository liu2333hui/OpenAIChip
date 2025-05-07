from power_models.GeneralModel import GeneralPrimitiveModel
#from GeneralModel import GeneralPrimitiveModel


import pandas as pd

#todos, fixing the primitive
class DeserializerPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			f = 0
			#print('row',row['in_0'])
			
			r = [int(r) for r in row['in_0'].split(",")]

			#print(r)
			#print(len(r), row['out_terms'])
	
			#input()
			s = [0]
			l = len(r)
			#if(len(r) > row['out_terms']):
			#	l = len(r) - row['out_terms']
				
			for r_idx in range(0,l, row['out_terms']):
				f = 0	
				for t in range(row['out_terms']):
					if(r_idx+t >= len(r)):
						continue
					#print(len(r), r_idx,t, r_idx+t)
					#print(r[r_idx + t], end=',')
					f = (f<<int(row['prec'])) + r[r_idx+t]
				s.append(f)
				#print()
				#print(f)
				#print(r)
			#print(row)
			#print(s)
			#input()
			#exit()
			

			return ','.join([str(ss) for ss in s])#row['in_0']
		
		df['out_0'] = df.apply(fn, axis = 1)
				
#if __name__ == "__main__":
def DeserializerPrimitiveTest( out_features = ['Total_Pwr','Unit_Cycles', 'Energy'], train = 0):
	ap = DeserializerPrimitive()

	from pathlib import Path

	# 指定目录路径
	name = "Deserializer"
	directory = Path('generated/Deserializer')
	train_sets = list(directory.rglob("17444*"))
	train_sets = train_sets + list(directory.rglob('17445*.txt'))
	train_sets = train_sets + list(directory.rglob('17446*.txt'))
	
	

	#Training Mode
	#train_sets = [
        #    "generated/SRAMBanked/tsmc40_dataset_combined.txt"    
	#]

	if train:
        #     	features = ['prec1','radix', 'inv_CLOCK', 'cap_load',] + \
        # ['bits_0', 'bits_1', 'in_0', 'in_1']
        # #'in_0', 'in_1', 'bits_0', 'bits_1', 'toggle', 'prec1']
        # out = 'Unit_Cycles'#'Total_Pwr'
		return ap.execute_train(name = name, 
	 		hardware_features = ['prec', 'out_terms', 'fanout'],
	 		#data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		# data_features = ["toggles_in_0","sum_toggles_in", 'toggles_out_0','toggles_in_1'],	
	 		data_features = [
         "bits_in_0", "bits_out_0",       "toggles_in_0",'toggles_out_0'],	
	 		
			train_sets = train_sets,#["generated/AdderN/tsmc40_RCA2.txt"],
	 		out_features = out_features,#['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
	 		in_scaling = [1e5],
	 		out_scaling = [1e10],
	 		test_size = 0.1,
	 		delimiter='\t'
	 	)
	ap.get_features(name, out_features = out_features)#['Total_Pwr'])	
	repeat = 10
	r = repeat
	input_data = {
            "CLOCK": [1],
            "terms": [1],
            "cap_load": [1.0],

	    "prec": [8],
            'out_terms': [16],
            "fanout": [1],
            "in_0":[[31,3,5,0, 1, 3, 4, 8] ],
	}
	res = ap.execute_testing(
		name = name, 
		out_features = out_features,
        input_data = input_data)
	# )
	print(res)
