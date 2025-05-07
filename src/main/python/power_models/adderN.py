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


if __name__ == "__main__":

	def ones_count(x):
		"""计算数字 x 的二进制表示中 1 的个数"""
		return bin(x).count('1')

	# 加载数据
	# df = pd.read_csv("generated/AdderN/tsmc40_simple.txt",  delimiter="\t")
	df = pd.read_csv("generated/AdderN/tsmc40_RCA2.txt",  delimiter="\t")
	print(df)
	# 计算 toggle（假设 in_0 是字符串格式，例如 "0,3"）
	def calculate_toggle(in_0_str):
		# 分割字符串并转换为整数
		bits = list(map(int, in_0_str.split(',')))
		if(bits.length == 1):
			return 0
		else:
			# 计算异或值（XOR）
			xor_result = bits[0] ^ bits[1]
			# print(bin(xor_result), bin(xor_result).count('1'))
			# 统计二进制中 1 的个数
			return bin(xor_result).count('1')

	def calculate_bits(in_0_str):
		return bin(int(in_0_str)).count("1")
		
	# 应用 toggle 计算
	
	def calculate_toggle(in_0_str):
		# print(in_0_str)
		# 分割字符串并转换为整数
		bits = list(map(int, in_0_str.split(',')))
		# 计算异或值（XOR）
		xor_result = bits[0] ^ bits[1]
		# print(bin(xor_result), bin(xor_result).count('1'))
		# 统计二进制中 1 的个数
		return bin(xor_result).count('1')
		
	def calculate_cum_toggle(row):
		terms = row['terms']
		toggle_cols = [f'toggle_{i}' for i in range(terms)]
		return row[toggle_cols].sum()
	
	def calculate_out_toggle(row):
		terms = row['terms']
		cols = [f'in_{i}' for i in range(terms)]
		s = 0
		for c in cols:
			bits = list(map(int, row[c].split(',')))
			s += bits[1]
		return calculate_bits(s)
					
	df['toggle_0'] = df['in_0'].apply(calculate_toggle)
	df['toggle_1'] = df['in_1'].apply(calculate_toggle)
	df['toggle_2'] = df['in_2'].apply(calculate_toggle)
	df['toggle_3'] = df['in_3'].apply(calculate_toggle)
	
	# df['toggle'] = df['toggle_0']+df['toggle_1']
	df['toggle'] = df.apply(calculate_cum_toggle, axis = 1)
	df['out_toggle'] = df.apply(calculate_out_toggle, axis = 1)
	#?what about output toggle ?
	
	# df['toggle_out'] = 
	#df['bits_0'] = df['in_0'].apply(calculate_bits)
	#df['bits_1'] = df['in_1'].apply(calculate_bits)
	
	# 添加新列 1/CLOCK（注意避免除以 0）
	df['inv_CLOCK'] = 1 / df['CLOCK'].replace(0, np.nan)  # 如果 CLOCK 为 0，替换为 NaN
	df = df.dropna()  # 删除包含 NaN 的行
	

	# 特征列
	# 2. 定义分组列
	group_cols = ['prec', 'buffered', 'fanout',  'terms', 
	             'CLOCK', 'cap_load', 'fanout_load','inv_CLOCK']

	features = ['prec_in', 'terms', 'inv_CLOCK', 'cap_load', 'toggle']

	# 目标变量#+ ['toggle', 'out_toggle']
	features = ['prec_in', 'terms', 'inv_CLOCK', 'cap_load', ] +\
	['toggle_0',	'toggle_1', 'toggle_2', 'toggle_3', 'out_toggle']
	
	out = 'Total_Pwr'
	df = df
	
	# features = ['fanout', 'inv_CLOCK', 'cap_load']
	# out = 'coef'
	# df = final_df
	
	y = df[out]*1e10
	X = df[features]*1e5
	X = np.log1p(X)
	y = np.log1p(y)	
		
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
	
	# X_train = X
	# X_test = X
	# y_train = y
	# y_test = y
	
	# 6. 定义模型列表
	models = {
	    "LinearRegression": LinearRegression(),
	    "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
	    "RandomForestRegressor": RandomForestRegressor(random_state=42),
	    "GradientBoostingRegressor": GradientBoostingRegressor(random_state=42),
	    "LinearSVR": LinearSVR(random_state=42),
	    "SVR": SVR(),
	    "MLPRegressor": MLPRegressor(random_state=42, max_iter=1000)
	}
	
	# 4. 遍历模型，训练并评估
	results = {}
	
	trained_models = {}
	def log1p_inverse(x):
	    return np.exp(x) - 1
			
	for name, model in models.items():
	    # 训练模型
	    model.fit(X_train, y_train)
	    
	    # 预测
	    # print(X_test)
	    # exit(0)
	    y_pred = model.predict(X_test)
	    
	    # 计算评估指标
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
	
	import pickle
	with open('generated/PowerModels/adderN.pkl', 'wb') as f:
	    pickle.dump(trained_models[best_model], f)
	
	# # toggle vs. power
	# data = [[2, 1/1, 0.1   ,1 ], 
	# 	[2, 1/1, 0.1  ,1.5 ], 
	# 	[2, 1/1, 0.1  ,2 ],
	# 	[2, 1/1, 0.1  ,2.5],
	# 	[2, 1/1, 0.1  ,3]
	# 	]
	# testing_df = pd.DataFrame(data, columns=['fanout', 'inv_CLOCK', 'cap_load','toggle'])
	# X = np.log1p(testing_df[features]*1e5)
	
	# best_m = trained_models["SVR"]
	# y =  log1p_inverse(best_m.predict(X))/1e10
	# import matplotlib.pyplot as plt
	# plt.plot([1,1.5,2,2.5,3], y )
	# plt.show()
	