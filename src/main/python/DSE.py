import numpy as np
from pprint import pprint
import copy
import pandas as pd
SBT = "/afs/ee.ust.hk/staff/ee/jaymok/.local/share/coursier/bin/sbt"
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
from toggle import gen_in
import os
import json
#####################################################
debug_sbt = 1

UNIT = "SystolicConvOur"
GLOBAL_RUNS = 0
START_RUN = 0#108#388#5#125#-1
COMPONENT_SELECT = []#"WEI_LOADER"]#"ADDER_TREE"]
PRIM_SELECT = []#"Network"]
MODES = [3]#1,2,0]#0-golden, 1-b1, 2-b2

N = 128


WEI_SPARSITY = 0.5  
WEI_BIT_ZERO = 3
ACT_SPARSITY = 0.5
ACT_BIT_ZERO = 3
ACT_PRECS = [8]
WEI_PRECS = [8]
######################################################
#Helpers

def dict_values_to_str(d):
    if isinstance(d, dict):  # 如果是字典
        return "_".join(dict_values_to_str(v) for v in d.values())
    elif isinstance(d, list):  # 如果是列表
        return "_".join(dict_values_to_str(item) for item in d)
    else:  # 其他类型（如字符串、整数等）
        return str(d)

    if isinstance(d, dict):  # 如果是字典
        return "{" + ", ".join(f"{k}: {dict_to_str(v)}" for k, v in d.items()) + "}"
    elif isinstance(d, list):  # 如果是列表
        return "[" + ", ".join(dict_to_str(item) for item in d) + "]"
    elif isinstance(d, int):  # 如果是整数
        return str(d)
    else:  # 其他类型（如字符串、浮点数等）
        return str(d)

def dict_to_str(d):
	return dict_values_to_str(d)


def valid_file(path):
	work_folder = path.split("/")[0:-1]
	if 1:
		path_parts = work_folder#.split('/')
	
		current_path = ""
		for part in path_parts:
		    current_path = os.path.join(current_path, part) if current_path else part
		    if not os.path.exists(current_path):
		        os.mkdir(current_path)
		        print(f"目录已创建: {current_path}")
		    else:
		        pass#print(f"目录已存在: {current_path}")


	return path
############################
#Components
#COMPONENTS



def get_prim(name):
	if(name == "AdderN"):
		return "adders.AdderN"
	elif(name == "Accumulator"):
		return "accumulators.RegAccumulatorNSpec"
	elif(name == "Multicast"):
		return "networks.Multicast"
	elif(name == "Deserializer"):
		return "networks.Deserializer"
	elif(name == "Parallel2Serial"):
		return "networks.Parallel2Serial"
	elif(name == "SRAMS"):
		return "memories.SRAMS"

	
	elif(name == "MaxN"):
		return "minmax.MaxN"

	elif(name == "MuxN"):
		return "networks.MuxN"
	elif(name == "ConstantMultiplier"):
		return "multipliers.ConstantMultiplier"


	#TODOS
	elif(name == "BitFusion"):
		return "multipliers.BitFusion"
	elif(name == "Cordic"):
		return "arithmetic.Cordic"
	elif(name == "FusedMultiplyAdd"):
		return "arithmetic.FusedMultiplyAdd"
	elif(name == "ConstantFusedMultiplyAdd"):
		return "arithmetic.ConstantFusedMultiplyAdd"
	elif(name == "Divider"):
		return "arithmetic.Divier"




def save_data(trace, in_data):

	with open(trace, "w") as f:
		for i in in_data:
			f.write(str(i) + "\t\n")


