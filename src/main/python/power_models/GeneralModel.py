import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import LinearSVR, SVR
from sklearn.neural_network import MLPRegressor
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn.utils.validation")
import os
import pickle
import itertools 

import copy

def calculate_sum_toggle(row):
	toggles = []
	#print(row)
	for i in range(row['terms']):
		in_0_str = row['in_'+str(i)]	
		toggles.append(calculate_toggle(in_0_str))
	toggles = sum(toggles)#/len(toggles) 

	return toggles#sum(row[f'toggles_in_{i}'] for i in range(row['terms']))	
	

def calculate_zeros(in_0_str):
	bits = list(map(int, in_0_str.split(',')))
	return bits.count(0)/len(bits)


def calculate_toggle(in_0_str):
	#print(in_0_str)
	# 分割字符串并转换为整数
	in_0_str = str(in_0_str)
	bits = list(map(int, in_0_str.split(',')))
	if(len(bits) == 1):
		return 0
	else:
		arr = bits
		toggle = []
		prev = arr[0]
		for i in arr[1:]:
			toggle.append(bin(prev ^ i).count('1'))
			prev = i
		toggle.append(bin(arr[-1] ^ arr[0]).count('1'))

		# print(toggle)
		return sum(toggle)/len(toggle) 
		# prev = bits[0]
		# toggle = 0
		# for i in range(len(bits[1:])):
			
		# 计算异或值（XOR）
		# xor_result = bits[0] ^ bits[1]
		# print(bin(xor_result), bin(xor_result).count('1'))
		# 统计二进制中 1 的个数
		# return bin(xor_result).count('1')
def calculate_bits(in_0_str):
	# 分割字符串并转换为整数
	#print(in_0_str)
	in_0_str = str(in_0_str)
	bits = list(map(int, in_0_str.split(',')))
	if(len(bits) == 1):
		in_0_str = str(in_0_str).split(",")[0]
		return bin(int(in_0_str)).count("1")
	else:
		arr = bits
		bits = []
		for i in arr:
			bits.append(bin(int(i)).count("1"))
		bits.append(bin(arr[-1] ^ arr[0]).count('1'))

		# print(toggle)
		return sum(bits)/len(bits) 
	
	#in_0_str = str(in_0_str).split(",")[0]
	#return bin(int(in_0_str)).count("1")

'''
def calculate_sum_zeros(row):
	for j in range(int(row['terms'])):
		arr =  
		toggle = []
		prev = arr[0]
		for i in arr:
			toggle.append(bin(prev ^ i).count('1'))
			prev = i
		zeros.append(bin(arr[-1] ^ arr[0]).count('1'))
	return sum(zeros)		


'''
def calculate_seq_len(in_0_str):
	bits = list(map(int, str(in_0_str).split(',')))
	return len(bits)

def log1p_inverse(x):
	return np.exp(x) - 1
		
def ones_count(x):
	"""计算数字 x 的二进制表示中 1 的个数"""
	return bin(x).count('1')
def is_float_or_int_column(column):
    return pd.api.types.is_float_dtype(column) or pd.api.types.is_integer_dtype(column)
		
#General power model
#1. training
# 1.0 Input features
#	generic (cap_load, clock)
#	hardware (specific for the hardware such as radix, precisions)
#	toggles (toggle information specific to the hardware)
#		in_*, the direct input
#		toggles_in_*, the input toggle
#		bits_in_*, the input bits
#		out_*, the direct output
#		toggles_out_*, the output toggle
#		bits_out_*, the output bits

#2. inference stage
# 2.0. 
# 2.1. Direct inference, input features --> power / energy / timing / area etc.
	
#(todos) consider other in_features such as
#	TechNode, etc.

