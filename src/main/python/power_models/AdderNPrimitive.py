#from GeneralModel import GeneralPrimitiveModel
import glob
from power_models.GeneralModel import  GeneralPrimitiveModel
#from power_models.GeneralModel import GeneralPrimitiveModel
# from power_models.GeneralModel import GeneralPrimitiveModel
import numpy as np

#todos, fixing the primitive
class AdderNPrimitive(GeneralPrimitiveModel):	
	def define_out(self, df):
		def fn(row):
			res = []
			# print(row['in_0'])
			for i in range(len(str(row['in_0']).split(","))):
				s = 0
				# print(str(row[f'in_0']).split(","))
				for j in range(int(row['terms'])):
					v = str(row[f'in_{j}']).split(",")[i]
					# print(v)
					s += int(float(v))
				res.append(s)
			return ','.join([str(r) for r in res])

		df['out_0'] = df.apply(
			fn
		, axis = 1)
				
#if __name__ == "__main__":
def AdderNPrimitiveTest(train = 1, out_features = 'Total_Pwr'):

	ap = AdderNPrimitive()

	name = "AdderN"

	'''
	toggle_per_bin, average = ap.execute_get_lut(name, 
			out_features= 'Total_Pwr',
			constant_features = {
				"CLOCK": 1,
				"cap_load": 0.10,
				"prec_in" : 16,
				"prec_sum": 16,
				"terms": 2,
			},
				variable_features = {
					"toggles_out_0": np.arange(16),
					"sum_toggles_in": np.arange(16)
				}
			)
	'''
	# print(toggle_per_bin)
	# print(average)
	#print(toggle_per_bin)
	#print(average)
	#Training Mode
	train_sets = glob.glob("generated/AdderN/1744*")
	train_sets =train_sets+ [
		"generated/AdderN/tsmc40_RCA2.txt",
	"generated/AdderN/tsmc40_RCA8.txt",
	"generated/AdderN/tsmc40_RCA16.txt",
	]
	#train = 1
	if train:
		return ap.execute_train(name = "AdderN", 
	 		hardware_features = ['prec_in', 'prec_sum', 'terms'],
	 		# data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2','toggles_in_3'],
	 		data_features = ['sum_toggles_in', 'toggles_out_0',"bits_out_0"],	
	 		
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
			"cap_load": [1.0],
			"prec_in" : [8],
			"prec_sum": [16],
			"terms": [2],
			"in_0":[r* [0,0, 22] ],
			"in_1":[r* [0,32, 123] ],
			"in_2":[r* [0, 1, 127] ],
			"in_3":[r* [0,32, 99] ],
		}
	)
	print(res)
