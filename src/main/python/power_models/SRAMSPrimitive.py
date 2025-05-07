from power_models.GeneralModel import GeneralPrimitiveModel
#from GeneralModel import GeneralPrimitiveModel


import pandas as pd

#todos, fixing the primitive
class SRAMSPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		# return row['in_0']#",".join()
		# pass
    
        #none!
		def fn(row):
			return row['in_0']
		# 	res = []
		# 	#print(row)
		# 	#print(row['in_0'])
		# 	for i in range(len(str(row['in_0']).split(","))):

		# 		s = 1
		# 		# print(str(row[f'in_0']).split(","))

		# 		for j in range(2):
		# 			v = str(row['in_'+str(j)]).split(",")[i]
		# 			#print(i, j, v,  row['in_'+str(j)])
		# 			s *= int(float(v))
		# 		res.append(s)
		# 	return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)
				
#if __name__ == "__main__":
def SRAMSPrimitiveTest( out_features = ['Total_Pwr','Unit_Cycles', 'Energy'], train = 0):
	ap = SRAMSPrimitive()

	df2 = pd.read_csv('generated/SRAMBanked/tsmc40_dataset_write.txt', delimiter='\t')
	df1 = pd.read_csv('generated/SRAMBanked/tsmc40_dataset_read.txt', delimiter='\t')
	# 为文件1添加 mode 列，值为 0
	df1['mode'] = 0 #read
	# 为文件2添加 mode 列，值为 1
	df2['mode'] = 1 #write
	df = pd.concat([df1,df2])
	df['in_0'] = df['write_data']
	df.to_csv('generated/SRAMBanked/tsmc40_dataset_combined.txt',sep="\t", index=False)

	#Training Mode
	train_sets = [
            "generated/SRAMBanked/tsmc40_dataset_combined.txt"    
	]

	name = "SRAMS"
	if train:
        #     	features = ['prec1','radix', 'inv_CLOCK', 'cap_load',] + \
        # ['bits_0', 'bits_1', 'in_0', 'in_1']
        # #'in_0', 'in_1', 'bits_0', 'bits_1', 'toggle', 'prec1']
        # out = 'Unit_Cycles'#'Total_Pwr'
		return ap.execute_train(name = name, 
	 		hardware_features = ['entry_bits', 'rows', 'mode'],
	 		# data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
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
	    'entry_bits': [16],
        	    'rows': [256],
        	    "mode": [1],
       	    "in_0":[[23,123,23,3,5,23] ],
	}
	res = ap.execute_testing(
		name = name, 
		out_features = out_features,
        input_data = input_data)
	# )
	print(res)