class GeneralPrimitiveModel:
	
	def get_features(self, name, out_features = ['Total_Pwr']):
		self.load(name,out_features )
		
		g = self.all_models[out_features[0]]['generic_features']	
		h = self.all_models[out_features[0]]['hardware_features']	
		d = self.all_models[out_features[0]]['data_features']	
		return g, h, d



	#for testing purposes
	def load(self, name, 
		out_features = ['Total_Pwr', 'Unit_Cycles', 'Energy']):
	
		all_models = {}
		
		for out in out_features:
			trained_model = {}
			pkl_file = self.get_pkl_name(out, name)
			
			#print("loading ", pkl_file)
			with open(pkl_file,"rb") as f:
				model = pickle.load(f)
			
			trained_model['ai_model'] = model['ai_model']
			trained_model['features'] = model['features'] 
			trained_model['data_features'] = model['data_features'] 
			trained_model['generic_features'] = model['generic_features'] 
			trained_model['hardware_features'] = model['hardware_features'] 
	
			trained_model['encoded_categories'] = model['encoded_categories'] 
			#print(trained_model['encoded_categories'])
	
			trained_model['in_scaling'] = model['in_scaling']
			trained_model['out_scaling'] = model['out_scaling']
		
			all_models[out] = trained_model
		
		self.all_models = all_models
	


	def execute_train(self, name, 
			hardware_features = ['prec_in', 'prec_sum', 'terms'],
			data_features = ['toggles_out_0', 'toggles_in_0', 'toggles_in_1', 'toggles_in_2',
					'toggles_in_3'],
			train_sets = ["generated/AdderN/tsmc40_RCA2.txt"],
			out_features = ['Total_Pwr','Unit_Cycles', 'Energy'],
			in_scaling = [1e5],
			out_scaling = [1e10],
			test_size = 0.1,
			delimiter='\t',
			rename_table = {
			}
		):
		#Training Mode
		self.create(name, hardware_features, data_features)
		return self.train(train_sets, delimiter ,
			out_features, 
			in_scaling,
			out_scaling,
			test_size,
			rename_table = rename_table)

	#mean cost
	#def execute_b2():


	#multi-stsage cost, 2-stage
	
	def execute_testing(self, name, 
			out_features= ['Total_Pwr'],
			input_data = {
				"CLOCK": [1],
				"cap_load": [0.10],
				"prec_in" : [4],
				"prec_sum": [4],
				"terms": [2],
				"in_0": [0,9,13],
				"in_1": [0,7,133],
				"in_2": [0,6,29],
				"in_3": [0,6,99],
			}

			):
		self.load(name, out_features )
		res_payload = {}

		#fix terms to 
		#print(input_data.keys())
		new_terms = 2**int(np.ceil(np.log2(input_data.get('terms', [1])[0])))
		for i in range(int(input_data.get('terms',[1])[0]), new_terms):
			input_data[f'in_{i}'] = np.zeros(np.array(input_data['in_0']).shape,dtype='int32').tolist()
		input_data['terms'] =[ new_terms]
		#print(input_data.keys())

		for out in out_features:
			#if("Multiplier" in name):	
			#	res = self.infer_old(input_data, out)			
			#else:
			res = self.inferv2(input_data, out)
			res_payload[out] = {"res":res}#, "res_avg": res_avg, "res_sum": sum(res)}
		return res_payload
	

	def execute_get_lut(self, name, 
			out_features= 'Total_Pwr',
			constant_features = {
				"CLOCK": 1,
				"cap_load": 0.10,
				"prec_in" : 4,
				"prec_sum": 4,
				"terms": 2,
			},
			variable_features = {
				"in_0": 2,#[0,1,2],
				"in_1": 2,#[0,1,2]
			},need_zero=True,
			N = 10
			):
		self.load(name, [out_features] )
		# print(self.all_models['Total_Pwr'])
		primitive_model = self.all_models[out_features]

		for k in variable_features: 
			variable_features[k] = [(i<<1)  - 1 for i in range(1,1+variable_features[k])]

		input_sequences = list(variable_features.values())
		combinations = list(itertools.product(*input_sequences))
		combinations_array = np.array(combinations) 

		combos = np.array(combinations_array)
		combos = combos.T

		combos = combos.tolist()


		for k in range(len(variable_features), constant_features['terms'][0]):
			combos.append( combos[k % len(variable_features)])#[(i<<1)  - 1 for i in range(1,1+variable_features[k])]

		#print(constant_features)
		#print(combos)
		#exit()


		

		ins ={}
		for k in constant_features:
			ins[k] = constant_features[k]

		
		#print(variable_features)	
		#input()
		for idx,k in enumerate(variable_features):
			if(need_zero):
				ins[k] = [[0, i]*N for i in combos[idx]]
			else:
				ins[k] = [[ i]*N for i in combos[idx]]
	
		for k in range(len(variable_features), constant_features['terms'][0]):
			ins["in_"+str(k)] = ins[ "in_"+  str (k % len(variable_features))]#[(i<<1)  - 1 for i in range(1,1+variable_features[k])]


		#print(ins)

		#input()	
		res = self.execute_testing(
			name = name,
			out_features =['Total_Pwr'],	
			input_data = ins
		)


		return res	

		#for c in constant_features:
		#	row = [constant_features[c][0]]*combos.shape[1]
		#	#print(row)
		#	#print(np.array(row).shape)
		#	#print(np.array(row).reshape((-1)))
		#	input_data = np.vstack((input_data, row))
		# print(input_data.shape)
		
		

		#columns = []
		#for v in variable_features:
		#		columns.append(v)
		#for c in constant_features:
		#		columns.append(c)

		# print(primitive_model['features'])
		# print(column/s)
		#df = pd.DataFrame(input_data.T, columns=columns)

		# print(df)
		
		
		# df = pd.DataFrame(input_data)


		#df['inv_CLOCK'] = 1 / df['CLOCK'].replace(0, np.nan)
		#return self.infer_df (df, out_features)

	def infer_df(self, df, out):
		primitive_model = self.all_models[out]
		mult_data = df[primitive_model['features']]
		#print("mult_data", mult_data)
		mult_data = np.array(mult_data, dtype='float32')
		#print(mult_data*primitive_model['in_scaling'])
		mult_X = np.log1p(mult_data*primitive_model["in_scaling"])
		mult_X = pd.DataFrame(mult_X, columns=primitive_model['features'])
		mult_Y = log1p_inverse(primitive_model["ai_model"].predict(mult_X))/primitive_model["out_scaling"]
		res = mult_Y
		# print(mult_Y)
		return res, np.sum(res)/len(res)

	#(todos) infer a batch of input_data, in form of a map
	#input_data = {
	#	
	#}

	def direct_infer(self, input_data, out='Total_Pwr'):
		df = pd.DataFrame(input_data)
	

		input_data['inv_CLOCK'] = 1 / np.array(input_data['CLOCK'])
	

	#input_data
	#{
	#	"in_0": [[1,2,3,], [3,4,5]...[]]
	#}

	#processed_input

	def inferv2(self, input_data, out = 'Total_Pwr'):
		primitive_model = self.all_models[out]
		for k,v in input_data.items():
			if("in_" in k):
				#print(input_data[k])
				input_data[k] = [",".join([str(d) for d in data]) for data in input_data[k]]
		batch = max([len(input_data[k]) for k in input_data])
		#data = np.zeros( (batch, len(primitive_model['features'])) )
		for k,v in input_data.items():
			if(len(v) < batch):
				input_data[k] = v * (batch//len(v))
		df = pd.DataFrame(input_data)
		df['inv_CLOCK'] = 1 / df['CLOCK'].replace(0, np.nan)
		#print(out, 'infer!! ', df)
		self.define_out(df)
		#print(out , 'out!!',df)

		#[1,2,3] --> [1,2], [2,3], [3,4]
		terms = df.iloc[0]['terms']
		nn = ["in_"+str(n) for n in range(terms)]
		hardware_only = df[df.columns.difference(nn)].iloc[0]
		
		results = []

		packed_df = df
		#print(packed_df)
		#go through all "toggle", "bits" features
		for f_idx, f in enumerate(primitive_model['features']):
			if(f in input_data):
				continue
			else:
				sel = "_".join(f.split("_")[1:])
				if("sum_toggles_in" in f):
					#print(df)
					packed_df[f] = packed_df.apply(calculate_sum_toggle, axis=1)
				elif("inv_" in f):
					packed_df[f] = 1/packed_df[sel]
				elif("toggles_" in f):
					packed_df[f] = packed_df[sel].apply(calculate_toggle)
				elif("bits_" in f):
					packed_df[f] = packed_df[sel].apply(calculate_bits)
				elif("encoded_" in f):
						
					#pass
					#df["encoded_" + data_f], unique_categories = pd.factorize(df[data_f])
					#category_mapping = {category: code for code, category in enumerate(unique_categories)}
					#encoded_categories[data_f] = category_mapping
					trained_model = primitive_model
					def encode_map(el):
						#print(trained_model['encoded_categories'])
						if(el == 'weight' or el == 'weights'):
							el = 'A'
						elif(el == 'input' or el == 'acts'):
							el = 'B'
						elif(el == 'both' or el == 'both'):
							el = 'dual'
			

						if(el == 'RCAAdder2' and el not in trained_model['encoded_categories'][sel]):
							el = 'SimpleAdder2'

						if(el == 'BitSerial' and el not in trained_model['encoded_categories'][sel]):
							el = 'BitSerialMultiplier'
	
						
						if(el == 128 and el not in trained_model['encoded_categories'][sel]):
							el = 64
	
	
						#print("ENCODED", trained_model['encoded_categories'])	
						#print(sel, el)
						#	exit()
						return trained_model['encoded_categories'][sel][el]
					packed_df[f] = packed_df[sel].apply(    encode_map  )
	

				else:
					print("[ERROR] feature not found represented!", f)					
		#print(packed_df)

		#input("OK?")
		
		res, res_avg = self.infer_df (packed_df, out)
		results.append((res, res_avg))
		return results
	
	
	def infer_old(self, input_data, out = 'Total_Pwr'):
		primitive_model = self.all_models[out]
		for k,v in input_data.items():
			if("in_" in k):
				input_data[k] = [",".join([str(d) for d in data]) for data in input_data[k]]
		#print(input_data)
		batch = max([len(input_data[k]) for k in input_data])
		#data = np.zeros( (batch, len(primitive_model['features'])) )
		for k,v in input_data.items():
			if(len(v) < batch):
				input_data[k] = v * (batch//len(v))
		df = pd.DataFrame(input_data)
		df['inv_CLOCK'] = 1 / df['CLOCK'].replace(0, np.nan)
		#print(out, 'infer!! ', df)
		self.define_out(df)
		#print(out , 'out!!',df)

		#[1,2,3] --> [1,2], [2,3], [3,4]
		terms = df.iloc[0]['terms']
		nn = ["in_"+str(n) for n in range(terms)]
		hardware_only = df[df.columns.difference(nn)].iloc[0]
		
		results = []

		for index, row in df.iterrows(): 		
			packed_df = pd.DataFrame(columns=df.columns)
			in_data = [ row['in_'+str(k)].split(",") for k in range(terms)]
			o_data = row['out_0'].split(",")	
			for i in range(len(row['in_0'].split(","))-1):
				for n in range(row['terms']): 	
					inn = 'in_' + str(n)
				
					#print(inn, in_data[n][i]+ "," + in_data[n][i+1])

					hardware_only[inn] =  in_data[n][i]+ "," + in_data[n][i+1] #str(row[inn][i]) + "," + str(row[inn][i+1])
				onn = 'out_0'
				hardware_only[onn] =  str(o_data[i]) + "," + str(o_data[i+1])
		
				
				new_row = hardware_only
				packed_df.loc[len(packed_df)] = new_row

			#print(packed_df.columns)
			#print(packed_df)
	
			#exit(0)

			#go through all "toggle", "bits" features
			for f_idx, f in enumerate(primitive_model['features']):
				if(f in input_data):
					continue
				else:
					sel = "_".join(f.split("_")[1:])
					if("sum_toggles_in" in f):
						#print(df)
						packed_df[f] = packed_df.apply(calculate_sum_toggle, axis=1)
					elif("inv_" in f):
						packed_df[f] = 1/packed_df[sel]
					elif("toggles_" in f):
						packed_df[f] = packed_df[sel].apply(calculate_toggle)
					elif("bits_" in f):
						packed_df[f] = packed_df[sel].apply(calculate_bits)
					elif("encoded_" in f):
						
						#pass
						#df["encoded_" + data_f], unique_categories = pd.factorize(df[data_f])
						#category_mapping = {category: code for code, category in enumerate(unique_categories)}
						#encoded_categories[data_f] = category_mapping
						trained_model = primitive_model
						def encode_map(el):
							#print(trained_model['encoded_categories'])
							if(el == 'weight' or el == 'weights'):
								el = 'A'
							elif(el == 'input' or el == 'acts'):
								el = 'B'
							elif(el == 'both' or el == 'both'):
								el = 'dual'
	
							return trained_model['encoded_categories'][sel][el]
						packed_df[f] = packed_df[sel].apply(    encode_map  )
	

					else:
						print("[ERROR] feature not found represented!", f)					

		
			res, res_avg = self.infer_df (packed_df, out)
			results.append((res, res_avg))
		return results
	
	def infer_v1(self, input_data, out = 'Total_Pwr'):
		primitive_model = self.all_models[out]
		

		for k,v in input_data.items():
			if("in_" in k):
				input_data[k] = [",".join([str(d) for d in data]) for data in input_data[k]]
		# print(input_data)

		batch = max([len(input_data[k]) for k in input_data])
		data = np.zeros( (batch, len(primitive_model['features'])) )

		#fix array lengths
		for k,v in input_data.items():
			if(len(v) < batch):
				input_data[k] = v * (batch//len(v))
		df = pd.DataFrame(input_data)
	

		df['inv_CLOCK'] = 1 / df['CLOCK'].replace(0, np.nan)
		#define outputs
		self.define_out(df)
		# df["out_0"] = df.apply(self.define_out,axis=1)

		#print(df)
		# self.secondary_features(df,primitive_model['features'] )

		#go through all "toggle", "bits" features
		for f_idx, f in enumerate(primitive_model['features']):
			if(f in input_data):
				continue
			else:
				sel = "_".join(f.split("_")[1:])
				if("sum_toggles_in" in f):
					#print(df)
					df[f] = df.apply(calculate_sum_toggle, axis=1)
				elif("inv_" in f):
					df[f] = 1/df[sel]
				elif("toggles_" in f):
					df[f] = df[sel].apply(calculate_toggle)
					# # print(sel)
					# seq = df[sel]
					# idx = 0
					# prev_a = seq[0]
					# toggles = []
					# for a in seq[1:]:
					# 	toggles.append(ones_count(int(a) ^ int(prev_a))) 
					# 	prev_a = a
					# 	# data[idx, len(hardware)+0] = ones_count(a)
					# 	idx = idx + 1
					# toggles.append(ones_count(int(prev_a) ^ int(seq[0])))
					# df[f] = toggles
				elif("bits_" in f):
					df[f] = df[sel].apply(calculate_bits)
				#elif('encoded_')
				else:
					print("[ERROR] feature not found represented!", f)					
		#print(df)

		
		return self.infer_df (df, out)
		#infer and return the powers
		# mult_data=mult_data.reshape((-1, len(adderN_features)))
		mult_data = df[primitive_model['features']]
		# print("mult_data", mult_data)
		mult_data = np.array(mult_data)
		mult_X = np.log1p(mult_data*primitive_model["in_scaling"])
		mult_X = pd.DataFrame(mult_X, columns=primitive_model['features'])
		mult_Y = log1p_inverse(primitive_model["ai_model"].predict(mult_X))/primitive_model["out_scaling"]
		res = mult_Y
		# print(mult_Y)
		return res, np.sum(res)/len(res)
		
	#(todos) different inference, we can have full LUTs
	#(todos) can infer a sequence for testing purposes
	
	#for training purposes
	def create(self, name, hardware_features, data_features,
		generic_features = ['inv_CLOCK', 'cap_load'],
		models = {
		 #   "LinearRegression": LinearRegression(),
		    "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
		    "RandomForestRegressor": RandomForestRegressor(random_state=42),
		 #   "GradientBoostingRegressor": GradientBoostingRegressor(random_state=42),
		 #   "LinearSVR": LinearSVR(random_state=42),
		 #   "SVR": SVR(),
		 #   "MLPRegressor": MLPRegressor(random_state=42, max_iter=1000)
		}):
		
		self.name = name
		self.generic_features = generic_features
		self.hardware_features = hardware_features
		self.data_features = data_features
		self.models = models
		
	#please define it, i.e.
	# df['out_0'] = df['in_0'] + df['in_1']
	def define_out(self, df):
		df['out_0'] = df['in_0']
	
	def get_pkl_name(self, out, name):

		if(not os.path.exists('generated/PowerModels/'+out)):
			os.mkdir('generated/PowerModels/'+out)
		return 'generated/PowerModels/'+out+'/'+name+'.pkl'
	



	#(todos) consider other out_features, such as
	# Area, Delay, Leackage_Pwr, Switching_Pwr, Gates etc. 
	def train(self, train_sets, delimiter='\t', 
		out_features = ['Total_Pwr', 'Unit_Cycles', 'Energy'],
		in_scaling = [1e5],
		out_scaling = [1e10],
		test_size = 0.2,
		rename_table = {}
		):
		#read dataset
		dfs = []
		for idx, ts in enumerate(train_sets):
			df_read = pd.read_csv(ts,  delimiter=delimiter)
			df_read['id'] = idx
			#print(df_read)
			#input()
			#print(df_read['out_terms'])
			#adhoc fix
			if('out_terms' in df_read.columns):
				if(not is_float_or_int_column(df_read['out_terms'])):
					continue
			dfs.append(df_read)
		df = pd.concat(dfs)
		#print(df)	
		df.fillna(1, inplace=True)
		#exit()
		
		for rn in rename_table:
			jiu = rn
			xin = rename_table(rn)
			df[xin] = df[jiu]
		
		#prepare secondary output features, i.e. energy, time etc.

		#assume there is at least one value
		df['max_seq_len'] = df['in_0'].apply(calculate_seq_len)

		if('cycles' in df.columns):
			df['Unit_Cycles'] = df['cycles']/10.0/df['N']  /df['max_seq_len']

			df['Energy'] = df['Total_Pwr'] * df['Unit_Cycles'] * df['CLOCK'] * 1e-9
		
		#prepare toggles / bits
		orig_features = self.generic_features + self.hardware_features + self.data_features
		

		features = []
		encoded_categories = {}

		#define secondary input features
		df['inv_CLOCK'] = 1 / df['CLOCK'].replace(0, np.nan)
		#define outputs
		self.define_out(df)
		
		#print(df['out_terms'] = )
		#print(is_float_or_int_column(df['out_terms'].iloc[0]))
		#exit()
		#print("HERE")
		#print(orig_features)
		#df = df.fillna("None")
		#print(is_float_or_int_column(df['terms']))
		#print(df['terms'].apply(print))
		#input()
		for data_f in orig_features:
			# print(data_f)
			sel = "_".join(data_f.split("_")[1:])
			if("sum_toggles_in" == data_f):
				df[data_f] = df.apply(calculate_sum_toggle, axis = 1)	
			elif("sum_bits_in" == data_f):
				df[data_f] = df.apply(calculate_sum_bits, axis = 1)	
			elif("sum_zeros_in" == data_f):
				df[data_f] = df.apply(calculate_sum_zeros, axis = 1)		
			elif("toggles_" in data_f):
				df[data_f] = df[sel].apply(calculate_toggle)
			elif("bits_" in data_f):
				df[data_f] = df[sel].apply(calculate_bits)
			elif(not is_float_or_int_column(df[data_f])):
				df["encoded_" + data_f], unique_categories = pd.factorize(df[data_f])
				category_mapping = {category: code for code, category in enumerate(unique_categories)}
				encoded_categories[data_f] = category_mapping
				# 使用保存的映射关系对新数据进行编码
				# new_df['Category_Encoded'] = new_df['Category'].map(category_mapping)
				# 处理未知类别（例如 Grape）
				# new_df['Category_Encoded'] = new_df['Category_Encoded'].fillna(-1)  # 将未知类别编码为 -1
				
				data_f = "encoded_" + data_f
			#else:
			#df[data_f] = df[data_f]
			features.append(data_f)

		# features, encoded_categories = self.secondary_features(df, orig_features)
		# out = np.array(df[[ 'out_0']])
		# sel = np.array(df[[ 'in_0']])
		# in_1 = np.array(df[[ 'in_1']])
		# in_2 = np.array(df[[ 'in_2']])
		# in_sum = np.array(df[[ 'sum_toggles_in']])
		# terms = np.array(df[['terms']])
		# Power = np.array(df[['Total_Pwr']])
		# print(out)
		# print(sel)
		# print(in_1)
		# print(in_2)
		# print("in_sum")
		# print(in_sum)
		# print("terms")
		# print(terms)
		# df[['out_0']]
		# print('power')
		# print(Power)
		# # print(df[[ 'toggles_in_0',"toggles_in_1",'sum_toggles_in']])
		

	


		# exit()
		#Training model !
		for idx, out in enumerate(out_features):

			#mask out the really small ones, df[out] <= 1e-7
			#valid_mask = (df[out] >= 1e-7)
			#y_train = y_train[valid_mask]
			#X_train = X_train[valid_mask]
			valid_mask = (df[out] > 1e-7)
			df = df[valid_mask]

			y = df[out]*out_scaling[idx % len(out_scaling)]
			X = df[features]*in_scaling[idx % len(in_scaling)]
			X = np.log1p(X)
			y = np.log1p(y)	
				
			X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
			results = {}
				
			trained_models = {}
		
				
		
			#print(X_train, y_train)
			for name, model in self.models.items():
				# 训练模型
				model.fit(X_train, y_train)
				
				# 预测``
				# print(X_test)
				# exit(0)
				y_pred = model.predict(X_test)
				
				# 计算评估指标
				#remove powers less than 1e-7 from calculation
				#otherwise cause huge errors
				# valid_mask = (y_test >= 1e-7)
				# y_test = y_test[valid_mask]
				# y_pred = y_pred[valid_mask]
				# print(y_test)
				# print(y_pred)
				# exit()

				mae = mean_absolute_error(y_test, y_pred)
				mse = mean_squared_error(y_test, y_pred)
				rmse = np.sqrt(mse)
				
				# 计算相对误差
		
					
				relative_error = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
				
				rel_err_inverse = np.mean(np.abs((log1p_inverse(y_test) - log1p_inverse(y_pred)) / log1p_inverse(y_test))) * 100
				# print("data")
				# print(log1p_inverse(y_test))
				# print(log1p_inverse(y_pred))
				# 保存结果
				results[name] = {
					"MAE": mae,
					"MSE": mse,
					"RMSE": rmse,
					"Relative Error (%)": relative_error,
					"rel_err_inverse":rel_err_inverse
				}
				trained_models[name] = model
				# 打印结果
				print(f"Model: {name}")
				print(f"  MAE: {mae}")
				print(f"  MSE: {mse}")
				print(f"  RMSE: {rmse}")
				print(f"  Relative Error (%): {relative_error}")
				print(f"  rel_err_inverse (%): {rel_err_inverse}")
				print("-" * 30)

			# 5. 找到表现最好的模型
			best_model = min(results, key=lambda x: results[x]['RMSE'])
			print(f"\nBest Model: {best_model}")
			print(f"  RMSE: {results[best_model]['RMSE']}")
			print(f"  Relative Error (%): {results[best_model]['Relative Error (%)']}")
			print(f"  rel_err_inverse (%): {results[best_model]['rel_err_inverse']}")
			
			
			saved_bun = {
					'ai_model': trained_models[best_model],
					'features': features,
					'hardware_features': self.hardware_features,
					'generic_features': self.generic_features,
					'data_features':  self.data_features,
	
					'in_scaling': in_scaling,
					'out_scaling': out_scaling,
					"define_out_fn": self.define_out,
					"encoded_categories": encoded_categories
			}
			with open(self.get_pkl_name(out, self.name), 'wb') as f:
				pickle.dump(saved_bun, f)



			#for plotting purposes, save the best model and its accuracy , perhaps we should move it to another set, i.e. cross-validation set, not on the same training set for better , do later, no time now
			#log1p_inverse(primitive_model["ai_model"].predict(mult_X))/primitive_model["out_scaling"]
			####################################################################
			if 1:

				X = df[features]
				y = df[out]*out_scaling[idx % len(out_scaling)]


				X = X*in_scaling[idx % len(in_scaling)]
				X = np.log1p(X)
				y = np.log1p(y)	



				X_train = X
				y_train = y
				X_test = X
				y_test = y

	
				best_model = trained_models[best_model]

				y_test_pred = best_model.predict(X_test)
				y_train_pred = best_model.predict(X_train)
	
				y_test_pred = log1p_inverse(y_test_pred)/out_scaling
				y_train_pred = log1p_inverse(y_train_pred)/out_scaling

				y_train_golden = log1p_inverse(y_train)/out_scaling
				y_test_golden = log1p_inverse(y_test)/out_scaling


				#rel_err_inverse = np.mean(np.abs((log1p_inverse(y_test) - log1p_inverse(y_pred)) / log1p_inverse(y_test))) * 100
				#######################################OUR FINAL METHOD#######################
				#this is only one unit
				import matplotlib.pyplot as plt
				#plt.scatter(np.array(y_train_pred),np.array(y_train_golden))	
				#plt.plot(np.array(y_train_golden),np.array(y_train_golden), 'r-')		
				#plt.scatter(np.array(y_test_pred), np.array(y_test_golden))
				#plt.show()
				golden = np.array(y_train_golden) #np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred = np.array(y_train_pred)#np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])

				golden = np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred = np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])


				#####################################FIXED POWER################################3



				#fixed power take
				#mean_value = np.mean(our_pred)
				#mean_arr = np.full_like(our_pred, mean_value)
				min_value = np.min(our_pred)
				min_arr = np.full_like(our_pred, min_value)
				max_value = np.max(our_pred)
				max_arr = np.full_like(our_pred, max_value)

				mean_value = (max_value+min_value)/2.0
	

				b1 = max_arr
				#average power 
				b2 = (max_arr+min_arr)/2

				#	plt.scatter(np.array(mean_arr),np.array(y_train_golden))	

				simple = [f for f in features ]

				X = df.copy()[simple]
				if("terms" not in df.columns):
					df['terms'] = 1	
					
				for c in X.columns:
					X["max_"+c] = np.mean(df[c])#, axis = 1)
					#print(X[c])
					#print(X["max_"+c])
					#input()

				#print(X.columns)
				#for c in X.columns:
				#if('max' in c):
				#print(X[c])
				#df["max_"+c] = np.max(df[c])


				#input()
				############################################################3
				#accelergy-like, we hack the df so that
				#instead of using the actual toggle, we estimate it based on the zero value
				
				y = df[out]*out_scaling[idx % len(out_scaling)]
				#X = df[simple]*in_scaling[idx % len(in_scaling)]
				#X = df#[simple]
				'''
				for c in df.columns:
					#print(c)
					#print(df[c])
					#print("in" in c)
					#print( "out" in c)
					if("toggle"in c or "bits" in c):
						continue
					if("inv" not in c and ("in" in c[0:2] or "out" in c[0:3])):
						#print(df[c])
						#input()
						def count(row):
							#print(row)
							return 1.0- calculate_zeros(row)				
							#input()
							return 0.0
						
						X['sparse_'+c] = df[c].apply(count)
						#print(X['sparse_'+c])
						#input()
				'''	
				#exit()
				#input("from sparse to toggle")
				for c in X.columns:
					if("max_" in c):
						continue
					if("toggle" in c or "bits" in c):
						#print(c)
						#source = "_".join(c.split("_")[-2:]))
						#input()
						max_bits = np.max(X["max_"+c])
						#c.split("toggle")
						
						def reuce(row):
							#print("row")
							#print(row)
							
							#input()
							if(row < 1.0 ):
								return 0.0
							else:
								return max_bits
						X[c] = X[c].apply(reuce)#0#,axis=1)
						
				#print(df[simple])
				#print(X)
				#input()
				X = X[simple]
				X = X*in_scaling[idx % len(in_scaling)]
				X = np.log1p(X)
				y = np.log1p(y)	
				#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
				X_train = X
				y_train = y
				X_test = X
				y_test = y

				y_test_pred = best_model.predict(X_test)
				y_train_pred = best_model.predict(X_train)
	
				y_test_pred = log1p_inverse(y_test_pred)/out_scaling
				y_train_pred = log1p_inverse(y_train_pred)/out_scaling

				y_train_golden = log1p_inverse(y_train)/out_scaling
				y_test_golden = log1p_inverse(y_test)/out_scaling
				#golden2 = np.array(y_train_golden) #np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				#our_pred2 = np.array(y_train_pred)#np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])
				accelergy_golden = np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				accelergy_pred = np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])

		
	




				#####################################METHOD V1################################3
				#print(df)
				#print(features)
				simple = [f for f in features if "bit" not in f]
				#print(df[simple])	
				y = df[out]*out_scaling[idx % len(out_scaling)]
				X = df[simple]*in_scaling[idx % len(in_scaling)]
				X = np.log1p(X)
				y = np.log1p(y)	

				X_train = X
				y_train = y
				X_test = X
				y_test = y

	

				best_model.fit(X_train, y_train)
				y_test_pred = best_model.predict(X_test)
				y_train_pred = best_model.predict(X_train)
	
				y_test_pred = log1p_inverse(y_test_pred)/out_scaling
				y_train_pred = log1p_inverse(y_train_pred)/out_scaling

				y_train_golden = log1p_inverse(y_train)/out_scaling
				y_test_golden = log1p_inverse(y_test)/out_scaling
				golden2 = np.array(y_train_golden) #np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred2 = np.array(y_train_pred)#np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])
				golden2 = np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred2 = np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])


				#####################################METHOD V2################################3

				simple = [f for f in features if "toggle" not in f]
				#print(df[simple])	
				y = df[out]*out_scaling[idx % len(out_scaling)]
				X = df[simple]*in_scaling[idx % len(in_scaling)]
				X = np.log1p(X)
				y = np.log1p(y)	

				X_train = X
				y_train = y
				X_test = X
				y_test = y

	

				best_model.fit(X_train, y_train)
				y_test_pred = best_model.predict(X_test)
				y_train_pred = best_model.predict(X_train)
	
				y_test_pred = log1p_inverse(y_test_pred)/out_scaling
				y_train_pred = log1p_inverse(y_train_pred)/out_scaling

				y_train_golden = log1p_inverse(y_train)/out_scaling
				y_test_golden = log1p_inverse(y_test)/out_scaling
				golden3 = np.array(y_train_golden) #np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred3 = np.array(y_train_pred)#np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])
				golden3 = np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred3 = np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])


				#####################################METHOD V3################################3

				simple = [f for f in features if not ("toggle" in f or "bit" in f  )]
				#print(df[simple])	
				y = df[out]*out_scaling[idx % len(out_scaling)]
				X = df[simple]*in_scaling[idx % len(in_scaling)]
				X = np.log1p(X)
				y = np.log1p(y)	

				X_train = X
				y_train = y
				X_test = X
				y_test = y

	

				best_model.fit(X_train, y_train)
				y_test_pred = best_model.predict(X_test)
				y_train_pred = best_model.predict(X_train)
	
				y_test_pred = log1p_inverse(y_test_pred)/out_scaling
				y_train_pred = log1p_inverse(y_train_pred)/out_scaling

				y_train_golden = log1p_inverse(y_train)/out_scaling
				y_test_golden = log1p_inverse(y_test)/out_scaling
				golden4 = np.array(y_train_golden) #np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred4 = np.array(y_train_pred)#np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])
				golden4 = np.concatenate([np.array(y_train_golden), np.array(y_test_golden)])
				our_pred4 = np.concatenate([np.array(y_train_pred), np.array(y_test_pred)])



	
	

	
	
					
				import random
				#random_int = random.randint(a, b)
				#two-stages power estimator
				#take several stages, low power, high power states
				b3_gold = []
				b3 = []
				N = 100
				#an ideal case, all the values are at the max
				for sparsity in range(0,N, 1):
					gold_power = 0
					zeros = sparsity
					ones = 0
					s = 0
					for n in range(sparsity, N):
						r = min(1,random.random()*2)
						s += r
						#if(r  > 0.5):
						ones += 1
						#else:
						#zeros += 1
					overall = (zeros*min_value + ones*max_value)/100
					bgolden = (max_value - min_value)*(s/100) + min_value
					#print(overall, bgolden)
					#exit()

					#print(zeros, ones)
					#print(overall, max_value)
					b3_gold.append(bgolden)
					b3.append(overall)
				#a more realistic scenario, have some values in the middle
				for sparsity in range(0, 100, 10):
					for rr in range(0, 10):	
						s = 0
						ones = 0	
						zeros = sparsity	
						rr = min(100,random.random()*100)
	
						for n in range(sparsity, 100):
							r = rr/100.0
							s += r
							#if(r  > 0.5):
							ones += 1
				#			#else:
				#			#	zeros += 1

						overall = (zeros*min_value + ones*max_value)/100
						bgolden = (max_value - min_value)*(s/100) + min_value
						
						b3_gold.append(bgolden)
						b3.append(overall)
	
				#print(len(b3_gold))
				#print(len(b3))
				#input()	
						
						
				#four-state-stages power estimator
				b4_gold = []
				b4 = []
				thirds_value =2/3* (max_value - min_value)
				quarters_value =1/3* (max_value - min_value)
	
				for sparsity in range(0, 100, 1):
					gold_power = 0
					zeros = sparsity
					ones = 0
					thirds = 0
					quarters = 0
					s = 0
					for n in range(sparsity, 100):
						r = min(1.0,random.random()*2)
						s += r
						if(r  > 0.75):
							ones += 1
						elif(r > 0.5):
							thirds += 1
						elif(r > 0.25):
							quarters += 1
						else:
							zeros += 1
					#print(zeros, quarters, thirds, ones)
					overall = (zeros*min_value + quarters*quarters_value + thirds*thirds_value + ones*max_value)/100
					bgolden = (max_value - min_value)*(s/100) + min_value

					b4_gold.append(bgolden)
					b4.append(overall)
				for sparsity in range(0, 100, 10):
					for rr in range(0, 100,10):	
						s = 0
						zeros = sparsity
						ones = 0
						thirds = 0
						quarters = 0
						rr = min(100,random.random()*200)
	
						for n in range(sparsity, 100):
							r = rr/100.0
							s += r
							if(r  > 0.75):
								ones += 1
							elif(r > 0.5):
								thirds += 1
							elif(r > 0.25):
								quarters += 1
							else:
								zeros += 1
						overall = (zeros*min_value + quarters*quarters_value + thirds*thirds_value + ones*max_value)/100
	
						bgolden = (max_value - min_value)*(s/100) + min_value
						b4_gold.append(bgolden)
						b4.append(overall)


				b3 = b3*10	
				b4 = b4*10
				b4_gold = b4_gold*10
				b3_gold = b3_gold*10


				#post processing
				golden_new = []	
				our_new = []
				accelergy_new = []
				b2_new = []	

				our_both_new = []
				our_toggle_new = []
				our_bits_new = []

				print('gold len', len(golden))
				for sparse in [1,2,4,5,6,7,8,12,16,24,32,48,64,128]:
					for i in range(0,len(golden)):#,10):
						golden_new.append(golden[i]*1.0/sparse)
						our_new.append(our_pred[i]*1.0/sparse)
						accelergy_new.append(accelergy_pred[i]*1.0/sparse)
						b2_new.append(b2[i]*1.0/sparse)
						#b2_new.append(accelergy_pred[i])
	
						our_both_new.append(our_pred4[i]*1.0/sparse)
						our_toggle_new.append(our_pred2[i]*1.0/sparse)
						our_bits_new.append(our_pred3[i]*1.0/sparse)
				

				########################PLOTTING#########################3
				#b2 = mean_arr
				#generate several random sequences
				'''
				plt.scatter(golden_new, accelergy_new, alpha=0.1)
				plt.scatter(golden_new, b2_new,alpha=0.1)	

				plt.scatter(golden_new, our_both_new,alpha=0.1)	
				plt.scatter(golden_new, our_toggle_new,alpha=0.1)	
				plt.scatter(golden_new, our_bits_new,alpha=0.1)	
				plt.scatter(golden_new, our_new, alpha=0.1)
				
				plt.legend(['Accelergy','Maestro',  
						 'OurNoToggle',  'OurNoToggle', 'OurNoBits', 'OurBoth'  ])	
				plt.plot(golden, golden, 'r-')
	

				#plt.scatter(
				plt.xlim(0, max_value)
				plt.ylim(0, max_value)

				plt.show()

				'''	
				#plt.scatter(golden, our_pred)	
				#plt.scatter(golden2, our_pred2)	
				#plt.scatter(golden3, our_pred3)	
				#plt.scatter(golden, accelergy_pred)	



				#plt.scatter(golden, b2)	
				#plt.scatter(golden, b1)	
				#plt.scatter(b3_gold, b3)	
				#plt.scatter(b4_gold, b4)	
	
				pkg =  {
					"golden": golden_new,
					"our": our_new,
					"accelergy": accelergy_new,
					"maestro": b2_new,
						
					"our_none": our_both_new,
					"our_toggle": our_toggle_new,
					"our_bits": our_bits_new,
				}
				#for p in pkg:
				#	print(len(pkg[p]))
				#input()
				return pkg


				return {

				"golden": golden,
				"estimate": our_pred,
				"estimate_no_bits": our_pred2,
				"estimate_no_toggle": our_pred3,

				"baseline1": b1,
				"baseline2": b2,
				"baseline3": b3,
				"baseline4": b4,
				"golden_baseline3": b3_gold,
				"golden_baseline4": b4_gold,

				


				}

				
				
