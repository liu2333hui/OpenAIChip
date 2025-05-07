import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score


def hua(logs_dir):


	#look at folders and designs
	all_data = []#pd.DataFrame()
	for res in logs_dir:
		for root, dirs, files in os.walk(res):
			for dir_name in dirs:
				design_dir = os.path.join(root, dir_name)
				collection = pd.DataFrame()
				for file_name in os.listdir(design_dir):	
					file_path = os.path.join(design_dir, file_name)
					df = pd.read_csv(file_path, sep='\t')
							
					#all_data = pd.concat([all_data, df], ignore_index=True)
					collection = pd.concat([collection, df], ignore_index=True)	
				if(not collection.empty):
					all_data.append(collection)

	#plot figure 
	#print(all_data)
	#print(all_data.columns)

	#for mod_df in all_data:
	#	print(mod_df)

	valid_modules = {"Total":["total"], "PE":["PE"], "INTERCONNECT":["L1_WEI_MULTICAST", "L1_ACT_MULTICAST"], "L1":["L1_WEI_READ", "L1_WEI_WRITE","L1_ACT_READ", "L1_ACT_WRITE"], "L2": ["L2_WEI_READ", "L2_WEI_WRITE", "L2_ACT_READ", "L2_ACT_WRITE" ]  }
	valid_models = ["baseline1", "baseline2", "estimate",]

	modules = len(valid_modules.keys())
	models = len(valid_models)
	fig, axes = plt.subplots(nrows=models, ncols=modules, figsize=(10, 7)) 

	#all_data[0].to_csv('output.csv', index=False)

	merge_data = pd.DataFrame()
	for mod_df in all_data:
		merge_data = pd.concat([merge_data, mod_df], ignore_index=True)	

	#first pass (golden)
	print(merge_data)
	#for mod_df in merge_data:	
	mod_df = merge_data.fillna(0)
	axes[-1, len(valid_modules)//2 ].set_xlabel("golden (W)")
	if True:
		for hidx, hardware in enumerate(valid_modules):
			keys = valid_modules[hardware]	
			print("keys", keys)
			print("mod_df", mod_df)
			if(len(keys) == 1):
				
				golden = mod_df[[k+"_golden_pwr" for k in keys]]
			else:
				golden = np.sum(np.array(mod_df[[k+"_golden_pwr" for k in keys]]), axis=-1)
			for idx, mm in enumerate(valid_models):
				if(idx == 0):
					axes[idx, hidx].set_title(hardware)	
				if(hidx == 0):
					axes[idx, hidx].set_ylabel(f'{mm} (W)')
	
					
				
				golden = np.array(golden)

				#errors
				if(len(keys) == 1):
					model_estimate = mod_df[[k+"_"+mm+"_pwr" for k in keys]]
				else:
					model_estimate = np.sum(np.array(mod_df[[k+"_"+mm+"_pwr" for k in keys]]), axis=-1)
				model_estimate = np.array(model_estimate)
	
				power_mse = mean_squared_error( model_estimate  , golden  )
				power_r = r2_score( model_estimate  , golden  )

				relative_errors = np.abs((model_estimate - golden) / (golden+1e-19))
				power_relative = np.mean(relative_errors)
	 
				text = "MSE:%f\nR:%f\nErr:%f" %(power_mse, power_r, power_relative)#f'MSE: {mse:.2f}\nR: {r:.2f}'
				axes[idx, hidx].text(0.05, 0.95, text, transform=axes[idx,hidx].transAxes, fontsize=8,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))


				axes[idx, hidx].plot(golden, golden, 'r')

	#second pass (against golden)
	for mod_df in all_data:
		
		for hidx, hardware in enumerate(valid_modules):

			keys = valid_modules[hardware]	
			if(keys[0]+"_golden_pwr" not in mod_df.columns ):
				continue
			print(mod_df[keys[0]+"_golden_pwr"])
			if(len(keys) == 1):
				golden = mod_df[[k+"_golden_pwr" for k in keys]]
			else:
				golden = np.sum(np.array(mod_df[[k+"_golden_pwr" for k in keys]]), axis=-1)
	
			for idx, mm in enumerate(valid_models):
				if(len(keys) == 1):
					model_estimate = mod_df[[k+"_"+mm+"_pwr" for k in keys]]
				else:
					model_estimate = np.sum(np.array(mod_df[[k+"_"+mm+"_pwr" for k in keys]]), axis=-1)
				golden = np.array(golden)
				model_estimate = np.array(model_estimate)
				
				axes[idx, hidx].scatter(golden, model_estimate)	
	
 



	fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.3, hspace=0.3)




	plt.show()



def hua_all(logs_dir):


	#look at folders and designs
	all_data = pd.DataFrame()
	for res in logs_dir:
		for root, dirs, files in os.walk(res):
			for dir_name in dirs:
				design_dir = os.path.join(root, dir_name)
				collection = pd.DataFrame()
				for file_name in os.listdir(design_dir):	
					file_path = os.path.join(design_dir, file_name)
					df = pd.read_csv(file_path, sep='\t')
					all_data = pd.concat([all_data, df], ignore_index=True)
					collection = pd.concat([collection, df], ignore_index=True)	
			#	all_data.append(collection)
	all_data = [all_data]
	#plot figure 
	#print(all_data)
	#print(all_data.columns)


	valid_modules = {"Total":["total"], "PE":["PE"], "INTERCONNECT":["L1_WEI_MULTICAST", "L1_ACT_MULTICAST"], "L1":["L1_WEI_READ", "L1_WEI_WRITE","L1_ACT_READ", "L1_ACT_WRITE"], "L2": ["L2_WEI_READ", "L2_WEI_WRITE", "L2_ACT_READ", "L2_ACT_WRITE" ]  }
	valid_models = ["estimate", "baseline1", "baseline2"]

	modules = len(valid_modules.keys())
	models = len(valid_models)
	fig, axes = plt.subplots(nrows=models, ncols=modules, figsize=(10, 8)) 
	

	#for mod_df in all_data:
	for mod_df in all_data:
		print(mod_df)
		for hidx, hardware in enumerate(valid_modules):

			keys = valid_modules[hardware]	

			if(len(keys) == 1):
				golden = mod_df[[k+"_golden_pwr" for k in keys]]
			else:
				golden = np.sum(np.array(mod_df[[k+"_golden_pwr" for k in keys]]), axis=-1)
	

			for idx, mm in enumerate(valid_models):
				if(len(keys) == 1):
					model_estimate = mod_df[[k+"_"+mm+"_pwr" for k in keys]]
				else:
					model_estimate = np.sum(np.array(mod_df[[k+"_"+mm+"_pwr" for k in keys]]), axis=-1)
				golden = np.array(golden)
				model_estimate = np.array(model_estimate)
	
				#print(np.array(golden))
				#print(model_estimate)
				
				axes[idx, hidx].scatter(golden, model_estimate, )	
				axes[idx, hidx].plot(golden, golden, 'r')

				axes.set_xlim(0, 1e-3)
				axes.set_ylim(0, 1e-3)				
				
				axes[idx, hidx].set_xscale("log")
				axes[idx, hidx].set_yscale("log")
				#plt.show()
	fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.3, hspace=0.3)
	plt.xscale("log")
	plt.yscale("log")


	plt.show()

if __name__ == "__main__":
	results_folder = ["generated/Architecture/SimpleArch/logs"]
	hua(results_folder)
