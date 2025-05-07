from power_models.GeneralModel import GeneralPrimitiveModel
#from GeneralModel import GeneralPrimitiveModel


import pandas as pd

#todos, fixing the primitive
class MulticastPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			return row['in_0']

		df['out_0'] = df.apply(fn, axis = 1)
				
#if __name__ == "__main__":
def MulticastPrimitiveTest( out_features = ['Total_Pwr','Unit_Cycles', 'Energy'], train = 0):
	ap = MulticastPrimitive()

	from pathlib import Path

	# 指定目录路径
	name = "Multicast"
	directory = Path('generated/Multicast')
	#train_sets = list(directory.rglob('174402*.txt'))
	

	#Training Mode
	train_sets = [
            "generated/Multicast/tsmc40_dataset.txt"    
	]

	if train:
        #     	features = ['prec1','radix', 'inv_CLOCK', 'cap_load',] + \
        # ['bits_0', 'bits_1', 'in_0', 'in_1']
        # #'in_0', 'in_1', 'bits_0', 'bits_1', 'toggle', 'prec1']
        # out = 'Unit_Cycles'#'Total_Pwr'
		return ap.execute_train(name = name, 
	 		hardware_features = ['prec', 'terms', 'fanout'],
	 		#data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		# data_features = ["toggles_in_0","sum_toggles_in", 'toggles_out_0','toggles_in_1'],	
	 		data_features = [
                "toggles_in_0", "bits_in_0"],#'toggles_out_0'],	
	 		
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
            'out_terms': [1],
            "fanout": [16],
            "in_0":[[31,2,1,0, 1, 3, 192, 8] ],
	}
	res = ap.execute_testing(
		name = name, 
		out_features = out_features,
        input_data = input_data)
	# )
	print(res)
