#new_path = "/nfs/project/JayMok/power_experiments_xie/primitives"
#os.environ['LD_LIBRARY_PATH'] = os.pathsep.join([new_path, os.environ.get('LD_LIBRARY_PATH', '')])
#print(os.environ['LD_LIBRARY_PATH'])
IS_LINUX = 1
SBT = "/afs/ee.ust.hk/staff/ee/jaymok/.local/share/coursier/bin/sbt"
import sys
#power_models_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(power_models_dir)
#power_models_dir = os.path.dirname(os.path.abspath(__file__) + "/power_models")
#sys.path.append(power_models_dir)
DEBUG = 0

import copy



if(IS_LINUX):
	import ctypes
	ctypes.CDLL('/nfs/project/JayMok/power_experiments_xie/primitives/libstdc++.so.6')
	ctypes.cdll.LoadLibrary('/nfs/project/JayMok/power_experiments_xie/primitives/libstdc++.so.6')
import numpy as np
import paddle.nn as nn
import os
import json
import pandas as pd
import os


import os
import pandas as pd
import numpy as np
#Several functions to collect already generated power traces
#or can be used to generate powers if json and traces are existing
import json
import glob

from ArchTemplates import trace_file


############################
from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
#from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive	
from power_models.MaxNPrimitive import MaxNPrimitive
from power_models.CrossbarPrimitive import CrossbarPrimitive
from power_models.MuxNPrimitive import MuxNPrimitive
from power_models.SRAMSPrimitive import SRAMSPrimitive
from power_models.SRAMSPrimitive import SRAMSPrimitive
from power_models.DeserializerPrimitive import DeserializerPrimitive
from power_models.Parallel2SerialPrimitive import Parallel2SerialPrimitive
	

from power_models.MulticastPrimitive import MulticastPrimitive
	
############################




# 1. read json
# 2. read fixed powers
# 3. generate energy estimate
def baseline1():
	pass
# 1. read json
# 2. read calibrated powers
# 3. generate energy estimate
def baseline2():
	pass

# 1. read json
# 2. read LUT state powers
# 3. generate energy estimate
def baseline3():
	pass


#read the golden file
def analyze_golden(r, units = -1):

	if(units == -1):
		root = "/".join(r.split("/")[0:-1])
		head = ".".join(r.split("/")[-1].split(".")[0:-1])
		#print("root", root)
		#print("head", head)
		for files in os.listdir(root):
			if("trace" in files and head in files):
				trace_sample = root+"/"+files
				break

		try:
			#trace_sample = r.split(".")
			#print(trace_sample)
			trace = pd.read_csv(trace_sample,header=None,  delimiter="\t", on_bad_lines = "skip").dropna(axis=1)
			#print(trace)
			#print(len(trace.columns))
			units = len(trace.columns)
	
		except:
			return -1
	
	try:
		print(units)
		POWER_GOLDEN_FILE = r
		gold = pd.read_csv(POWER_GOLDEN_FILE,  delimiter="\t")
		rel = gold.tail(n=units)['Total_Pwr']
	
		#print(rel)	
		if(len(rel) == 0):
			return -1
		res = {"unit_pwrs": rel, "total_pwrs": np.sum(rel), "avg_pwrs": np.sum(rel)/len(rel)}
		#print("GOLDEN", res)
	
		#with open(r, "r") as f:
		#	for l in f.readlines():
		#		print(l)	
		#exit()
		#pass
		return res
	except:
		return -1

def analyze_our(JSON_FILE):
	with open(JSON_FILE, 'r', encoding='utf-8') as f:
		jdata = json.load(f)
	#print(jdata)
	return jdata

	pass

def analyze_b1():
	pass

def analyze_b2():
	pass

def analyze_b3():
	pass

BENCHMARKS = {}
DATASET = {}