def get_golden(name, general_config,inputs = {}):
	if(1):
		JSON_FILE = valid_file(f"generated/DSE/tmp/{name}.json")
		TRACE_FILE = []
		for i in inputs:
			f = valid_file(f"generated/DSE/tmp/{name}.{i}")
			TRACE_FILE.append( f)
			#TRACE_FILE_1 = valid_file(f"generated/DSE/tmp/{name}.in_1")
			#print(inputs)
			save_data(f, inputs[i][0])
	#save_data(TRACE_FILE_1, in_1)
	def collapse(d):
		for k in d:
			d[k] = d[k][0]
	collapse(general_config)
	general_config.update({

		"EDAVerification": True,
		"fanout_load": 0.0,
		"OutputPowerFile": valid_file(f"generated/DSE/tmp/{name}.gold"),#blocks[module]["POWER_GOLDEN_FILE"],
		"tech": 'tsmc40',
		#"CustomMap": self.MODULES[module]['config'].get("CustomMap", {}),

		})	
	with open(JSON_FILE, "w") as json_file:
		json.dump(general_config, json_file, indent=4)  # indent 用于格式化输出	
	TRACE_FILES = " ".join(TRACE_FILE) #TRACE_FILE_0 + " " + TRACE_FILE_1
	primitive = get_prim(name)#"multipliers.name"
	print(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
	os.system(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')

	gold = pd.read_csv(general_config['OutputPowerFile'],  delimiter="\t")
	
	#	with open(general_config['OutputPowerFile']) as f:
	#for l in f.readlines():
	rel = gold.tail(n=1)['Total_Pwr']

	general_config['Total_Pwr'] = rel
	return general_config




#other models, 0 = golden, 1 = baseline1 (Use Avg power), 2 = baseline2 (Accelergy, two-state)
def MulticastBlock(h, hh, ratio, in_a, fanout = 1, mode = [0,1,2], PRIM_SELECT=[]):
	if(len(PRIM_SELECT) != 0 and "Multicast" not in PRIM_SELECT):
		return -1
	name = "Multicast"
	if 1:
		general_config = {
			"CLOCK": [h['CLOCK']],"cap_load": [h['cap_load']],
			'prec': [hh['PREC']],
			"terms": [1],
			"fanout": [fanout]#fanout]
		}
		input_data={}
		#print(INNER)
		#print(len(in_a))
		input_data[f"in_0"] = [in_a.tolist() ]	
	
		#print(input_data)
		#input_data.update(general_config)
		config = {}
		config.update(input_data)
		config.update(general_config)
		ap = MulticastPrimitive()
		res = ap.execute_testing(
			name = "Multicast",out_features = ['Total_Pwr'],input_data=config)	

	#b1 model
	if(1 in mode or 2 in mode):
		b1_res = ap.execute_get_lut( name=name, 
			out_features= 'Total_Pwr',
			constant_features = general_config,
			need_zero =True,#True,# False,#True,#False,#False,
			variable_features = {
				"in_0": general_config['prec'][0],#[1<<i for i in range(prec1)],
			})
		xiao = min(b1_res['Total_Pwr']['res'][-1][0])
		da = max(b1_res['Total_Pwr']['res'][-1][0])

	if(0 in mode):
		general_config.update({
			"CustomMap": [{}],
		})
		#print(general_config)
		if(debug_sbt):
			input()
		gold_res_r = get_golden(name,general_config, input_data)
		
		print(gold_res_r['Total_Pwr'])

	#if(1):
	#if(1 in mode):				
	#	print("b1_r",b1_res['Total_Pwr']['res'][-1][-1])
			

	#if(2 in mode):
	#sparsity = 1-sparsity
	#print("b2_r",sparsity,xiao + (da-xiao)*sparsity)#b1_res['Total_Pwr']['res'][-1][0]		

	#save results
	results = {}
	if(1 in mode):
		#print(res)
		#return b1_res
		results = b1_res
	if(2 in mode):
		#print(res)
		#return b1_res
		in_a = in_a.tolist()
		sparsity = 1 - in_a.count(0)/len(in_a)

		results = {"Total_Pwr": {"res": [[ xiao + (da-xiao)*sparsity ]]}}
	if(3 in mode):
		#print(res)
		#return b1_res
		results = res

	if(0 in mode):
		#print(res)
		#return b1_res
		results = {"Total_Pwr": {"res": [[gold_res_r]]}}

	return results



def NetworkBlock(h, hh,ratio ,in_0,sparsity, fanout , mode = [1,2,3], PRIM_SELECT=[]):
	if(len(PRIM_SELECT) != 0 and "Network" not in PRIM_SELECT):
		return -1
	
	input_data = {"in_0": [in_0]}

	#deserializer
	if(ratio < 0 ):
		general_config = {
			"CLOCK": [h['CLOCK']],"cap_load": [h['cap_load']],
			'prec': [hh['PREC']],
			"terms": [1],
			"out_terms": [abs(ratio)],"fanout": [fanout],
			"hardwareType": [ hh.get('NETWORK_TYPE', "Mux") ],
		}

		our_config = copy.deepcopy(general_config)
		our_config["in_0"] = [in_0]

		name = "Deserializer"
		ap = DeserializerPrimitive()
		res = ap.execute_testing(
			name = name,out_features = ['Total_Pwr'],input_data=our_config)	
	#serializer
	else:	
		general_config = {
			"CLOCK": [h['CLOCK']],"cap_load": [h['cap_load']],
			'prec': [hh['PREC']]	,
			"terms": [abs(ratio)],"fanout": [fanout],
			"hardwareType": [ hh.get('NETWORK_TYPE',"Mux") ],

			}
		our_config = copy.deepcopy(general_config)
		our_config["in_0"] = [in_0]


		INNER = abs(ratio)
		name = "Parallel2Serial"
		#print(INNER)
		arr = in_0
		sections = INNER
		#if(len(arr) - sections > 0):
		padded_arr = np.pad(arr, (0, sections - len(arr)  % sections), mode='constant', constant_values=0)
		in_a = padded_arr
		#print( sections  -  len(arr) % sections)
		#else:	
		#in_a = in_0
		#print(len(in_a), INNER)
		#print(len(arr), sections)
		#input()
		
		in_a_split = np.split(np.array(in_a), INNER)
		for t in range(int(INNER)):
			our_config[f"in_{t}"] = [in_a_split[t].tolist() ]		
		ap = Parallel2SerialPrimitive()
		res = ap.execute_testing(
			name = name,out_features = ['Total_Pwr'],input_data=our_config)	

	#b1 model
	if(1 in mode or 2 in mode):
		b1_res = ap.execute_get_lut( name=name, 
			out_features= 'Total_Pwr',
			constant_features = general_config,
			need_zero =True,#True,# False,#True,#False,#False,
			variable_features = {
				"in_0": general_config['prec'][0],#[1<<i for i in range(prec1)],
			})
		xiao = min(b1_res['Total_Pwr']['res'][-1][0])
		da = max(b1_res['Total_Pwr']['res'][-1][0])

	if(0 in mode):
		general_config.update({
			"CustomMap": [{}],
		})
		print(general_config)
		if(debug_sbt):
			input()
		gold_res_r = get_golden(name,general_config, input_data)

	if(1):
		if(1 in mode):				
			print("b1_r",b1_res['Total_Pwr']['res'][-1][-1])

		if(2 in mode):
			sparsity = 1-sparsity
			print("b2_r",sparsity,xiao + (da-xiao)*sparsity)#b1_res['Total_Pwr']['res'][-1][0]		

	results = {}
	if(1 in mode):
		#print(res)
		#return b1_res
		results = b1_res
	if(2 in mode):
		#print(res)
		#return b1_res
		results = {"Total_Pwr": {"res": [[ xiao + (da-xiao)*sparsity ]]}}
	if(3 in mode):
		#print(res)
		#return b1_res
		results = res

	if(0 in mode):
		#print(res)
		#return b1_res
		results = gold_res_r

	return results



	#print("our_r",res['Total_Pwr']['res'][-1][-1])
	#input()
	#exit()
	return res#, res_w

	

	return res


def SRAMBlock(h, hh, in_0, sparsity, rw_mode = 0,  mode = [], PRIM_SELECT=[]):
	if(len(PRIM_SELECT) != 0 and "SRAMS" not in PRIM_SELECT):
		return -1

	general_config = {
			"CLOCK": [h['CLOCK']],"cap_load": [h['cap_load']],
			"terms": [1],"entry_bits": [hh["SRAM_SIZE"][0]], "rows": [hh["SRAM_SIZE"][1]],
			"type": hh["SRAM_TYPE"],
			"mode": [rw_mode],		}

	name = "SRAMS"
	input_data = {"in_0": [in_0]}

	ap = SRAMSPrimitive()
	our_config = copy.deepcopy(general_config)
	our_config["in_0"] = [in_0]
	res_r = ap.execute_testing(
			name = "SRAMS", 
			out_features =['Total_Pwr'],
			input_data = our_config
	)
	#b1 model
	if(1 in mode or 2 in mode):
		general_config['mode'] = [0]
		b1_res = ap.execute_get_lut( name=name, 
			out_features= 'Total_Pwr',
			constant_features = general_config,
			need_zero =False,#True,# False,#True,#False,#False,
			variable_features = {
				"in_0": general_config['entry_bits'][0],#[1<<i for i in range(prec1)],
			})
		xiao = min(b1_res['Total_Pwr']['res'][-1][0])
		da = max(b1_res['Total_Pwr']['res'][-1][0])

	if(0 in mode):
		gold_res_r = get_golden(name,general_config, input_data)

	if(1):
		if(1 in mode):				
			print("b1",b1_res['Total_Pwr']['res'][-1][-1])

		if(2 in mode):
			sparsity = 1-sparsity
			print("b2",sparsity,xiao + (da-xiao)*sparsity)#b1_res['Total_Pwr']['res'][-1][0]		

	results = {}
	if(1 in mode):
		#print(res)
		#return b1_res
		results = b1_res
	if(2 in mode):
		#print(res)
		#return b1_res
		results = {"Total_Pwr": {"res": [[ xiao + (da-xiao)*sparsity ]]}}
	if(3 in mode):
		#print(res)
		#return b1_res
		results = res_r

	if(0 in mode):
		#print(res)
		#return b1_res
		results = gold_res_r

	return results


	#print("our",res_r['Total_Pwr']['res'][-1][-1])
	#input()
	#exit()
	return res_r#, res_w
	"""
	res_r = ap.execute_testing(
		name = "SRAMS",out_features = ['Total_Pwr'],
		input_data = {
			"CLOCK": [h['CLOCK']],"cap_load": [h['cap_load']],
			"terms": [1],"entry_bits": [hh["SRAM_SIZE"][0]], "rows": [hh["SRAM_SIZE"][1]],
			"mode": [0],"in_0": [in_0],
		})
	res_w = ap.execute_testing(
		name = "SRAMS",out_features = ['Total_Pwr'],
		input_data = {
			"CLOCK": [h['CLOCK']],"cap_load": [h['cap_load']],
			"terms": [1],"entry_bits": [hh["SRAM_SIZE"][0]], "rows": [hh["SRAM_SIZE"][1]],
			"mode": [1],"in_0": [in_0],
		})
	return res_r, res_w
	"""




def Multiplier2Block(h, hh, in_0, in_1, prec1, prec2,side, sparsity, mode = [0,1,2], PRIM_SELECT=[]):
	if(len(PRIM_SELECT) != 0 and "Multiplier2" not in PRIM_SELECT):
		return -1
	
	#print(len(in_0), len(in_1))
	general_config = {

		"CLOCK": [h['CLOCK']  ],
		"cap_load": [h['cap_load']],
		"prec1": [prec1],
       		"prec2": [prec2],
		"in_0":[in_0],#[i for i in in_0],#[[18],[158] ],
		"in_1":[in_1],#[i for i in in_1],#[[38],[27] ],   
		"radix": [hh["MULT_RADIX"]], 
		'terms': [2],	
		'multiplierType': [hh['MULT_TYPE']],#'HighRadixMultiplier'],
		'side': [side],
		'adderType': [hh['MULT_CORE_ADDER_TYPE']],	
	}
	#our model
	ap = Multiplier2Primitive()
	res = ap.execute_testing(
			name = "Multiplier2", 
			out_features =['Total_Pwr'],
			input_data = general_config
		)
	#print(res)
	#input()
	#power correction
	

	#b1 model
	if(1 in mode or 2 in mode):
		ap = Multiplier2Primitive()
		b1_res = ap.execute_get_lut( name="Multiplier2", 
			out_features= 'Total_Pwr',
			constant_features = {
			"CLOCK": [h['CLOCK']  ],
			"cap_load": [h['cap_load']],
			"prec1": [prec1],
       			"prec2": [prec2],
			"radix": [hh["MULT_RADIX"]], 
			'terms': [2],	
			'multiplierType': [hh['MULT_TYPE']],#'HighRadixMultiplier'],
				'side': [side],
				'adderType': [hh['MULT_CORE_ADDER_TYPE']],	
			},
			need_zero =False,#True,# False,#True,#False,#False,
			variable_features = {
				"in_0": prec1,#[1<<i for i in range(prec1)],
				"in_1": prec2,#3[1<<i for i in range(prec2)]
			})
		xiao = min(b1_res['Total_Pwr']['res'][-1][0])
		da = max(b1_res['Total_Pwr']['res'][-1][0])
	"""
	if(0 in mode):
		JSON_FILE = valid_file("generated/DSE/tmp/Multiplier2.json")
		TRACE_FILE_0 = valid_file("generated/DSE/tmp/Multiplier2.in_0")
		TRACE_FILE_1 = valid_file("generated/DSE/tmp/Multiplier2.in_1")
		def save_data(trace, in_data):
			with open(trace, "w") as f:
				for i in in_data:
					f.write(str(i) + "\n")
		save_data(TRACE_FILE_0, in_0)
		save_data(TRACE_FILE_1, in_1)
		def collapse(d):
			for k in d:
				d[k] = d[k][0]
		collapse(general_config)
		general_config.update({

		"EDAVerification": True,
		"fanout_load": 0.0,
		"OutputPowerFile": valid_file("generated/DSE/tmp/Multiplier2.gold"),#blocks[module]["POWER_GOLDEN_FILE"],
		"tech": 'tsmc40',
		#"CustomMap": self.MODULES[module]['config'].get("CustomMap", {}),

		})	
		with open(JSON_FILE, "w") as json_file:
			json.dump(general_config, json_file, indent=4)  # indent 用于格式化输出	
		TRACE_FILES = TRACE_FILE_0 + " " + TRACE_FILE_1
		primitive = "multipliers.Multiplier2"
		print(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
		os.system(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
	"""
	#if(0 in mode):
	#	get_golden(name,general_config, input_data)
	if(0 in mode):
		general_config.update({
			"CustomMap": [{}],
		})
		#print(general_config)
		if(debug_sbt):
			input()
		gold_res_r = get_golden(name,general_config, input_data)



	if(1):
		if(1 in mode):				
			print("b1",b1_res['Total_Pwr']['res'][-1][-1])
		if(2 in mode):
			sparsity = 1-sparsity
			print("b2",sparsity,xiao + (da-xiao)*sparsity)#b1_res['Total_Pwr']['res'][-1][0]		

	#print("our",res['Total_Pwr']['res'][-1][-1])
	#exit()
	results = {}
	if(1 in mode):
		#print(res)
		#return b1_res
		results = b1_res
	if(2 in mode):
		#print(res)
		#return b1_res
		results = {"Total_Pwr": {"res": [[ xiao + (da-xiao)*sparsity ]]}}
	if(3 in mode):
		#print(res)
		#return b1_res
		results = res

	if(0 in mode):
		#print(res)
		#return b1_res
		results = gold_res_r

	return results


	return res


def MuxBlock(h, hh, in_0, prec_in, in_terms,  sparsity, PRIM_SELECT=[], mode = []):
			
	if(len(PRIM_SELECT) != 0 and "Mux" not in PRIM_SELECT):
		return -1
	if(in_terms < 2):
		#just return a wire, no crossbar needed is simply a direct mapping
		return {"Total_Pwr": {"res": [ [ 0.0] ]}}

	if 1:
		general_config = {
			"CLOCK": [h['CLOCK']],"cap_load": [h['cap_load']],
			'prec': [hh['PREC']],
			"terms": [  in_terms   ]  ,
		}

		
		#do a quick check, zero eliminate in the in_0
		terminate_idx = []
		idx = 0
		INNER = in_terms
		input_data={
			"in_0": [ []]
		}
		for d_idx, d in enumerate(in_0):
			if(d != 0):
				input_data[f"in_0"][0].append( d_idx % INNER )
				idx += 1
			
			if((d_idx + 1)% max(1,INNER//h['SPARSE_RATIO']) == 0):
				terminate_idx.append(idx)
				idx = 0

		avg_terminate =int( max(1,sum(terminate_idx)/len(terminate_idx))) + 1
		#print(int(avg_terminate)+1)
		#print(h["SPARSE_RATIO"])
		for i in range(in_terms):
			res= np.repeat(in_0[i::INNER], avg_terminate).tolist()
			input_data[f"in_{1+i}"] = [ np.repeat( res, len(in_0)//len(res) )   ]
		#print([ len(input_data[f"in_{i}"][0]) for i in range(0, INNER+1)])
		#input()
		
		#for sequence longer than 4096, cut
		cut = min(4096, min([ len(input_data[f"in_{i}"][0]) for i in range(0, INNER+1)]))
		for i in range(0, INNER+1):
			input_data[f'in_{i}'] =[ input_data[f'in_{i}'][0][0:cut] ]
		
		if(cut == 0):
			return {"Total_Pwr": {"res": [[0]]}}
		
			
		#print(INNER, in_0[0::INNER])
		
		ap = MuxNPrimitive()
		input_data.update(general_config)
		res = ap.execute_testing(
			name = "MuxN",out_features = ['Total_Pwr'],input_data=input_data)	

	if(1 in mode or 2 in mode):
		variable_features = {
			'in_0': general_config['prec'],
			'in_1': general_config['prec'],
		}

		b1_res = ap.execute_get_lut( name="MuxN", 
				out_features= 'Total_Pwr',
			constant_features = general_config,
			need_zero =True,#True,# False,#True,#False,#False,
			variable_features = variable_features )

		xiao = min(b1_res['Total_Pwr']['res'][-1][0])
		da = max(b1_res['Total_Pwr']['res'][-1][0])


	if(0 in mode):
		general_config.update({
			"CustomMap": [{}],
		})
		#print(general_config)
		if(debug_sbt):
			input()
		gold_res_r = get_golden(name,general_config, input_data)


		
	#if(0 in mode):
	#	get_golden(name,general_config, input_data)

	results = {}
	if(1 in mode):
		#print(res)
		#return b1_res
		results = b1_res
	if(2 in mode):
		#print(res)
		#return b1_res
		results = {"Total_Pwr": {"res": [[ xiao + (da-xiao)*sparsity ]]}}
	if(3 in mode):
		#print(res)
		#return b1_res
		results = res

	if(0 in mode):
		#print(res)
		#return b1_res
		results = gold_res_r

	return results




	return res




def AdderNBlock( h, hh, in_0 ,  prec_in,  mode, sparsity , INNER = 2, PRIM_SELECT=[]):
	if(len(PRIM_SELECT) != 0 and "AdderN" not in PRIM_SELECT):
		return -1
	if(INNER < 2):
		INNER = 2	

	#power model

	if(hh['ADDERN_TYPE'] in ["AddTreeN", "SimpleAdderN"]):
		general_config = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['PREC']],
					"prec_sum": [hh['OUT_PREC']],
					"terms": [INNER],
					"adderNType": [hh["ADDERN_TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					}


		name = "AdderN"
		ap = AdderNPrimitive()
		general_config['terms'] = [INNER]
		input_data = {}
		for t in range(INNER):
			input_data[f"in_{t}"] =[ in_0]

		our_config = copy.deepcopy(general_config)
		our_config.update(input_data)
		res = ap.execute_testing(
					name = name,
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = our_config,#general_config,#input_data
					)
	




	
	elif(hh['ADDERN_TYPE'] == "Accumulator"):
		general_config = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['PREC']],
					"prec_out": [hh['OUT_PREC']],
					"terms": [1],
					"adderNType": [hh["ADDERN_TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					}



		name = "Accumulator"

		ap = AccumulatorPrimitive()
		#our model
		our_config = copy.deepcopy(general_config)
		input_data = {"in_0": [in_0]}
		our_config.update({"in_0": [in_0]})
		res = ap.execute_testing(
			name = name,
			out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
			input_data = our_config)
	#b1 model
	if(1 in mode or 2 in mode):
		b1_res = ap.execute_get_lut( name=name, 
				out_features= 'Total_Pwr',
			constant_features = general_config,
			need_zero =True,#True,# False,#True,#False,#False,
			variable_features = {
				"in_0": prec_in,#[1<<i for i in range(prec1)],
			})
		xiao = min(b1_res['Total_Pwr']['res'][-1][0])
		da = max(b1_res['Total_Pwr']['res'][-1][0])

	#golden
	#if(0 in mode):
	#	get_golden(name,general_config, input_data)


	if(0 in mode):
		general_config.update({
			"CustomMap": [{}],
		})
		#print(general_config)
		if(debug_sbt):
			input()
		gold_res_r = get_golden(name,general_config, input_data)


	if(1):
		if(1 in mode):				
			print("b1",b1_res['Total_Pwr']['res'][-1][-1])
		if(2 in mode):
			sparsity = 1-sparsity
			print("b2",sparsity,xiao + (da-xiao)*sparsity)#b1_res['Total_Pwr']['res'][-1][0]		

	results = {}
	if(1 in mode):
		#print(res)
		#return b1_res
		results = b1_res
	if(2 in mode):
		#print(res)
		#return b1_res
		results = {"Total_Pwr": {"res": [[ xiao + (da-xiao)*sparsity ]]}}
	if(3 in mode):
		#print(res)
		#return b1_res
		results = res

	if(0 in mode):
		#print(res)
		#return b1_res
		results = gold_res_r

	return results


	#print("our",res['Total_Pwr']['res'][-1][-1])
	#exit()
	return res



###############################################################














#########################################################
#SYSTOLIC
#########################################################
#Maestro-like
def SystolicMaxModel(hardware_config, benchmark):
	pass

#Accelergy-like
def SystolicTwoStateModel(hardware_config, benchmark):
	pass


def SystolicOurModel(hardware_config, benchmark, modes = []):
	global N
	MODES = modes
	
	h = hardware_config["GENERAL"]

	pe = h['TI']*h['TN']*h['TKX']*h['TKY']*h['TX']*h['TY']*h['TB']

	hp = {}	
	all_powers = {}
	for bb in benchmark:
		b = benchmark[bb]
		cycles = {}
		powers = {}


		#modify sparsity when there is no local re-use, or there is only reuse after a window
		wei_reuse = 1
		act_reuse = 1
		ACT  = ['B', 'I']
		if(h['INTER_PE_Y'] ):
			pass
		else:
			ACT.append("KX")
		if(h['INTER_PE_Y'] ):
			pass
		else:
			ACT.append("KY")

		wei_flag = 0
		act_flag = 0
		for var in h["LOOP_ORDER"][::-1]:
			if( wei_flag or var in ["N", "I", "KX", "KY"]):
				wei_reuse *= 1
				wei_flag = 1
			else:
				wei_reuse *= h["T"+var]

			if(act_flag or var in ACT):
				act_reuse *= 1
				act_flag = 1	
			else:	
				act_reuse *= h["T"+var]
			
		#print("wei_reuse", "act_reuse")
		#print(wei_reuse, act_reuse)
		#input()
		#print(b)
		in_a = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = h['ACT_PREC'], N = N, REUSE = act_reuse)
		in_w = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = h['WEI_PREC'], N = N, REUSE = wei_reuse)
		in_o = [in_w[idx] *in_a[idx] for idx in range(min(len(in_w), len(in_a)))]
		OUT_SPARSITY = 1 - in_o.count(0)/len(in_o)
	
		PE_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
			 (b['I']+h['TI']-1)//h['TI']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			




		INNER = h["TKX"]*h["TKY"]*h["TI"]

		ACC_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			

		#power cost, there is an added Parallel2Serial unit
		if(not  h['INTER_PE_X']  ):
			X_CYCLES =  (b['X']+h['TX']+h['TKX']-1)//(h['TX']+h['TKX']-1)  * (b['KX']+h['TKX']-1)//h['TKX'] 
			X_TILE = (h['TX'] + h['TKX'] - 1)
		else:
			X_CYCLES =   (b['X']+h['TX']-1)//h['TX'] 
			X_TILE = h['TX']

		if(not  h['INTER_PE_Y']  ):
			Y_CYCLES =  (b['Y']+h['TY']+h['TKY']-1)//(h['TY']+h['TKY']-1)  * (b['KY']+h['TKY']-1)//h['TKY'] 
			Y_TILE = (h['TY'] + h['TKY'] - 1)
		else:
			Y_CYCLES =   (b['Y']+h['TY']-1)//h['TY'] 
			Y_TILE = h['TY']

		WEI_TILE = h['TN']*h["TKX"]*h["TKY"]*h["TI"]
		ACT_TILE = h['TB']*X_TILE*Y_TILE*h["TI"]
		OUT_TILE = h['TB']*h["TX"]*h["TY"]*h["TN"]

		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 
	
		for component in hardware_config:
			c = component
			hh = hardware_config[component] 
			#print(bb,component)
			if(component == "PE_ARRAY"):
				side = hh["MULT_SIDE"]
				radix = hh['MULT_RADIX']
				ratio = np.log2(radix)
				if(side == "weight"):
					side_cycle = hh["WEI_PREC"]/ratio
					prec1 = hh["WEI_PREC"]
					prec2 = hh["ACT_PREC"]
					side_bits =1 -  b["WEI_BIT_ZERO"]/hh['WEI_PREC']
					in_0 = in_w#gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N)
					in_1 = in_a#gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N)
					sparsity = b['WEI_SPARSITY']
				else:
					in_0 = in_a#gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N)
					in_1 = in_w#gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N)
					side_cycle = hh["ACT_PREC"]/ratio				
					prec2 = hh["WEI_PREC"]
					prec1 = hh["ACT_PREC"]	
					side_bits =1 -  b["ACT_BIT_ZERO"]/hh['ACT_PREC']

					sparsity = b['ACT_SPARSITY']

				cc = min(len(in_0), len(in_1))
				in_0 = in_0[0:cc]
				in_1 = in_1[0:cc]
	
		
				#power model
				res = Multiplier2Block(h, hh, in_0, in_1, prec1,prec2= prec2, side=side,mode=MODES, sparsity = sparsity)


				units = pe
				#powers[c] = res['Total_Pwr']['res'][-1] * units
				powers[c] = res['Total_Pwr']['res'][-1][-1] *units



			
			elif(component == "ADDER_TREE"):
		
				
				#res = AdderNBlock(, h=h, hh=hh, in_0=in_0 ,   mode=modes, sparsity = sparsity)
				res = AdderNBlock( h, hh, in_o ,  hh["PREC"],  mode=MODES, sparsity= 1 - in_o.count(0)/len(in_o), INNER = INNER)




				units = pe // INNER
				#powers[c] = res['Total_Pwr']['res'][-1] * units
				powers[c] = res['Total_Pwr']['res'][-1][-1] *units





				pass
			elif(component == "ACCUMULATOR"):	
	
				ap = AccumulatorPrimitive()
				res = ap.execute_testing(
					name = "Accumulator",
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['ACCUM_PREC']],
					"prec_out": [hh['ACCUM_PREC']],
					"terms": [1],
					"adderNType": [hh["TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					"in_0": [in_a],
					})
				units = pe // INNER
				powers[c] = res['Total_Pwr']['res'][-1][-1] *units

				pass	

			elif(component == "OUT_LOADER"):	
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				ratio = hh['LOAD_RATIO']

				res_r = SRAMBlock(h, hh, in_a, sparsity = OUT_SPARSITY, rw_mode = 0,mode = MODES)
				res_w = SRAMBlock(h, hh, in_a, sparsity = OUT_SPARSITY , rw_mode = 1,mode = MODES)

				res = NetworkBlock(h, hh,ratio, in_a, sparsity = OUT_SPARSITY,  fanout = 1,mode=MODES)
				units =  1/side_cycle * OUT_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}
				pass
			elif(component == "WEI_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				ratio = hh['LOAD_RATIO']

				#res_r, res_w = SRAMBlock(h, hh, in_w, mode = modes)
				res_r = SRAMBlock(h, hh, in_a, sparsity = b['WEI_SPARSITY'], rw_mode = 0,mode = MODES)
				res_w = SRAMBlock(h, hh, in_a, sparsity = b['WEI_SPARSITY'], rw_mode = 1,mode =MODES)


				res = NetworkBlock(h, hh,ratio, in_w, sparsity = b['WEI_SPARSITY'], mode =MODES, fanout = 1)
				units =  1/side_cycle * WEI_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	


				#print(res_r, res_w)
				#print(units)
				#input()	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}
				pass			
			elif(component == "ACT_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				ratio = hh['LOAD_RATIO']

				#res_r, res_w = SRAMBlock(h, hh, in_a,  mode = modes)
				res_r = SRAMBlock(h, hh, in_a, sparsity = b['ACT_SPARSITY'], rw_mode = 0,mode = MODES)
				res_w = SRAMBlock(h, hh, in_a, sparsity = b['ACT_SPARSITY'], rw_mode = 1,mode = MODES)


				res = NetworkBlock(h, hh,ratio, in_a, b['ACT_SPARSITY'],  fanout = 1, mode=MODES)
				units =  1/side_cycle * ACT_TILE*hh['PREC'] #fillter for now
				res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
				res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	
				powers[c] = {
					"SRAM": [res_r, res_w],
					"NETWORK": res}	

			elif(component == "WEI_PE_CAST"):
				ratio = min(hh['CAST_RATIO']		, pe//WEI_TILE)
					
				fanout = (pe//WEI_TILE)//ratio	
				#print("WEI_CAST")
				#print(fanout, ratio)
				#print(WEI_TILE)
				#input()
				res = MulticastBlock(h, hh, ratio, np.repeat(in_w,1), fanout = (pe//WEI_TILE)//ratio , mode = MODES)
				units = WEI_TILE*ratio
				res = res['Total_Pwr']['res'][-1][-1] *units 
				powers[c] = {"NETWORK": res}	
			elif(component == "ACT_PE_CAST"):
				ratio = min(hh['CAST_RATIO']		, pe//ACT_TILE)
				fanout = (pe//ACT_TILE)//ratio	
				#print("ACT_CAST")
				#print(fanout, ratio)
				#print(ACT_TILE)
				#input()
				res =MulticastBlock(h, hh, ratio, np.repeat(in_a, 1), fanout = (pe//ACT_TILE)//ratio ,mode=MODES)
				#(todos) worst case here, the fanout may have to be adjusted to optimize for diagonal systolic arrays
				units = ACT_TILE*ratio
				res = res['Total_Pwr']['res'][-1][-1] *units 
				powers[c] = {"NETWORK": res}	
				pass
	
			elif(component == "L2"):
				pwrs = []
				for busunit,in_0,tile,sparsity in [("ACT_LOADER", in_a,ACT_TILE,b['ACT_SPARSITY']), ("OUT_LOADER", in_o,OUT_TILE, OUT_SPARSITY), ("WEI_LOADER", in_w,WEI_TILE, b['WEI_SPARSITY'])]:

					if((hh['BIT_LEN']//hh['PREC']) > tile):
						ratio = (hh['BIT_LEN']//hh['PREC']) // tile
					else:
						ratio = -tile //( hh['BIT_LEN']//hh['PREC'])

					if(ratio < 0):
						side = abs(ratio)
					else:
						side = 1/abs(ratio)
					#hh['PREC'] = h['WEI_PREC']
					#res_r, res_w = SRAMBlock(h, hh, in_0, mode = modes)

					res_r = SRAMBlock(h, hh, in_a, rw_mode = 0,sparsity=sparsity,mode=MODES)
					res_w = SRAMBlock(h, hh, in_a, rw_mode = 1,sparsity=sparsity,mode=MODES)


					units =  1/side * tile #fillter for now
					#print("L2")
					#print(res_r, res_w)
					#print('ratio',ratio)
					#print('units',units)
					#print('side',side)
					#print('tile',tile)
					#input()
					res_r = res_r['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]
					res_w = res_w['Total_Pwr']['res'][-1][-1] *units / hh['SRAM_SIZE'][0]

			
					res = NetworkBlock(h, hh,ratio, in_0, sparsity = sparsity,  fanout = 1,mode=MODES)

					res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	

					
					pwrs.append((res_r, res_w,res))	
				powers[c] = {
					"BUS": pwrs}

				pass
	
		#print(bb,cycles, max([cycles[t] for t in cycles]))
		#print(bb, hp)
		#print(bb)
		#pprint(powers)# max([cycles[t] for t in cycles]))
		#print(bb, hp)
		all_powers[bb] = powers
	return all_powers


	return powers

	pass

def SystolicGoldenModel(hardware_config, benchmark):
	pass




#Simple Timing simulator
def SystolicTimer(hardware_config, benchmark   ):
	cycles_list = []
	h = hardware_config["GENERAL"]

	pe = h['TI']*h['TN']*h['TKX']*h['TKY']


	hp = {}

	
	for bb in benchmark:
		b = benchmark[bb]
		cycles = {}

		if(not  h['INTER_PE_X']  ):
			X_CYCLES =  (b['X']+h['TX']+h['TKX']-1)//(h['TX']+h['TKX']-1)  * (b['KX']+h['TKX']-1)//h['TKX'] //b["STRIDE"]
			X_TILE = (h['TX'] + h['TKX'] - 1)
		else:
			X_CYCLES =   (b['X']+h['TX']-1)//h['TX'] //b['STRIDE']
			X_TILE = h['TX']

		if(not  h['INTER_PE_Y']  ):
			Y_CYCLES =  (b['Y']+h['TY']+h['TKY']-1)//(h['TY']+h['TKY']-1)//b['STRIDE']  * (b['KY']+h['TKY']-1)//h['TKY'] 
			Y_TILE = (h['TY'] + h['TKY'] - 1)
		else:
			Y_CYCLES =   (b['Y']+h['TY']-1)//h['TY'] //b['STRIDE']
			Y_TILE = h['TY']

		PE_CYCLES = (b['X']+h['TX']-1)//b['STRIDE']//h['TX']   *     (b['Y']+h['TY']-1)//b['STRIDE']//h['TY']  *\
			(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
			 (b['I']+h['TI']-1)//h['TI']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			




		WEI_TILE = h['TN']*h["TKX"]*h["TKY"]*h["TI"]
		ACT_TILE = h['TB']*X_TILE*Y_TILE*h["TI"]
		OUT_TILE = h['TB']*h["TX"]*h["TY"]*h["TN"]

		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 
	

		INNER = h["TKX"]*h["TKY"]*h["TI"]

		ACC_CYCLES = (b['X']+h['TX']-1)//h['TX']   *     (b['Y']+h['TY']-1)//h['TY']  *\
			 (b['N']+h['TN']-1)//h['TN']  *\
			 (b['B']+h['TB']-1)//h['TB'] 			

		#power cost, there is an added Parallel2Serial unit
		if( h['INTER_PE_X']  ):
			X_CYCLES =  (b['X']+h['TX']+h['TKX']-1)//(h['TX']+h['TKX']-1)  * (b['KX']+h['TKX']-1)//h['TKX'] 
		else:
			X_CYCLES =   (b['X']+h['TX']-1)//h['TX'] 

		if( h['INTER_PE_Y']  ):
			Y_CYCLES =  (b['Y']+h['TY']+h['TKY']-1)//(h['TY']+h['TKY']-1)  * (b['KY']+h['TKY']-1)//h['TKY'] 
		else:
			Y_CYCLES =   (b['Y']+h['TY']-1)//h['TY'] 




		ACT_CYCLES = X_CYCLES  *  Y_CYCLES * \
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['B']+h['TB']-1)//h['TB'] 			

		
		WEI_CYCLES = 	(b['KX']+h['TKX']-1)//h['TKX']  *  	(b['KX']+h['TKX']-1)//h['TKX']*\
					 (b['I']+h['TI']-1)//h['TI']  *\
					 (b['N']+h['TN']-1)//h['TN'] 
		#print(WEI_CYCLES)
	
		for component in hardware_config:
			c = component
			hh = hardware_config[component] 
			#print(bb,component)
			if(component == "PE_ARRAY"):
				side = hh["MULT_SIDE"]
				radix = hh['MULT_RADIX']
				ratio = np.log2(radix)
				#print(radix, ratio)
				if(side == "weight"):
					ratio = min(ratio, hh["WEI_PREC"])

					side_cycle = hh["WEI_PREC"]/ratio
					side_bits = 1 - b["WEI_BIT_ZERO"]/hh['WEI_PREC']
				else:
					ratio = min(ratio, hh["ACT_PREC"])


					side_cycle = hh["ACT_PREC"]/ratio				
					side_bits = 1 - b["ACT_BIT_ZERO"]/hh['ACT_PREC']
				#print(b["WEI_BIT_ZERO"],hh['WEI_PREC'],side_bits, side_cycle)
		
				if(hh["MULT_TYPE"] == "HighRadixMultiplier"):
					cycles[c] = PE_CYCLES * side_cycle
				elif(hh["MULT_TYPE"] == "BitSerialMultiplier"):
					cycles[c] = PE_CYCLES * side_cycle* side_bits
				#print(cycles)	
				print(PE_CYCLES, side_cycle)
				#input()

				#exit()
			
			elif(component == "ADDER_TREE"):


				if(hh["ADDERN_TYPE"] in [ "AddTreeN", "SimpleAdderN"]):
					side_cycle = 1
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					side_cycle = INNER
				else:
					print("invalid ADDERN_TYPE", hh["ADDERN_TYPE"])
					exit()
				print(PE_CYCLES, side_cycle)
				#input()
	
				cycles[c] = PE_CYCLES * side_cycle
	
				pass
			elif(component == "ACCUMULATOR"):
				cycles[c] = PE_CYCLES 
	
				pass	

			elif(component == "OUT_LOADER"):	
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
				cycles[c] = ACC_CYCLES*side_cycle
				pass
			elif(component == "WEI_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	

				cycles[c] = WEI_CYCLES*side_cycle
				hp[c] = 1/side_cycle * WEI_TILE*hh['PREC']
				pass			
			elif(component == "ACT_LOADER"):
				if(hh['LOAD_RATIO'] < 0):
					side_cycle = abs(hh['LOAD_RATIO'])
				else:
					side_cycle = 1/abs(hh['LOAD_RATIO'])
	
	
				cycles[c] = ACT_CYCLES* side_cycle
				hp[c] = 1/side_cycle * WEI_TILE*hh['PREC']
	
				pass
			elif(component == "WEI_PE_CAST"):
				cycles[c] = PE_CYCLES*hh['CAST_RATIO']		
				pass
			elif(component == "ACT_PE_CAST"):
				cycles[c] =PE_CYCLES*hh['CAST_RATIO']		
				pass
	
			elif(component == "L2"):
				#if(hh['LOAD_RATIO']< 0):
				#	side_cycle = abs(hh['LOAD_RATIO'])
				#else:
				#	side_cycle = 1/abs(hh['LOAD_RATIO'])

				cycles[c] = 0
				pwrs = []
				for busunit,tile,cycles_0 in [("ACT_LOADER", ACT_TILE, ACT_CYCLES), ("OUT_LOADER", OUT_TILE,ACC_CYCLES), ("WEI_LOADER", WEI_TILE, WEI_CYCLES)]:

					#print(hh['BIT_LEN'], hh['PREC'], tile)
					if(hh['BIT_LEN']//hh['PREC'] > tile):
						ratio = hh['BIT_LEN']//hh['PREC'] // tile
					else:
						ratio = -tile //( hh['BIT_LEN']//hh['PREC'])

					if(ratio < 0):
						side = abs(ratio)
					else:
						side = 1/abs(ratio)
					cycles[c] += cycles_0*side	
			
					#cycles[c] = WEI_CYCLES*side_cycle + ACT_CYCLES*side_cycle + ACC_CYCLES*side_cycle		
		#print(cycles)	
		#print(bb,cycles, max([cycles[t] for t in cycles]))
		#print(bb, hp)
		cycles_list.append(cycles)


	return cycles_list

if __name__ == "__main__":
	
	PREC = 8
	ACT_PREC = 8
	WEI_PREC = 8
	SystolicConv_0 = {
		"GENERAL": {"LOOP_ORDER": ["B","I","X","Y","KX","KY","N"],"TB": 1,"TN": 16,"TI": 16,"TX": 1,"TY": 1,"TKX": 1,"TKY": 1,"CLOCK": 1,"cap_load": 0.1,"tech":"tsmc40","INTER_PE_X": False,"INTER_PE_Y": False, "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC},
		"PE_ARRAY": {"ACT_PREC": ACT_PREC,"WEI_PREC": WEI_PREC,"MULT_TYPE": "BitSerialMultiplier","MULT_SIDE": "input","MULT_RADIX": 1<<8,"MULT_CORE_ADDER_TYPE": "SimpleAdder2",},
		"ADDER_TREE":{"ADDERN_TYPE": "AddTreeN","CORE_ADDER_TYPE": "SimpleAdder2","PREC": ACT_PREC+WEI_PREC,"OUT_PREC": ACT_PREC+WEI_PREC,"DEPTH": 1, },	
		"ACCUMULATOR": {"TYPE": "AccumulatorN","CORE_ADDER_TYPE": "SimpleAdder2","ACCUM_PREC": ACT_PREC+WEI_PREC,},
		"WEI_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": WEI_PREC,},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC+WEI_PREC,},
		"WEI_PE_CAST":{"CAST_RATIO": 1,"PREC": WEI_PREC,"NETWORK_TYPE": "Mux",},
		"ACT_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	SparseConv_0 = {}
	WinogradConv_0 = {}
	MaxPool_0 = {
		"GENERAL": {"LOOP_ORDER": ["B", "N", "X", "Y", "KX", "KY"],"TB":1,"TN":16,"TI":16,"TX":1,"TY":1,"TKX":1,"TKY":1,"CLOCK":1,"cap_load":0.1,"tech":"tsmc40"},
		"MAX_TREE":{"TYPE": "MaxTreeN","CORE_TYPE": "SimpleMax2","PREC": ACT_PREC,"OUT_PREC": ACT_PREC,"DEPTH": 1, },	
		"MAX_ACCUM": {"TYPE": "AccumulatorN","CORE_ADDER_TYPE": "SimpleMax2","ACCUM_PREC": ACT_PREC,},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"ACT_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	AvgPool_0 = {
		"GENERAL": {"LOOP_ORDER": ["B", "N", "X", "Y", "KX", "KY"],"TB":1,"TN":16,"TI":16,"TX":1,"TY":1,"TKX":1,"TKY":1,"CLOCK":1,"cap_load":0.1,"tech":"tsmc40"},
		"ADDER_TREE":{"TYPE": "AdderTreeN","CORE_TYPE": "SimpleAdder2","PREC": ACT_PREC,"OUT_PREC": ACT_PREC*2,"DEPTH": 1, },	
		"ACCUM": {"TYPE": "AccumulatorN","CORE_ADDER_TYPE": "SimpleAdder2","ACCUM_PREC": ACT_PREC*2,},
		"ACT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"ACT_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	Elementwise_0 = {
		"GENERAL": {"LOOP_ORDER": ["B", "N", "X", "Y", "KX", "KY"],"TB":1,"TN":16,"TI":16,"TX":1,"TY":1,"TKX":1,"TKY":1,"CLOCK":1,"cap_load":0.1,"tech":"tsmc40"},
		"ADDER_TREE":{"TYPE": "AdderTreeN","CORE_TYPE": "SimpleAdder2","PREC": ACT_PREC,"OUT_PREC": ACT_PREC*2,"DEPTH": 1, },	
		"ACCUM": {"TYPE": "AccumulatorN","CORE_ADDER_TYPE": "SimpleAdder2","ACCUM_PREC": ACT_PREC*2,},
		"ACT_1_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"ACT_2_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},	
		"OUT_LOADER": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","TOTAL_SIZE" : 48000,"NETWORK_TYPE": "Mux","LOAD_RATIO": -32,"PREC": ACT_PREC,},
		"ACT_2_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"ACT_1_PE_CAST": {"CAST_RATIO": 4,"PREC": ACT_PREC,"NETWORK_TYPE": "Shift",},
		"L2": {"SRAM_SIZE": [16, 256],"SRAM_TYPE": "Reg","BIT_LEN": 512,"PREC": PREC,},
	}

	accelerator_core = {
		#"SparseConv_0": SparseConv_0,
		#"WinogradConv_0": WinogradConv_0,
		"SystolicConv_0": SystolicConv_0,	
		"MaxPool_0": MaxPool_0,
		"AvgPool_0": AvgPool_0,
		"Elementwise_0": Elementwise_0,
	}


	def Bottleneck(n,X,N,I,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO):
		Y = X
		return {
		f"Conv{n}_1": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_2": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_3": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_4": {
			"X":X,"Y":X,"N":I,"I":I,"KX":3,"KY":3,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Element{n}_4": {
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		f"Conv{n}_5": {
			"X":X,"Y":Y,"N":N,"I":I,"KX":1,"KY":1,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},

		}


	B = 4
	benchmark = {
		"Conv1": {
			"X":224,"Y":224,"N":64,"I":3,"KX":7,"KY":7,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		"AvgPool1": {
			"X":7,"Y":7,"N":1024,"KX":7,"KY":7,"B":B,"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
		"MaxPool1": {
			"X":112,"Y":112,"N":64,"KX":3,"KY":3,"B":B,"STRIDE": 2,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},

		"FC": {
			"X":1,"Y":1,"N":1000,"I":1024,"KX":1,"KY":1,"B":B,
			"STRIDE": 1,	
			"WEI_SPARSITY": WEI_SPARSITY,"ACT_SPARSITY": ACT_SPARSITY,
			"WEI_BIT_ZERO": WEI_BIT_ZERO,"ACT_BIT_ZERO": ACT_BIT_ZERO,			
		},
	}

	benchmark.update(Bottleneck(2,56,64,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(3,56,256,64,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(4,28,512,256,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)
	benchmark.update(Bottleneck(5,14,1024,512,B, WEI_SPARSITY, ACT_SPARSITY, WEI_BIT_ZERO, ACT_BIT_ZERO)	)

	def ArchTimer(core, mapping, benchmarks=benchmark, FILTER=[]):
		global GLOBAL_RUNS
		global START_RUN
		global COMPONENT_SELECT
		#print(FILTER[0])
		#print(COMPONENT_SELECT)
		#input()

		if(len(COMPONENT_SELECT) != 0 and FILTER[0] not in COMPONENT_SELECT):
			return -1#continue
		GLOBAL_RUNS += 1
		if(START_RUN > GLOBAL_RUNS):
			return
		#Get Area	
		#Get Timing and Power
		res = {}
		for benchmark in benchmarks:
			unit = mapping[benchmark].split("_")[0]
			if(unit == "SystolicConv"):
				base_hardware_config = core[mapping[benchmark]]	

				#filtering if necessary
				if(len(FILTER) == 0):
					pass
				else:
					base_hardware_config = {k: v for k, v in base_hardware_config.items() if k in FILTER + ["GENERAL"]}

				#(TODOS), when there are multiple components in one-run, not FILTER
				GEN =  dict_values_to_str(base_hardware_config["GENERAL"])
				COMP = dict_values_to_str(base_hardware_config[FILTER[0]])

				base_file = valid_file(f"generated/DSE/FIRST_PASS/Conv/{UNIT}/{GEN}/{FILTER[0]}/{COMP}/{benchmark}.{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}")


				#base_file = valid_file(f"generated/DSE/FIRST_PASS/Conv/SystolicConv/{GEN}/{FILTER[0]}/{COMP}/{benchmark}.{WEI_SPARSITY}_{ACT_SPARSITY}_{WEI_BIT_ZERO}_{ACT_BIT_ZERO}")


				time_res = SystolicTimer(base_hardware_config, {benchmark:benchmarks[benchmark]})#, FILTER=FILTER)	
				time_file = valid_file(f"{base_file}.time")
				with open(time_file  , "w", encoding="utf-8") as f:
					json.dump(time_res, f, indent=4)

				#print("our model")
				#input()
				power_res = SystolicOurModel(base_hardware_config, {benchmark:benchmarks[benchmark]}, modes = MODES)# FILTER=FILTER)	
				our_file = valid_file(f"{base_file}.ourpower")
				with open(our_file  , "w", encoding="utf-8") as f:
					json.dump(power_res, f, indent=4)

				#baseline1(todos)
				#baseline2(todos)
				#print(f"done {benchmark} {FILTER[0]} {GEN} {COMP}")
				#res[benchmark] = {"time": time_res, "power": power_res}#unit_res, for sharing purposes
		
		#post analysis? sum up the total benchmark results?
		print(f"done {GLOBAL_RUNS} FULL LOAD {FILTER[0]} {GEN} {COMP}")
		#print(res)
		#input()	
		#exit()	
		return res

	#ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark)


	################################################################################
	# DSE 1st PASS - SYSTOLIC CONV UNIT
	################################################################################
	Conv_0 = "SystolicConv_0"
	MAPPING = {
		"Conv1": Conv_0,
		"MaxPool1": "MaxPool_0",
		"Conv2_1": Conv_0,
		"Conv2_2": Conv_0,
		"Conv2_3": Conv_0,
		"Conv2_4": Conv_0,
		"Element2_4": "Elementwise_0",
		"Conv2_5": Conv_0,
		"Conv3_1": Conv_0,
		"Conv3_2": Conv_0,
		"Conv3_3": Conv_0,
		"Conv3_4": Conv_0,
		"Element3_4": "Elementwise_0",
		"Conv3_5": Conv_0,	
		"Conv4_1": Conv_0,
		"Conv4_2": Conv_0,
		"Conv4_3": Conv_0,
		"Conv4_4": Conv_0,
		"Element4_4": "Elementwise_0",
		"Conv4_5": Conv_0,	
		"Conv5_1": Conv_0,
		"Conv5_2": Conv_0,
		"Conv5_3": Conv_0,
		"Conv5_4": Conv_0,
		"Element5_4": "Elementwise_0",
		"Conv5_5": Conv_0,	
		"AvgPool1": "AvgPool_0",
		"FC": Conv_0,	
	}


	LOOP_ORDERS = [
				["B", "N", "I", "KX", "KY", "X", "Y"],
					["B", "N", "Y", "X", "I", "KX", "KY"],
					["B", "Y", "X", "KY", "KX", "I", "N"],
					["B", "Y", "X", "KY", "KX", "N", "I"],	
					["KY", "KX", "I", "X", "Y", "B", "N"],
					["I", "N", "KX", "KY", "Y", "X", "B"],
					["I","B", "N", "X", "Y", "KX", "KY"],	
					["B",  "KX", "KY",  "N", "I","X", "Y", ],	
	]

	#tb,tn,  ti,tx, ty,tkx,tky in 	
	TILINGS = [#64 pe case
		[1, 8,   8,1,  1,  1,1],
		[1, 16,   16,1,  1,  1,1],
		[1, 12,   12,1,  1,  1,1],
		[1, 12,   8,1,  1,  1,1],	
		[1, 4,   4,2,  2,  1,1],
 		[1, 4,   4,1,  1,  2,2],
 		[1, 4,   4,2,  1,  2,1],
  		[1, 2,   2,2,  2,  2,2],
  		[2, 1,   2,2,  2,  2,2],
  		[1, 16,  1,1,  1,  1,1],  
  		[1, 4,  16,1,  1,  1,1],   
 	       	[1,8,  8,1,  1,  2,2],
        	[1,8,  8,1,  2,  1,2],	
        	[1,16,  4,1,  2,  1,2],	
       		[1,4,  16,2,  2,  1,2],			
        	[2,4,  8,2,  2,  1,1],			
	       	[2,2,  16,2,  2,  1,1],			
	       	[1,8,  32,1,  1,  1,1],			]

	#1st pass
	#hc = accelerator_core
	hc = accelerator_core["SystolicConv_0"]
	benchmark_filter = {}
	for bb in benchmark:
		b = benchmark[bb]		
		if("Conv" in bb):
			if(1):
				#if(b['KX'] == WinoConv_0["GENERAL"]["TKX"] and b['KY'] == WinoConv_0["GENERAL"]["TKY"]):
				#print(bb)
				#print(b)
				#input()
				benchmark_filter[bb] = b
	#exit()


	res = SystolicTimer(hc, benchmark_filter)#, FILTER=FILTER)	
	#power_res = SystolicOurModel(base_hardware_config, {benchmark:benchmarks[benchmark]}, modes = MODES)# FILTER=FILTER)	
	
	print(res)
	exit()			
	for clock in [1]:
		for cap_load in [0.1]:
			for ACT_PREC in ACT_PRECS:
				for WEI_PREC in WEI_PRECS:
					for inter_x in [True,False]:
						for inter_y in [True,False]:	
							for lp in LOOP_ORDERS:
								for tb,tn, ti,tx, ty,tkx,tky in TILINGS:		
									#GENERAL
									hc["GENERAL"]["LOOP_ORDER"] = lp
									hc["GENERAL"]["TB"] =  tb
									hc["GENERAL"]["TI"] =  ti
									hc["GENERAL"]["TN"] =  tn
									hc["GENERAL"]["TX"] =  tx
									hc["GENERAL"]["TY"] =  ty
									hc["GENERAL"]["TKX"] =  tkx
									hc["GENERAL"]["TKY"] =  tky			
			
									hc["GENERAL"]["INTER_PE_X"] =  inter_x
									hc["GENERAL"]["INTER_PE_Y"] =  inter_y
			
									#component-level pass
									#use accelerator_core as the base
									#1.1. PE_ARRAY
									FILTER = "PE_ARRAY"
									for MULT_TYPE in ["BitSerialMultiplier", "HighRadixMultiplier"]:
										for MULT_SIDE in ["weight", "input", "both"]:
											for MULT_CORE_ADDER_TYPE in ["SimpleAdder2"]:
												for RADIX in range(1,WEI_PREC):
													MULT_RADIX = 1<<RADIX
													hc[FILTER]['MULT_TYPE'] = MULT_TYPE
													hc[FILTER]['MULT_SIDE'] = MULT_SIDE
													hc[FILTER]['MULT_CORE_ADDER_TYPE'] = MULT_CORE_ADDER_TYPE
													hc[FILTER]['MULT_RADIX'] = MULT_RADIX
							
													ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])
										


									#1.2. ADDER_TREE
									FILTER = "ADDER_TREE"
									for ADDERN_TYPE in ["SimpleAdderN","AddTreeN", "Accumulator"]:
										for CORE_ADDER_TYPE in ["SimpleAdder2"]:
											hc[FILTER]['CORE_ADDER_TYPE'] = CORE_ADDER_TYPE
											hc[FILTER]['ADDERN_TYPE'] = ADDERN_TYPE
											ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])
										
									#1.3. ACCUMULATOR
									FILTER = "ACCUMULATOR"
									for CORE_ADDER_TYPE in ["SimpleAdder2","RCAAdder2"]:
										hc[FILTER]['CORE_ADDER_TYPE'] = CORE_ADDER_TYPE
										ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])
									#1.4-5-6 WEI_LOADER
									def LOADER(FILTER):										
										for SRAM_SIZE in [[16,256]]:
											for SRAM_TYPE in ["Reg"]:
												for NETWORK_TYPE in ["Mux", "Shift"]:
													for LOAD_RATIO in [-2,-32,-16, -8, -4, -2, 1, 2, 4]:			
														
														hc[FILTER]['NETWORK_TYPE'] = NETWORK_TYPE
														hc[FILTER]['LOAD_RATIO'] = LOAD_RATIO
	
														ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])

	
									LOADER("WEI_LOADER")
									LOADER("OUT_LOADER")
									LOADER("ACT_LOADER")						
									#1.7 BROADCASTING NETWORK
									def CASTING(FILTER):										
										for NETWORK_TYPE in ["Mux", "Shift"]:
											for CAST_RATIO in [1, 2, 4, 8, 16, 32]:			
												hc[FILTER]['NETWORK_TYPE'] = NETWORK_TYPE
												hc[FILTER]['CAST_RATIO'] = CAST_RATIO	
												ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])

									CASTING("WEI_PE_CAST")
									CASTING("ACT_PE_CAST")
							
									#1.8 L2
									FILTER = "L2"
									for BIT_LEN in [64, 128, 256, 512, 1024]:
										hc[FILTER]['BIT_LEN'] = BIT_LEN
										ArchTimer(core=accelerator_core,mapping=MAPPING, benchmarks=benchmark, FILTER=[FILTER])


	#END first pass of SYstolic Unit
	################################################################################
	# DSE 1st PASS - WINOGRAD CONV UNIT
	################################################################################
	

	################################################################################
	# DSE 1st PASS - SPARSE CONV UNIT
	################################################################################	





	################################################################################
	# DSE 2nd PASS - WINOGRAD CONV UNIT
	# 2nd pass
	# combinational recovery
	################################################################################
	









	#our power
	#SystolicTimer(base_hardware_config, benchmark)	
	#SystolicOurModel(base_hardware_config, benchmark)
	#input()
	#timing model
	#SystolicTimer(base_hardware_config, benchmark)
	
	
