from GeneralModel import GeneralPrimitiveModel

#todos, fixing the primitive
class Adder2Primitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			res = []
			for i in range(len(str(row['in_0']).split(","))):
				s = 0
				for j in range(2):
					v = str(row[f'in_{j}']).split(",")[i]
					s += int(float(v))
				res.append(s)
			return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)
				
if __name__ == "__main__":
	ap = Adder2Primitive()

	#Training Mode
	ap.execute_train(name = "Adder2", 
	 		hardware_features = ['prec_in', 'prec_sum'],
	 		data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1'],
	 		train_sets = ["generated/AdderN/tsmc40_RCA2.txt"],
	 		out_features = ['Total_Pwr'],
	 		in_scaling = [1e5],
	 		out_scaling = [1e10],
	 		test_size = 0.1,
	 		delimiter='\t'
	 	)

		
	#Evaluation Mode
	res = ap.execute_testing(
		name = "Adder2",
		out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
		input_data = {
			"CLOCK": [1],
			"cap_load": [0.10],
			"prec_in" : [16],
			"prec_sum": [16],
			"in_0":[ [0,9,13, 88, 123] ],
			"in_1":[ [0,7,133, 77, 1239] ],
		}
	)
	print(res)
