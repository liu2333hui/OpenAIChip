from power_models.AdderNPrimitive import  AdderNPrimitive



def train_adder():
	ap = AdderNPrimitive()

	#Training Mode
	train_sets = ["generated/AdderN/tsmc40_RCA2.txt"]
	train = 1
	if train:
		ap.execute_train(name = "AdderN", 
	 		hardware_features = ['prec_in', 'prec_sum', 'terms'],
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
		name = "AdderN",
		out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
		input_data = {
			"CLOCK": [1],
			"cap_load": [0.10],
			"prec_in" : [8],
			"prec_sum": [16],
			"terms": [2],
			"in_0":[r* [0,0, 22] ],
			"in_1":[r* [0,32, 0] ],
			"in_2":[r* [0, 1, 127] ],
			"in_3":[r* [0,32, 99] ],
		}
	)
	print(res)

if __name__ == "__main__":
	train_adder()


