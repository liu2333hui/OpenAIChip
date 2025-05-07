from power_models.GeneralModel import GeneralPrimitiveModel
#from GeneralModel import GeneralPrimitiveModel



#todos, fixing the primitive
class ConstantMultiplierPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			res = []
			# print(row['in_0'])
			for i in range(len(str(row['in_0']).split(","))):
				s = 1
				# print(str(row[f'in_0']).split(","))
				for j in range(1):
					v = str(row[f'in_{j}']).split(",")[i]
					# print(v)
					s *= int(float(v))
				s *= int(row[f'constant'])
				res.append(s)
			return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)
				
if __name__ == "__main__":
	ap = ConstantMultiplierPrimitive()

	#Training Mode
	train_sets = [
        # "generated/MultiplexerN/tsmc40_2.txt",
		#"generated/Multiplier2/tsmc40_dataset.txt",
		# "generated/MultiplexerN/tsmc40_test.txt",	
		]

	from pathlib import Path

	# 指定目录路径
	directory = Path('generated/ConstantMultiplier')
	
	train_sets = list(directory.rglob('1742*.txt'))
	#print(len(train_sets))
	#train_sets =train_sets[0:69]

	
	train = 0
	name = "ConstantMultiplier"
	if train:
        #     	features = ['prec1','radix', 'inv_CLOCK', 'cap_load',] + \
        # ['bits_0', 'bits_1', 'in_0', 'in_1']
        # #'in_0', 'in_1', 'bits_0', 'bits_1', 'toggle', 'prec1']
        # out = 'Unit_Cycles'#'Total_Pwr'
		ap.execute_train(name = name, 
	 		hardware_features = ['prec1', 'constant'],
	 		# data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		# data_features = ["toggles_in_0","sum_toggles_in", 'toggles_out_0','toggles_in_1'],	
	 		data_features = ["toggles_in_0", "bits_constant", 'toggles_out_0'],	
	 		
			train_sets = train_sets,#["generated/AdderN/tsmc40_RCA2.txt"],
	 		out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
	 		in_scaling = [1e5],
	 		out_scaling = [1e10],
	 		test_size = 0.1,
	 		delimiter='\t'
	 	)
	
	repeat = 10
	r = repeat
	res = ap.execute_testing(
		name = name, 
		out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
		input_data = {
			"CLOCK": [1],
			"cap_load": [0.1],
			"prec1": [8],
			"constant": [23],
			"in_0":[[31],[3], [5] ],
		}
	)
	print(res)
