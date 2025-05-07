from power_models.GeneralModel import GeneralPrimitiveModel
#from GeneralModel import GeneralPrimitiveModel



#todos, fixing the primitive
class MuxNPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			res = []
			for i in range(len(str(row['in_0']).split(","))):
				# for j in range(int(row['terms'])):
				j = int(row[f'in_0'].split(",")[i])+1
				#print(j, i, len(row[f'in_{j}'].split(",")))
				v = str(row[f'in_{j}']).split(",")[i]# % len(str(row[f'in_{j}']).split(","))]
				s = int(float(v))
				res.append(s)
			return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)

def MuxNPrimitiveTest(train = False, out_features = ["Total_Pwr"]):
	ap = MuxNPrimitive()

	#Training Mode
	import glob
	txt_files = glob.glob("generated/MuxN/1744*.txt")
	
	txt_files = txt_files + glob.glob("generated/MuxN/17437*.txt")
	train_sets = txt_files + [\
		"generated/MuxN/tsmc40_2.txt",
		"generated/MuxN/tsmc40_dataset_full.txt",

		# "generated/MultiplexerN/tsmc40_test.txt",
		# "generated/MultiplexerN/tsmc40_512.txt",
		# "generated/MultiplexerN/tsmc40_4.txt",
		]
	train = train
	name = "MuxN"
	if train:
		return ap.execute_train(name = name, 
	 		hardware_features = ['prec', 'terms'],
	 		# data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		 data_features = ["bits_in_0", "bits_out_0", "toggles_in_0","sum_toggles_in",'toggles_out_0'],	
	 		#data_features = ["bits_in_0",,"sum_toggles_in", 'toggles_out_0'] ,
	 		#data_features = ['toggles_out_0'] ,
	
			#data_features = [f"toggles_in_{i}" for i in range(512)] + [f"bits_in_{i}" for i in range(512)] + ["toggles_out_0"],

	 		
			train_sets = train_sets,#["generated/AdderN/tsmc40_RCA2.txt"],
	 		out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
	 		in_scaling = [1e6],
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
			"cap_load": [1.0],
			"prec": [8],
			"terms": [4],
			"in_0":[r* [0,0, 0] ],
			"in_1":[r* [0,32, 129] ],
			"in_2":[r* [0, 1239, 127] ],
			"in_3":[r* [0,391, 99] ],
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



#case study of a two-level model
#assume the mux model is already good
#then we can build two-level models using it
#then train another model

def MuxN2CrossbarTraining():
	ap = MuxNPrimitive()
	name = "MuxN"

	repeat = 3
	r = repeat
	prec = 8

	#outputs
	#terms
	for M in [512, 256, 128, 64, 32][::-1]:	
		for P in [1,2,4,8,16,32, 64, 128, 256][::-1]:
			if(P >= M):
				continue
			for in0 in range(0, prec):
				for in1 in range(0, prec):
					#for p in range(P) :
					input_data = {	
						"CLOCK": [1],
						"cap_load": [0.1],
						"prec": [prec],
						"terms": [M],
						"in_0": [ r*[0, 1]  for p in range(P)    ],
						}
					
					for m in range( M):
						if (m % 2 == 0):
							input_data["in_"+str(m+1)] =[r*[0, (1<<in0)-1]]	
						else:
							input_data["in_"+str(m+1)] =[r*[0, (1<<in1)-1]]
						
					res = ap.execute_testing(
						name = name, 
						out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
							input_data = input_data
							)
					#print(input_data)
					
					#save it in the dataset
					print(len(res['Total_Pwr']['res']))
					print(sum([s[1]  for s in res['Total_Pwr']['res']]))
					sum_pwr = sum([s[1]  for s in res['Total_Pwr']['res']])
						
	
	
					exit()			
	


if __name__ == "__main__":
	MuxNPrimitiveTest()	
	#MuxN2CrossbarTraining()
	