def analyze_result(res):
	rr = res.split(".")	
	r = rr[-1]
	net = rr[-2]
	benchmark = ".".join(res.split("/")[-1].split(".")[0:-2]).replace("_", "")

	BENCHMARKS[benchmark] = BENCHMARKS.get(benchmark, len(BENCHMARKS))

	#BENCHMARKS[str(len(BENCHMARKS))] = benchmark
	#exit()
	if(r == "golden"):
		gold = analyze_golden(res)
		#failed case
		if(gold == -1):
			pass
		else:
			print("\t"*3,"PRIMITIVE (GOLD)@", BENCHMARKS[benchmark],":", net, gold['total_pwrs'])
		#exit()
		pass


	elif(r == "our"):
		gold = analyze_our(res)
		#failed case
		if(gold == -1):
			pass
		else:
			print("\t"*3,"PRIMITIVE (OUR)@", BENCHMARKS[benchmark],":", net, gold['estimated_our'])
	
		#input()
		return gold

		#print(res)
		#exit()
		pass

	elif(r == "baseline1"):
		pass

	elif(r == "baseline2"):
		pass
	
	elif(r == "baseline3"):
		pass
	elif(r == "cpp"):
		pass
	elif(r == "json"):
		pass
	elif(r == "txt"):
		pass		

