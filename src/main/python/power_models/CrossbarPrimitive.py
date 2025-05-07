from power_models.GeneralModel import GeneralPrimitiveModel

#todos, fixing the primitive
class CrossbarPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			res = []
			for i in range(len(str(row['in_0']).split(","))):
				# for j in range(int(row['terms'])):
				j = int(row[f'in_0'].split(",")[i])+1
				v = str(row[f'in_{j}']).split(",")[i]
				s = int(float(v))
				res.append(s)
			return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)

def MuxNPrimitiveTest(train = False)	:
	ap = CrossbarPrimitive()

	#Training Mode
	train_sets = ["generated/MuxN/tsmc40_2.txt",
		"generated/MuxN/tsmc40_dataset_full.txt",
		# "generated/MultiplexerN/tsmc40_test.txt",
		
		]
	train = train
	name = "MuxN"
	if train:
		ap.execute_train(name = name, 
	 		hardware_features = ['prec', 'terms'],
	 		# data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		# data_features = ["toggles_in_0","sum_toggles_in", 'toggles_out_0','toggles_in_1'],	
	 		data_features = ["toggles_in_0","sum_toggles_in", 'toggles_out_0'],	
	 		
			train_sets = train_sets,#["generated/AdderN/tsmc40_RCA2.txt"],
	 		out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
	 		in_scaling = [1e5],
	 		out_scaling = [1e10],
	 		test_size = 0.1,
	 		delimiter='\t'
	 	)
	
	repeat = 10
	r = repeat
	input_data = {
			"CLOCK": [1],
			"cap_load": [0.10],
			"prec": [16],
			"terms": [8],
			"in_0":[r* [0,3, 5] ],
			"in_1":[r* [0,32, 0] ],
			"in_2":[r* [0, 1, 127] ],
			"in_3":[r* [0,32, 99] ],
 			"in_4":[r* [0,32, 0] ],
			"in_5":[r* [0, 1, 127] ],
			"in_6":[r* [0,32, 99] ],           
			"in_7":[r* [0,32, 99] ],           
			"in_8":[r* [0,32, 99] ],           
		}
	input_data = {
			"CLOCK": [1],
			"cap_load": [0.10],
			"prec": [16],
			"terms": [8],
			"in_0":[r* [0,3, 5] ],
			"in_1":[r* [0,32, 0] ],
			"in_2":[r* [0, 1, 127] ],
			"in_3":[r* [0,32, 99] ],
 			"in_4":[r* [0,32, 0] ],
			"in_5":[r* [0, 1, 127] ],
			"in_6":[r* [0,32, 0] ],           
			"in_7":[r* [0,32, 0] ],           
			"in_8":[r* [0,32, 0] ],           
		}


	res = ap.execute_testing(
		name = name, 
		out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
		input_data = input_data
	)
	print(res)
if __name__ == "__main__":
	MuxNPrimitiveTest()	
