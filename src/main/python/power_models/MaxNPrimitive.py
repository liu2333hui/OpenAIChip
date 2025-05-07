from power_models.GeneralModel import GeneralPrimitiveModel

#todos, fixing the primitive
class MaxNPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			res = []
			for i in range(len(str(row['in_0']).split(","))):
				s = 0
				for j in range(int(row['terms'])):
					v = str(row[f'in_{j}']).split(",")[i]
					if(int(v) > s):
						s = int(float(v))
				res.append(s)
			return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)
				
#if __name__ == "__main__":
def MaxNPrimitiveTest(train = 1,out_features = ["Total_Pwr"]):
	ap = MaxNPrimitive()

	#Training Mode
	train_sets = ["generated/MaxN/tsmc40_dataset.txt"]
	train = train
	name = "MaxN"
	if train:
		return ap.execute_train(name = name, 
	 		hardware_features = ['prec', 'terms'],
	 		# data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		data_features = ['sum_toggles_in', 'toggles_out_0'],	
	 		
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
			"cap_load": [0.10],
			"prec": [16],
			"terms": [2],
			"in_0":[r* [0,0, 22] ],
			"in_1":[r* [0,32, 0] ],
			"in_2":[r* [0, 1, 127] ],
			"in_3":[r* [0,32, 99] ],
		}
	)
	print(res)