# 1. read json
# 2. read traces
# 3. generate input_data, hardware params
# 4. feed into ML model
def generate_our_pwr(res):
	rr = res.split(".")	
	r = rr[-1]
	net = rr[-2]
	benchmark = ".".join(res.split("/")[-1].split(".")[0:-2]).replace("_", "")

	BENCHMARKS[benchmark] = BENCHMARKS.get(benchmark, len(BENCHMARKS))

	#BENCHMARKS[str(len(BENCHMARKS))] = benchmark
	#exit()
	if(r == "golden"):
		#read json
		JSON_FILE = '.'.join(rr[0:-1] + ['json'])
		OUR_FILE = '.'.join(rr[0:-1] + ['our'])
			
		#print(OUR_FILE)
		#print(os.path.exists(OUR_FILE))
		#input()
		if(os.path.exists(OUR_FILE)):
			print("exists")
			#return 1
			#exit()


		POWER_GOLDEN_FILE = res

		#ad-hoc for now
		with open(JSON_FILE, 'r', encoding='utf-8') as f:
			jdata = json.load(f)
		print(jdata)
		
		print(res)
		#print(JSON_FILE)


		#2. read traces
		'''
		root = "/".join(rr[0:-1])
		print(root)
		head = ".".join(rr[-1].split(".")[0:-1])
		#print("root", root)
		#print("head", head)
		TRACES = []
		for files in os.listdir(root):
			if("trace" in files and head in files):
				trace_sample = root+"/"+files	
				TRACES.append(trace_sample)
		'''

		TRACE_JI = '.'.join(rr[0:-1] + ['trace'])
	
		txt_files = glob.glob(TRACE_JI+"*")  
		print(len(txt_files))  # 输出: ['file1.txt', 'file2.txt', ...]
		
		#print(jdata.keys())
		primitive = jdata['primitive']
	
		primitive_name = primitive.split(".")[1]


		
		# 3. generate input_data, hardware params
		crossbar_flag =False
	
		num_inputs = len(txt_files)
		TRACE_FILES = txt_files[0:num_inputs]

	

		#if(primitive_name != "Multiplier2"):
		#	return -1	
		factor = 1

		if(primitive_name == "ConstantMultiplier2"):
			return -2
		if(primitive_name == "Multiplier2"):
			prim = Multiplier2Primitive()

				
		elif(primitive_name == "MaxN"):
			prim = MaxNPrimitive()
	
		elif(primitive_name == "AdderN"):
			prim = AdderNPrimitive()
		#elif(primitive_name == "ConstantMultiplier"):
		#	prim = ConstantMultiplier()
		elif(primitive_name == "SRAMS"):
			prim = SRAMSPrimitive()		
		elif(primitive_name == "Deserializer"):#caster
			prim = DeserializerPrimitive()		
	
		elif(primitive_name == "Multicast"):#caster
			prim = MulticastPrimitive()		
	
		elif(primitive_name == "MuxN"):
			prim = MuxNPrimitive()		
	
		elif(primitive_name == "Parallel2Serial"):
			prim = Parallel2SerialPrimitive()		
	
		elif(primitive_name == "Crossbar"):
			print("HERE")
			prim = MuxNPrimitive()		
			primitive_name = "MuxN"	
			crossbar_flag = True
			
			jdata['terms'] = jdata['in_terms']
			num_inputs = jdata['terms']	
			TRACE_FILES = txt_files[0:num_inputs]
			#prim = CrossbarPrimitive()		
			factor = jdata['out_terms']
		else:
			print("primitive ", primitive_name, "no model")
			
			exit()

		if('in_terms' in jdata):
			jdata['terms'] = jdata['in_terms']
		else:
			jdata['terms'] = num_inputs
	
	

		CONFIG = {}
		CONFIG.update({
					"fanout_load": 0.0,
			})
		CONFIG.update(  jdata    )
	


		#print(CONFIG)
		#input()
		g,h,d = prim.get_features(primitive_name, out_features = ['Total_Pwr'])
	


		input_data = {}
		#if 'terms' not in input_data:
		#	input_data['terms'] = [num_inputs]


		for gg in h+g:
			if("inv" in gg):
				ggg = gg.split("_")[1]	
				input_data[gg] = [1.0/CONFIG[ggg]]
				input_data[ggg] = [CONFIG[ggg]]


			else:
				input_data[gg] = [CONFIG[gg]]
	
		
		if("terms" not in input_data):
			input_data['terms'] = [num_inputs]

		r = 1
		
		try:
			input_data = trace_file(num=num_inputs, TRACE_FILE=TRACE_FILES, input_data=input_data, r = r)
		except:
			return -1

		#print(input_data)
	
		#exit()
		
	

		# 3-4. Post-processing of input _data
		#(todos)
		results = []
		if(crossbar_flag):
			print("crossbar!")
			print("first, split inputs into multpiple. Second. out_terms")
			for i in range(num_inputs-1):
				input_data[f"in_{num_inputs-i}"] = input_data[f"in_{num_inputs-i-1}"]	
			import copy
			for j in range(CONFIG['out_terms']):
				input_data_raw =copy.deepcopy( input_data)
	
				input_data_new = trace_file(num=1, TRACE_FILE=[txt_files[num_inputs+j]], input_data=input_data_raw, r = r)
				#print("INFERENCE")
				#for k in range(1,num_inputs+1):
				#	d = input_data["in_"+str(k)] 
				#	for dd in d:
				#		print(dd)
				#print(dd.split(","))
				#= [[int(dd) for dd in d.split(",")] for d in input_data["in_"+str(k)] ]
				#print(input_data_new)
				#input()
				res = prim.execute_testing(
					name = primitive_name,
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
						input_data = input_data_new
				)
	
				#print(j,res)	
				results.append(res)
	

		else:

	
			# 4. feed into ML model
			#print(input_data.keys())
			#input()
			try:
				res = prim.execute_testing(
					name = primitive_name,
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = input_data
			)
			except:
				return -1
	

			results.append(res)	

		print("reuslts",results)
		print("len_results",len(results))

		#get total power
		s = 0
		for r in results:
			r = r["Total_Pwr"]['res']
			for u in r:
				
				s+=u[1]#*len(u[0])	
		print("s",s, s)
		
		#Save results
		gold = 0
	
		PKG = {
		#	"results": results,
			"estimated_our": s,
		}

		#with open(OUR_FILE, "w", encoding="utf-8") as f:
		#    json.dump(PKG, f, ensure_ascii=False, indent=4)  # 格式化输出并支持中文‌:ml-citation{ref="1,4" data="citationList"}
	
		#exit()

		res = analyze_golden(POWER_GOLDEN_FILE)#, units = CONFIG['out_terms'])
		print(res)
		if(res==-1):
			return -1
		if(len(input_data['in_0']) < 30):#too short, offset
			gold = res['total_pwrs']/3
		else:
			gold = res['total_pwrs']

		PKG = {
		#	"results": results,
	
			"estimated_our": s*factor,
			"golden_raw": res['total_pwrs'],
			"golden": gold
		}
		print("GOLD", res)
		print("PKG",PKG)
		#input("OK?")


		with open(OUR_FILE, "w", encoding="utf-8") as f:
		    json.dump(PKG, f, ensure_ascii=False, indent=4)  # 格式化输出并支持中文‌:ml-citation{ref="1,4" data="citationList"}
	
	


		return PKG
		pass


	
