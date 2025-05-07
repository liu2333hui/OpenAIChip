import random
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


#sparsity: 0.0, not sparse, 1.0, very sparse
#bit_zero: 0, not bit sparse, prec very bit sparse	
def gen_in(sparsity, bit_zero, prec = 8, N = 1000, REUSE = 1,  MAX = 512):
	bit_zero = max(1,int(prec) - bit_zero)
	#print(bit_zero)
	#exit()
	#if(N > MAX):
	#N = MAX
	N = N #% (4*4*3*3*5*5)
	REUSE = REUSE #% (60)
	#print(REUSE, N)

	N = N +1
	v = []
	for n in range(int(N*(1-sparsity))):
		cur = random.randint(0, 1<<bit_zero)

		v.append(cur)

	for n in range(int(N*sparsity)):
		v.append(0)

	random.shuffle(v)	
	#print(v)
	#print(np.repeat(v, REUSE))
	#print(REUSE)
	#input()
	res= np.repeat(v, REUSE).tolist()
	return res
	return [r for idx,r in enumerate(res) if(idx <= 7*7*4*4*3*3*5*5-1)]
	return v


def toggle_estimator(sparsity, bit_zero, prec = 8, N=10000):
	#N =100000
	prev = 0
	cnt = 0

	v = []
	for n in range(int(N*(1-sparsity))):
		cur = random.randint(0, 1<<bit_zero)

		v.append(cur)

	for n in range(int(N*sparsity)):
		v.append(0)

	random.shuffle(v)	

	prev =0 
	for n in range(N-1):
		cur = v[n]
		cnt +=bin(prev ^ cur).count("1")
		prev = cur
		
	#print(v)

	return cnt / (N*prec)
		

def toggle_test():
	M = 10
	prec = 8
	sparsities = []
	bits = []
	toggles = []
	for sp in range(0, 100, 10):
		sparsity = sp/100.0
		for bit_zero in range(0, prec):
			T = []
			for m in range(M):
				t = toggle_estimator(sparsity, bit_zero, prec = prec,N=1000*m+1000)#, 10000*m+10000)
				T.append(t)		
			print(sparsity, bit_zero, T, sum(T)/len(T))#toggles[-1])
			toggles.append(sum(T)/len(T))
			bits.append(bit_zero)
			sparsities.append(sparsity)
	
	import pickle
	with open("toggles.pkl", "wb") as f:
		pickle.dump(toggles, f)
	with open("sparsities.pkl", "wb") as f:
		pickle.dump(sparsities, f)
	with open("bits.pkl", "wb") as f:
		pickle.dump(bits, f)


def toggle_train():
	import pickle
	with open("toggles.pkl", "rb") as f:
		toggles = pickle.load(f)
	with open("sparsities.pkl", "rb") as f:
		sparsities = pickle.load(f)
	with open("bits.pkl", "rb") as f:
		bits = pickle.load(f)
	
	import matplotlib.pyplot as plt
	plt.scatter(sparsities, toggles)
	plt.show()

	plt.scatter(bits, toggles)
	plt.show()


def toggle_train():
	import pickle
	with open("toggles.pkl", "rb") as f:
		toggles = pickle.load(f)
	with open("sparsities.pkl", "rb") as f:
		sparsities = pickle.load(f)
	with open("bits.pkl", "rb") as f:
		bits = pickle.load(f)
	
	#import matplotlib.pyplot as plt
	#plt.scatter(sparsities, toggles)
	#plt.show()

	#plt.scatter(bits, toggles)
	#plt.show()

	models = {
		 #   "LinearRegression": LinearRegression(),
		    "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
		    "RandomForestRegressor": RandomForestRegressor(random_state=42),
		 #   "GradientBoostingRegressor": GradientBoostingRegressor(random_state=42),
		 #   "LinearSVR": LinearSVR(random_state=42),
		 #   "SVR": SVR(),
		 #   "MLPRegressor": MLPRegressor(random_state=42, max_iter=1000)
		}
		

	df = pd.DataFrame()
	df['sparsities'] = sparsities
	df['bits'] = bits	
	X_train =df
	y_train = np.array(toggles)
	for m in models:
		model = models[m]
		
		model.fit(X_train, y_train)
	
		y_pred = model.predict(X_train)
		
		relative_error = np.mean(np.abs((y_train - y_pred) / y_pred)) * 100
		print(m,relative_error)
		
		with open(f'{m}.pkl', 'wb') as f:
			pickle.dump(model, f)

	
	
def toggle_infer(bits, sparsity):
	models = {
		 #   "LinearRegression": LinearRegression(),
		    "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
		    "RandomForestRegressor": RandomForestRegressor(random_state=42),
		 #   "GradientBoostingRegressor": GradientBoostingRegressor(random_state=42),
		 #   "LinearSVR": LinearSVR(random_state=42),
		 #   "SVR": SVR(),
		 #   "MLPRegressor": MLPRegressor(random_state=42, max_iter=1000)
		}
	
	m = 'DecisionTreeRegressor'	
	with open(f'{m}.pkl', 'rb') as f:
		model = pickle.load(f)


	df = pd.DataFrame()
	df['sparsities'] = [sparsity]#sparsities
	df['bits'] = [bits]
	X_train =df
	
	toggles = model.predict(X_train)
	return toggles[0]	

if __name__ == "__main__":
	#toggle_test()
	#toggle_train()
	ss = []
	bb = []
	tt = []
	for sparsity in range(0, 100):
		s = sparsity/100.0
		for bits in range(0, 8):
			t = toggle_infer(bits, s)
			print(t)
			bb.append(bits)
			ss.append(s)
			tt.append(t)		

	import matplotlib.pyplot as plt
	plt.scatter(ss, tt)
	plt.show()

	plt.scatter(bb, tt)
	plt.show()


