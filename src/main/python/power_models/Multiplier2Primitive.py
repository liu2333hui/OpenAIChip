from power_models.GeneralModel import GeneralPrimitiveModel
import glob
#from GeneralModel import GeneralPrimitiveModel
from toggle import gen_in


#todos, fixing the primitive
class Multiplier2Primitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			res = []
			#print(row)
			#print(row['in_0'])
			for i in range(len(str(row['in_0']).split(","))):

				s = 1
				# print(str(row[f'in_0']).split(","))

				for j in range(2):
					v = str(row['in_'+str(j)]).split(",")[i]
					#print(i, j, v,  row['in_'+str(j)])
					s *= int(float(v))
				res.append(s)
			return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)
				
#if __name__ == "__main__":
def Multiplier2PrimitiveTest( out_features = ['Total_Pwr','Unit_Cycles', 'Energy'], train = 0):
	ap = Multiplier2Primitive()

	#Training Mode
	train_sets = []
	train_sets =train_sets + glob.glob("generated/Multiplier2/17449*")	
	train_sets = train_sets + glob.glob("generated/Multiplier2/1739*")
	train_sets =train_sets + glob.glob("generated/Multiplier2/1744*")
	train_sets =train_sets + glob.glob("generated/Multiplier2/1742*")
	train_sets =train_sets + glob.glob("generated/Multiplier2/1740*")
	
	
	
	train_sets = train_sets + [
        # "generated/MultiplexerN/tsmc40_2.txt",
		"generated/Multiplier2/tsmc40_dataset.txt",

		# "generated/MultiplexerN/tsmc40_test.txt",
		#"generated/Multiplier2/tsmc40_condensed.txt",

		"generated/Multiplier2/tsmc40_dataset_bitserial.txt",
		
		]

	name = "Multiplier2"
	if train:
        #     	features = ['prec1','radix', 'inv_CLOCK', 'cap_load',] + \
        # ['bits_0', 'bits_1', 'in_0', 'in_1']
        # #'in_0', 'in_1', 'bits_0', 'bits_1', 'toggle', 'prec1']
        # out = 'Unit_Cycles'#'Total_Pwr'
		return ap.execute_train(name = name, 

	 		# hardware_features = ['prec1','prec2', 'radix'],

	 		hardware_features = ['prec1', 'radix', 
		'multiplierType', 'side','adderType'],

	 		# data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		#data_features = ["toggles_in_0","sum_toggles_in", 'toggles_out_0','toggles_in_1'],	
	 		data_features = ["bits_in_0", "bits_in_1", "toggles_in_0", "toggles_in_1", "toggles_out_0"],#'toggles_out_0'],	
	 		#data_features = ["bits_in_0", "bits_in_1", "toggles_in_0", "toggles_in_1", "toggles_out_0"],#'toggles_out_0'],	
	
	 		
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
			"cap_load": [0.5],

			"prec1": [8],
            "prec2": [8],
            "radix": [128], 

		#	"in_0":[[127,0,0,0,0], ],
		#	"in_1":[[127,0,0,0,0], ],   
		"in_0": [ gen_in(sparsity=0.1, bit_zero=0, prec=8, N = 1000) ],
		"in_1": [ gen_in(sparsity=0.1, bit_zero=0, prec=8, N = 1000) ],


		'terms': [2],

		'multiplierType': ['HighRadixMultiplier'],
		'side': ['A'],
		'adderType': ['SimpleAdder2'],

		}
	res = ap.execute_testing(
		name = name, 
		out_features =out_features,
		 # ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
		input_data = input_data
	)
	print(res, res["Total_Pwr"]['res'][-1][-1]*1.1)