def collect_new_flow(folder, analyze_result_fn):


	STRUCTURED_DATASET = {}
	SD = STRUCTURED_DATASET

	for item in os.listdir(folder):
		item_path = os.path.join(folder, item)
		if os.path.isfile(item_path):
			continue
			#print(f"文件: {item_path}")  # 处理文件
		elif os.path.isdir(item_path):		
			core = item	
			print(f"CORE: {item_path}")	
			prims = 0
			for core_type in os.listdir(item_path):
				print("\tCORE_TYPE:" + core_type)
				if(core_type not in SD):
					SD[core_type] = {}	
				item_item_path = os.path.join(item_path, core_type)
				if(os.path.isdir(item_item_path)):	
					for module in os.listdir(item_item_path):
						module_path = os.path.join(item_item_path, module)
						if(module not in SD[core_type]):
							SD[core_type][module] = {}
						if(os.path.isdir(module_path)):
							print("\t\tUNIT:" + module)						
							for component in os.listdir(module_path):
								if(component not in SD[core_type][module]):
									SD[core_type][module][component] = {}
	
								comp_path = os.path.join(module_path, component)
								print("\t\t\tCOMPONENT_TYPE:"+component)
									
								for component_type in os.listdir(comp_path):
									#print("\t\t\t\tRESULTS:"+component_type)
	
									#two-level arch
									prim_path = os.path.join(comp_path, component_type)
									gold = analyze_result_fn(prim_path)
									if(gold != None):	
										SD[core_type][module][component] = gold
	
				
									#for primitive_files in os.listdir(prim_fold):
									#print("\t\t\t\tPRIMITVE: " + primitive_files)
									prims += 1
						else:
							#one-level arch
							gold = analyze_result_fn(module_path)
							prims += 1
							if(gold != None):
								SD[core_type][module] = gold
	
							#print("\t\tRESULTS:"+module)
						#print("\t\t" + module)	
					#end components or primitives
			#end core
			#exit()
			#print(SD)
			print("prims", prims)
			print()
	return SD				
				

def collect_old_flow(root):	
	pass

def collect_2024_flow(root):
	pass	


def JSON2Panda(JSON_FILE):

	#COMPONENTS vs. POWERS
	component_data = {}

	#TOTAL vs. POWERS
	


	with open(JSON_FILE, 'r', encoding='utf-8') as f:
		jdata = json.load(f)
	
	#all primitives
	for cores in jdata:

		for units in jdata[cores]:

			if( "." in units ):
				#new row
				if(len(jdata[cores][units]) > 0):
					net = units.split(".")[-2]
					if(net not in component_data):
						component_data[net] = {"estimate": [], "golden": []}
					component_data[net]['estimate'] .append( jdata[cores][units]['estimated_our'])
					component_data[net]['golden'] .append( jdata[cores][units]['golden'])
	
					#print(+"\t"+str(jdata[cores][units]['estimated_our']) + "\t" +str( jdata[cores][units]['golden']))
						
			else:
				for component in jdata[cores][units]:
					#print(jdata[cores][units][component])
					pass
	
	import matplotlib.pyplot as plt
	data = component_data
	print(component_data.keys())
	
	fig, axes = plt.subplots(len(data),1, figsize=(10, 6*len(data)))  # 动态创建子图‌:ml-citation{ref="3,6" data="citationList"}
	for idx, (net_name, net_data) in enumerate(data.items()):
		ax = axes[idx] if len(data)>1 else axes  # 处理单网络情况
		ax.plot(net_data['estimate'], label='Estimate', marker='o')
		ax.plot(net_data['golden'], label='Golden', marker='x')
		#ax.scatter(net_data['golden'],net_data['estimate'], label='Estimate', marker='o')
		#ax.plot(net_data['golden'], label='Golden', marker='x')
	
		ax.set_title(f'{net_name} Comparison')
		ax.legend()

	plt.tight_layout()
	plt.show()
		

if __name__ == "__main__":
	#oNce everything ready
	#SD = collect_new_flow("generated/Arch", analyze_result)	
	#print(SD)	
	#with open("dataset.0409", "w", encoding="utf-8") as f:
	#    json.dump(SD, f, ensure_ascii=False, indent=4)  # 格式化输出并支持中文‌:ml-citation{ref="1,4" data="citationList"}
	#JSON2Panda("dataset.0409")
	
	#if we missing some our we can generate it here
	#collect_new_flow("generated/Arch", generate_our_pwr)#analyze_result)	
	collect_new_flow("generated/ArchWino", generate_our_pwr)#analyze_result)	
	
	SD = collect_new_flow("generated/ArchWino", analyze_result)	
	exit()
	#print(SD)	
	with open("dataset.0409", "w", encoding="utf-8") as f:
	    json.dump(SD, f, ensure_ascii=False, indent=4)  # 格式化输出并支持中文‌:ml-citation{ref="1,4" data="citationList"}
	JSON2Panda("dataset.0409")
	
	
	#collect_old_flow(00)
	#collect_2024_flow()
