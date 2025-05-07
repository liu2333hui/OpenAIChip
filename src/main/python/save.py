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


############################
from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive	
from power_models.MaxNPrimitive import MaxNPrimitive
	


############################




#general helper to generate cpp files
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



def log1p_inverse(x):
	return np.exp(x) - 1
		

def trace_file(num, TRACE_FILE, input_data, r = 1):
	
	for t in range(num):
		file_path = f"{TRACE_FILE}_{t}"#+str(t)
		result = []
		# 打开文件进行读取
		with open(file_path, 'r') as file:
			# 读取所有行
			lines = file.readlines()
			
			# 遍历每一行
			for line in lines:
				# 按空格分割每行数据
				row_data = [int(num) for num in line.strip().split()]
				#print(row_data)
				# 若结果列表为空，先初始化结果列表
				if not result:
					result = [[] for _ in range(len(row_data))]
				# 将每行数据添加到对应列的列表中
				for i, num in enumerate(row_data):
					result[i].append(num)
			#print(result)
		input_data[f"in_{t}"] = [re for re in result]
	return input_data
	

def bit_count_helper():
	return """
	// 计算单个数字的1的数量
	int countBits(int num) {
	    int count = 0;
	    while (num) {
	        num &= (num - 1); // 清除最低位的1
	        count++;
	    }
	    return count;
	}
	
	// 对整个数组进行计算，并保存到新数组
	int* countBitsInArray(int* arr, int size) {
	    // 创建一个新数组，用于存储每个数字的1的数量
	    int* bitCounts = new int[size];
	
	    // 遍历原始数组，计算每个数字的1的数量
	    for (int i = 0; i < size; i++) {
	        bitCounts[i] = countBits(arr[i]);
	    }
	
	    return bitCounts; // 返回新数组
	}
	"""

def cpp_read_file_helper():
    return '''
	#include <iostream>
	#include <fstream>
	#include <cstdlib>  // Pour malloc et free

	// Fonction pour lire un fichier et stocker les valeurs dans un tableau
	int* lireFichierEtRemplirTableau(const char* filename, int*size, int count) {
		std::ifstream file(filename);
		if (!file.is_open()) {
			std::cerr << "Erreur : Impossible d'ouvrir le fichier." << std::endl;
			return nullptr;
		}

		int count2 = 0;
		std::string line;
		while (std::getline(file, line)) {
			count2++;
		}

		file.clear();  // Effacer les flags d'erreur
		file.seekg(0); // Retourner au début du fichier

		int* array = (int*)malloc(count * sizeof(int));
		if (array == nullptr) {
			std::cerr << "Erreur : chec de l'allocation mémoire." << std::endl;
			file.close();
			return nullptr;
		}

		// Initialiser le tableau avec des zéros
		for (int i = 0; i < count; i++) {
			array[i] = 0;
		}

		int index = 0;
		while (std::getline(file, line)) {
			array[index] = std::stoi(line); // Convertir la ligne en entier
			index++;
		}

		file.close();

		*size = count2;

		return array;
	}
	'''


#run_it --> run the ./a.out
#need_trace --> this is for the acutal data, tracing like vcd
def generate_cpp(root,name,PARAMETERS,DATA,NETS, loop_order, valid_loops, tiling_pre = "CNN_T",hardware_config = {}, SIM_CYCLE_LIM = -1,hooks = {
				"core_before_outer_group_start": "",
				"core_before_inner_group_start": "",
				"core_after_inner_group_start":"",
				"core_after_data_fetch":"",
				"core_after_inner_group_end":"",
				"core_after_outer_group_end": ""
				}		, run_it=True, need_trace=False,	
debug = True
):
	PRE = tiling_pre
	OUTPUT_FILES = {}
	if True:
		NET_DATA = NETS
		#1. define files
		CPP_FILE = root + "/"+name+".cpp"
		name = name + "."+str(abs(SIM_CYCLE_LIM))
		for n in NET_DATA:
			OUTPUT_FILES[n] = {}
	
			#TOGGLING_FILE is the toggling data
			#TRACE_FILE is the actual data
			#JSON file is the json used by scala
			#POWER GOLDEN FILE is the golden ptpx
			#RUNTIME file is related with the timing
			#(todos) AREA file is related with the area
			NET_DATA[n]['TOGGLING_FILE'] = root + "/"+name+"."+n+".toggling"
			NET_DATA[n]['OUTPUT_TOGGLING_FILE'] = root + "/"+name+"."+n+".out.toggling"


	
			NET_DATA[n]['TRACE_FILE'] = root + "/"+name+"."+n+".trace"
			NET_DATA[n]['JSON_FILE'] = root + "/" + name + ".json"
			NET_DATA[n]['POWER_GOLDEN_FILE'] = root + "/" + name + ".golden"	
			NET_DATA[n]['RUNTIME_FILE'] = root + "/" + name + ".runtime"	

			#TOGLGING_FILE is INPUT_TOGGLING_FILE
			OUTPUT_FILES[n]['TOGGLING_FILE'] = root + "/"+name+"."+n+".toggling"
			OUTPUT_FILES[n]['OUTPUT_TOGGLING_FILE'] = root + "/"+name+"."+n+".out.toggling"



			OUTPUT_FILES[n]['TRACE_FILE'] = root + "/"+name+"."+n+".trace"
			OUTPUT_FILES[n]['JSON_FILE'] = root + "/" + name + ".json"
			OUTPUT_FILES[n]['POWER_GOLDEN_FILE'] = root + "/" + name + ".golden"	
			OUTPUT_FILES[n]['RUNTIME_FILE'] = root + "/" + name + ".runtime"	
	

		with open(CPP_FILE, "w") as f:
			f.write("#include <iostream>\n")
			f.write("#include <algorithm>\n")
			f.write(cpp_read_file_helper())
			f.write(bit_count_helper())
			f.write("int main(){\n")


			for p,v in PARAMETERS.items():
				f.write(f"int {p} = {v};\n")


			for i in DATA:
				name = i['name']
				filename = i['file']
				size = i['size']
				f.write(f"int {name}_size;\n")
				f.write(f"int* {name} = lireFichierEtRemplirTableau(\"{filename}\", &{name}_size, {size});\n") 	


			for nk in NET_DATA:
				n = NET_DATA[nk]
				net =nk.lower()# n["net"]
				units = n['units']
				prec = 1
				for i in n['input_bins']:
					prec *= i
				#prec = n['input_bins']
				num_inputs = len(n['input_bins'])
				
				for m in n['input_metadata']:
					
					f.write(f'''
					int {m}_{net}[{units}][{prec}];
					for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {prec}; j++) {{
							{m}_{net}[k][j] = 0;
					}}''')

				for m in n['output_metadata']:
					
					f.write(f'''
					int out_{m}_{net}[{units}][{prec}];
					for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {prec}; j++) {{
							out_{m}_{net}[k][j] = 0;
					}}''')


				groups = n['input_group']
				total_units = units * groups
				f.write(f'''
					int prev_{net}[{total_units}][{num_inputs}];
					int cur_{net}[{total_units}][{num_inputs}];
	
					for(int k = 0; k < {total_units}; k++)
						for (int j = 0; j < {num_inputs}; j++){{
						prev_{net}[k][j] = 0;
						cur_{net}[k][j] = 0;	
						}}
						
				''')
				if(debug):
					f.write(f'std::cout << "// Analyzing Workload" << std::endl;\n')
	
			# neck
			if True:
				#body 
				if(debug):
					f.write(f'std::cout << "// Analyzing Workload" << std::endl;\n')


			for n in NET_DATA:
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				group = n['input_group']
				num_inputs =len( n['input_bins'])
	
				TRACE_FILE = n['TRACE_FILE']#'#root+"/"+name+f".{net}.trace"
				#for i in range(num_inputs):#terms = FC_TI for adder tree	
				#	f.write(f'std::ofstream goldenOutFile_{net}_{i}("{TRACE_FILE}_{i}");\n');

			#3.5
			#variable init	
			f.write(f'int sim_cycles = -1;\n')	
			if(need_trace):
				for n in NET_DATA:
					net = n.lower()
					n = NET_DATA[n]
					units = n['units']
					
					accumulate = n['accumulate']
					num_inputs =len( n['input_bins'])
					group = n['input_group']
	
					if(SIM_CYCLE_LIM == -1):
						SIM_CYCLES = 88888888
					else:
						SIM_CYCLES = SIM_CYCLE_LIM
					f.write(f'int trace_store_{net}[{units}*{group}][{num_inputs}][{SIM_CYCLES}];\n')



			for n in NET_DATA:
				net = n.lower()#["net"].lower()
				f.write(f'int {net} = 0;\n')
				f.write(f'int group_{net} = 0;\n')
	

			#3.6
			#body
			#outer loop
			START = {}
			DEPTH = {}
			for v in valid_loops:
				START[v] = "0"
				DEPTH[v] = valid_loops[v]["LIM"]

			cnt = 0
			c = hardware_config
			for lp in loop_order:
				for v in valid_loops:
					if(lp == v and c[PRE+lp] != 0):
						f.write(f'''int prev_{v} = 0;\n''')

			for lp in loop_order:
				for v in valid_loops:
					if(lp == v and c[PRE+lp] != 0):
						start = START[lp]
						depth = DEPTH[lp]
						stride = valid_loops[v]["STRIDE"]

						f.write(f"for(int {lp} = {start}; {lp} < {start+'+'+depth}; \
						{lp} += {c[PRE+lp]}*{stride})"+"{\n")
						DEPTH[lp] = PRE+lp
						START[lp] = lp
						cnt += 1
		
			#self.outer_cnt = cnt
			#3.7
			#body
			#inner loop


		
			INNER_LOOPS = {}
			inner_cnt = 0
			for v in valid_loops:
				#variable = v[1:].upper() #TB, the B here
				variable = v
				lowv = variable.lower()
				lim = valid_loops[variable]["LIM"]
				stride = valid_loops[variable]["STRIDE"]
				INNER_LOOPS[variable] = f'''for (int {lowv} = {variable}; {lowv} < std::min({variable} + {c[PRE+variable]}*{stride}, {lim}); {lowv}+={stride}){{'''
				inner_cnt += 1
		
			print(INNER_LOOPS)	
			#3.8
			#interior core
			#dantian
			#(this part is the custom part that one should write, is functional too)
			CYCLE_LIMIT = SIM_CYCLE_LIM
			if(CYCLE_LIMIT == -1):
				pass
			else:
				if(debug):
					f.write('std::cout<< N << "\t" << B << "\t" << X<< "\t" <<Y<< "\t" << KX << "\t"<< KY << "\t" << std::endl;')
				f.write(f'''
				sim_cycles++;
				if(sim_cycles > {CYCLE_LIMIT})
					//break;
					goto done_sim;
				''')
		
			
			f.write(hooks['core_before_outer_group_start'])

			#if continuous_accumulate, this net will be not zero, but {net} = {net}
			for n in NET_DATA:
				net = n.lower()#net = n["net"].lower()
				n = NET_DATA[n]	
				group = n['input_group']
				#f.write(f"int accumulate_{net} = 0;\n")

				f.write(f'{net} = 0;\n')
				f.write(f'group_{net} = 0;\n')
	

			
	
		
			
			outer_loops = 0
			for v in valid_loops:
				group = valid_loops[v]['GROUP']
				if(group != "INNER"):
					#print(v)
					#print(inner_tiles)
					#print(inner_tiles[v])
					#print(INNER_LOOPS[inner_tiles[v]])
					f.write(INNER_LOOPS[v])
					outer_loops += 1
		



			f.write(hooks['core_before_inner_group_start'])
		
			#todos, local and global accumulate
			for n in NET_DATA:
				net = n.lower()#net = n["net"].lower()
				n = NET_DATA[n]	
				units = n['units'] // n['input_group']	
				group = n['input_group']
				f.write(f"int accumulate_{net}[{units}];\n")	
				f.write(f"int prev_accumulate_{net}[{units}];\n")
				f.write(f'''for (int idx = 0; idx < {units} ; idx++){{
					accumulate_{net}[idx] = 0;	
					prev_accumulate_{net}[idx] = 0;
					}}
					''')	
				
	
					
			inner_loops = 0
			for v in valid_loops:
				group = valid_loops[v]['GROUP']
				if(group == "INNER"):
					f.write(INNER_LOOPS[v])
					inner_loops += 1
		
			f.write(hooks['core_after_inner_group_start'])
		
			for d in DATA:
				name = d['name']
				size = d['size']
				indexing = d['indexing']
				if(debug):
					f.write('std::cout << "data_recovered" << std::endl;')
				f.write(f'''
				int {name}_idx = {indexing};
				int {name}_data = {name}[{name}_idx];
				''')
				
			f.write(hooks['core_after_data_fetch'])
					
			#update toggle bins and previous values
		
			for n in NET_DATA:
				net = n.lower()
				n = NET_DATA[n]
		
		
				#"in_function": "weight_data * input_data",
				#"post_function": "",#after accumulation
				#"accumulate": True
		
				units = n['units']
				accumulate = n['accumulate']
				accumulate_op = n['accumulate_op']
	
				num_inputs =len( n['input_bins'])
				prev_update = n.get('prev_update', '0')
				cur_update = n.get('cur_update', '0')
	
				output_update = n.get('output_update', '0')
				group = n['input_group']
	
				for m in n['input_metadata']:

					#meta_aggregate = n['input_metadata'][m]['aggregate']
					meta_update = n['input_metadata'][m]['update']
					f.write(f'''
					if(sim_cycles >= 0){{
					''')
					if(debug):
						f.write(f'''
					std::cout << "start" << std::endl;
					''')

					for jjj in range(num_inputs):#(int jjj = 0 ; jjj < {num_inputs}; jjj++)
						f.write(f'''
							cur_{net}[{net}][{jjj}] = {cur_update[jjj]};
						''')
	
					
					f.write(f'''
					//int update = update; 	
					//int prev_update = prev_{net}[{net}];
					//{m}_{net}[{net}][__builtin_popcount(update^prev_{net}[{net}])]++;					''') 
					f.write(f'''
					for(int jjj = 0; jjj < {num_inputs}; jjj++){{
						{m}_{net}[{net}][{meta_update}]++; 
					}}
					''')
					
					

				for jjj in range(num_inputs):#(int jjj = 0 ; jjj < {num_inputs}; jjj++)
					if(debug):
						f.write(f'std::cout <<"net\t"<< {net} << {prev_update[jjj]} << std::endl;')	
					f.write(f'''
							prev_{net}[{net}][{jjj}] = {prev_update[jjj]};
						''')
					#if(need_trace):
					#	f.write(f'goldenOutFile_{net}_{jjj} << {prev_update[jjj]}  << "\\n";\n');


				f.write(f'''
				}}
				''')


				#take care of output updating, if accumulating skip and move forward
				if(debug):
					f.write('std::cout << "start accum" <<std::endl;')
	
				f.write(f"int out_update = {output_update};\n")
	
				for m in n['output_metadata']:
					meta_update = n['output_metadata'][m]['update']
	
					if(accumulate):
						f.write(f"accumulate_{net}[group_{net}] = {accumulate_op};")	
					else:
						f.write(f'out_{m}_{net}[{net}][{meta_update}]++'); 	
						#what to do ?

						#for m in n['output_metadata']:
						#f.write("out_prev_{net}[{net}] = {output_update};")						
				if(debug):	
					f.write(f'''
					//std::cout << "done accum" <<std::endl;
					''')
				f.write(f'''
					{net} = ({net}+1);
				''')
		

			for i in range(inner_loops):
				f.write(f'}}\n')

			if(debug):	
				f.write(f'''
					std::cout << "done inner" <<std::endl;
					''')
	
			for m in n['output_metadata']:
				meta_update = n['output_metadata'][m]['update']
					
				if(accumulate):
					f.write(f'out_{m}_{net}[group_{net}][{meta_update}]++;')	

			if(debug):	
				f.write(f'''
					std::cout << "meta update" <<std::endl;
					''')
	
			#(todos) in the general case, the group can be inserted at any layer	
			f.write(f'''
				group_{net} = (group_{net}+1);
			''')
	
						
	
			f.write(hooks['core_after_inner_group_end'])
		
			

			for i in range(outer_loops):
				f.write(f'}}')


			if(need_trace):
				for n in NET_DATA:
					net = n.lower()
					n = NET_DATA[n]
					units = n['units']
					
					accumulate = n['accumulate']
					num_inputs =len( n['input_bins'])
					if(debug):	
						f.write(f'''
					std::cout << "trace starting" <<std::endl;
					''')
					
					for jjj in range(num_inputs):#(int jjj = 0 ; jjj < {num_inputs}; jjj++)	
						for g in range(group): 
							for u in range(units):
								#f.write(f'std::cout << {net} << "\t" << prev_{net}[{u}][{jjj}] << std::endl;')
								#f.write(f'//goldenOutFile_{net}_{jjj} << prev_{net}[{u}][{jjj}]  << "\\t";\n');
								#f.write(f'goldenOutFile_{net}_{jjj} << "testing" << "\\t";\n');
				
								f.write(f'trace_store_{net}[{u}+{units}*{g}][{jjj}][sim_cycles] = prev_{net}[{u}+{units}*{g}][{jjj}];\n')


	
								if(debug):	
									f.write(f'''
					std::cout << "trace {jjj}_{u+units*g}" <<std::endl;\n
					''')

	
						#f.write(f'//goldenOutFile_{net}_{jjj} << "\\n";\n');
						f.write(f'std::cout <<"traceoutput" << sim_cycles << "\\n";\n');
	
				if(debug):	
					f.write(f'''
					std::cout << "trace ok" <<std::endl;
					''')
	


		
			#f.write("sim_cycles += 1;\n")
	
			f.write(hooks['core_after_outer_group_end'])




			#tail 
			for i in range(cnt):
				f.write("}\n")
				
			#SAVE RESULTS
			f.write(f'''
done_sim:
std::cout << "// Saving Data" << std::endl;''')
			f.write(f'std::cout << "run simulation for " << sim_cycles << std::endl;\n')
			#f.write(f'''
			#	std::ofstream timeFile("{RUNTIME}");
			#	timeFile << sim_cycles << "\\n";
			#	timeFile.close();''')

			for n in NET_DATA:
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				units = n['units']
	
				group = n['input_group']
				TOGGLING_FILE = n['TOGGLING_FILE']#'#root+"/"+name+f".{net}.trace"
				OUTPUT_TOGGLING_FILE = n['OUTPUT_TOGGLING_FILE']
				
				units = n['units']//group
				prec = n['input_bins']
				prec = 1
				for i in n['input_bins']:
					prec *= i


				output_prec = n['output_bins']
				


				for m in n['output_metadata']:
					f.write(f'std::cout << "saving output toggles!" << std::endl;\n')
					f.write(f'std::ofstream OutputToggleOutFile_{m}_{net}("{OUTPUT_TOGGLING_FILE}");\n');	
					f.write(f'''
						//int {m}_{net}[{units}][{prec}];
						for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {output_prec}; j++) {{
						OutputToggleOutFile_{m}_{net}	<<	out_{m}_{net}[k][j] << "\\n" ;
					if(out_{m}_{net}[k][j] > 0){{
					//std::cout <<"OUT\t" << k << "\\t" <<j<<"\\t"	<<	out_{m}_{net}[k][j] << "\\n" ;
					}}
	
					}}\n''')


					
					f.write(f'OutputToggleOutFile_{m}_{net}.close();\n')


				#inputs now
				units = n['units']
				group = n['input_group']

				if(need_trace):
					f.write(f'std::cout << "saving input raw trace!" << std::endl;\n')

					#for (int g = 0 ; g < {group}; g++){{
					#	for (int jjj = 0; jjj < {num_inputs}; jjj++){{
					for g in range(group):
						for jjj in range(num_inputs):
							i = jjj + num_inputs*g
							f.write(f'''
					//int i = jjj + {num_inputs}*g;
				std::ofstream goldenOutFile_{net}_{i}("{TRACE_FILE}_{i}");	
	
						for(int s = 0; s < sim_cycles; s++){{
							//std::cout << s << "\\t";
							for (int u = 0; u < {units} ; u++){{

				//std::cout	<<trace_store_{net}[u+{units}*{g}][{jjj}][s] << "\\t"; 
				goldenOutFile_{net}_{i}	<<trace_store_{net}[u+{units}*{g}][{jjj}][s] << "\\t"; 
	
		}}
			goldenOutFile_{net}_{i} << std::endl;
	
	}}
		goldenOutFile_{net}_{i}.close();
	//std::cout << std::endl;
						''')

					"""
					for g in range(group):#terms = FC_TI for adder tree	
						for jjj in range(num_inputs):

							i = jjj + num_inputs*g
							f.write(f'std::ofstream goldenOutFile_{net}_{i}("{TRACE_FILE}_{i}");\n');	
							f.write(f'''
			for(int s = 0 ; s < sim_cycles; s++){{
	
				for(int u = 0; u < {units}; u++){{
			goldenOutFile_{net}_{i}	<<	trace_store_{net}[{u}+{units}*{g}][{jjj}][s] << "\\t"; 
			std::cout	<<s << "\\t"	<<trace_store_{net}[{u}+{units}*{g}][{jjj}][s] << "\\t"; 

				}}
			goldenOutFile_{net}_{i} << std::endl;
			std::cout << std::endl;
	
			}} ''')
						f.write(f'goldenOutFile_{net}_{i}.close();\n');	
					"""	



				for m in n['input_metadata']:
					
					f.write(f'std::cout << "saving input metadata toggles!" << std::endl;\n')
	

					f.write(f'std::ofstream ToggleOutFile_{m}_{net}("{TOGGLING_FILE}");\n');
	
					f.write(f'''
					//int {m}_{net}[{units}][{prec}];
					for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {prec}; j++) {{
					ToggleOutFile_{m}_{net}	<<	{m}_{net}[k][j] << "\\n" ;
					if({m}_{net}[k][j] > 0)
					std::cout << k << "\\t" <<j<<"\\t"	<<	{m}_{net}[k][j] << "\\n" ;
	
					}}''')

					f.write(f'ToggleOutFile_{m}_{net}.close();\n');
	

			for n in NET_DATA:
				net = n.lower()#n["net"]
				n = NET_DATA[n]
				group = n['input_group']
				TRACE_FILE = n['TRACE_FILE']#'#root+"/"+name+f".{net}.trace"
				num_inputs =len( n['input_bins'])
	
				#for i in range(num_inputs):#terms = FC_TI for adder tree	
				#f.write(f'goldenOutFile_{net}_{i}.close();\n');
				
				#f.write(f'ToggleOutFile_{net}_{i}.close();\n');


				#std::cout << "// Saving ADDER/ACCUM Data - DONE" << std::endl;	

			for d in DATA:
				name = d['name']
				size = d['size']
				indexing = d['indexing']
				f.write(f'''
					free({name});
					''')
	
			f.write(f'''return 0;
				}}''')
	


		#run it
		if(not IS_LINUX):
			os.system(f"g++ -O2 {CPP_FILE}") #make this as fast as possible please	
			os.system(".\\a.exe")
		else:
			os.system(f"g++ -O3 {CPP_FILE} -Wl,-rpath,/nfs/project/JayMok/power_experiments_xie/primitives")
	
		if(run_it):	
			os.system("./a.out")
		print(OUTPUT_FILES)
		return OUTPUT_FILES	



#general architecture
#Infer the PPA on a network
#1. Our Power Model w/ Toggle
#2. Baselines (Maestro, Accelergy, Aladdin, Interstellar)
#3. Ground Truth (scala + ptpx)
#Methodology:
#1. Generate trace and simulation output files
#2. Estimate the Power

#FLOW 1: PERF ARCH +GOLDEN+ ESTIMATE POWER+BASELINE
#1. ga = GenArch(haredware_configs)
#2. ga.gen_perf_trace(network_configs, SIM_CYCLES = 100) 
#3. ga.estimate_golden_pwr(nc)
#4. ga.estimate_our_pwr(nc)
#5. ga.estimate_b1_pwr(nc)
#6. ga.estimate_b2_pwr(nc) 

#FLOW 2: FOR DSE
#1. ga = GenArch(hardware_configs)
#2. ga.gen_perf_trace(network_configs, SIM_CYCLE = FULL)
#3. ga.estimate_our_pwr(network_configs)

#FLOW 3: LONG PERF ARCH, already run, changing updating our power model
#1. ga = GenArch(hardware_configs)
#2. ga.estimate_our_pwr(network_configs)
class GeneralUnit:
	#hc is a specific hardware
	#nc is a specific network layer
	def __init__(self, hc, work_folder = "generated/Architecture/"):
		self.hc = hc
	def get_primitive_statistics(self):
		self.MODULES = {
		}
	#estimate powers
	def estimate_golden_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		print(traces)
		
		for blocks in traces:
			for module in blocks:
				print(module)
				print(blocks[module].keys())
				print(self.MODULES[module]['config'].keys())
				print(self.MODULES[module].keys())
					
				POWER_GOLDEN_FILE = blocks[module]["POWER_GOLDEN_FILE"]	
		
				CONFIG = self.hc
				CONFIG.update({
						"EDAVerification": True,
						"fanout_load": 0.0,
						"OutputPowerFile": blocks[module]["POWER_GOLDEN_FILE"]
				})
				CONFIG.update(self.MODULES[module]['config'])
					
				JSON_FILE = blocks[module]["JSON_FILE"]

				with open(JSON_FILE, "w") as json_file:
					json.dump(CONFIG, json_file, indent=4)  # indent 用于格式化输出		
					TRACE_FILE = blocks[module]["TRACE_FILE"]
					input_bins = self.MODULES[module]['input_bins']

					TRACE_FILES = " ".join([TRACE_FILE+"_"+str(i) for i in range(len(input_bins))])
					print("run sbt")

				primitive = self.MODULES[module]['config']['primitive']

				if(SIM_PARAMS["RUN_GOLDEN_SBT"]):
					print(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
					os.system(f'{SBT} "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
				#os.system(f'{SBT} "test:runMain adders.AdderNSpecFromFile {PE_TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')
			
				gold = pd.read_csv(POWER_GOLDEN_FILE,  delimiter="\t")
				#get relevant rows
				units = self.MODULES[module]['units']	
				rel = gold.tail(n=units)['Total_Pwr']
				print("GOLDEN POWER")
				print(rel, np.sum(rel))
				#print("GOLDEN ADDER TREE", np.sum(rel))
				at_golden_pwr = np.sum(rel)
				return {"unit_pwrs": rel, "total_pwrs": np.sum(rel), "avg_pwrs": np.sum(rel)/len(rel)}
					

				


	def estimate_our_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		return {}

	def estimate_our_pwr_v1(self, traces, network_layer,mapping, SIM_PARAMS):
		all_powers = {}
		for blocks in traces:
			for module in blocks:	
				primitive = self.MODULES[module]['config']['primitive']
			
				n = self.MODULES[module]	
				num_inputs = len(n['input_bins'])
	

				primitive_name = primitive.split(".")[1]

				#import importlib
				#module_name = f"power_models.{primitive_name}Primitive"
				
			#prim = importlib.import_module(module_name)
				#PRIM = getattr(prim, f"{primitive_name}Primitive")

				#from power_models.AdderNPrimitive import AdderNPrimitive
				#prim = PRIM()

				TRACE_FILE = blocks[module]["TRACE_FILE"]
				input_bins = self.MODULES[module]['input_bins']

				TRACE_FILES = " ".join([TRACE_FILE+"_"+str(i) for i in range(len(input_bins))])
				CONFIG = self.hc
				CONFIG.update({
						"EDAVerification": True,
						"fanout_load": 0.0,
						"OutputPowerFile": blocks[module]["POWER_GOLDEN_FILE"]
				})
				CONFIG.update(self.MODULES[module]['config'])
	
				if(primitive_name == "Multiplier2"):
					prim = Multiplier2Primitive()
				
				elif(primitive_name == "MaxN"):
					prim = MaxN()
				elif(primitive_name == "AdderN"):
					prim = AdderN()
	
	
				else:
					print("primitive ", primitive_Name, "no model")

				
				g,h,d = prim.get_features(primitive_name, out_features = ['Total_Pwr'])
	
				input_data = {}
				for gg in h+g:
					if("inv" in gg):
						ggg = gg.split("_")[1]	
						input_data[gg] = [1.0/CONFIG[ggg]]
						input_data[ggg] = [CONFIG[ggg]]


					else:
						input_data[gg] = [CONFIG[gg]]
	
							
				
				
				r = 5
				'''
				input_data = {
					"CLOCK": [CONFIG["CLOCK"]],
					"cap_load": [CONFIG["cap_load"]],
					"prec_in" : [prec],
					"prec_sum": [prec],
					"terms": [self.FC_TI]
				}
				'''	
					
				input_data = trace_file(num=num_inputs, TRACE_FILE=TRACE_FILE, input_data=input_data, r = r)

				if 'terms' not in input_data:
					input_data['terms'] = [num_inputs]
				#print(input_data)
				res = prim.execute_testing(
					name = primitive_name,
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = input_data
				)
				#print(res)
				at_estimate_pwr = res['Total_Pwr']['res']#['res_sum']
				#compress
				unit_pwrs = []
				#print(at_estimate_pwr.keys()	)
				sum_pwrs = []	
				for units in res['Total_Pwr']['res']:
					res = units
					#print(units)
					#print(res[0])
					avg_pwr = sum(res[0])/len(res[0])		
					sum_pwr = sum(res[0])
					unit_pwrs.append(avg_pwr)
					sum_pwrs.append(sum_pwr)
				total_pwr = sum(unit_pwrs)
				print(sum_pwrs)
				print(unit_pwrs, total_pwr)	
				#print(at_estimate_pwr)	
				return at_estimate_pwr


	def estimate_b1_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		return {}

	def estimate_b2_pwr(self, traces, network_layer,mapping, SIM_PARAMS):
		return {}
	

	#def gen_perf_trace(self, SIM_CYCLES = 8888888888888888):
	#	return {}	
	def infer(self, params):
		return {}
	def gen_perf_trace(self,network_layer,mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):
		work_folder = SIM_PARAMS.get("root", "generated/Architecture/GeneralUnit")
		import os
		path = work_folder #+ "/" + dict_to_str(self.hc)
		#os.makedirs(path, exist_ok=True)
		# 分割路径为每一层
		path_parts = path.split('/')
		
		# 逐层检查并创建目录
		current_path = ""
		for part in path_parts:
		    current_path = os.path.join(current_path, part) if current_path else part
		    if not os.path.exists(current_path):
		        os.mkdir(current_path)
		        print(f"目录已创建: {current_path}")
		    else:
		        print(f"目录已存在: {current_path}")
		self.root = path
		print("here")

	
		return {}	


class GeneralConvUnit(GeneralUnit):
	def gen_perf_trace(self,network_layer,mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):
		super().gen_perf_trace(network_layer, mapping, SIM_PARAMS)


		params = {
		"in_channels": layer._in_channels,
					"out_channels": layer._out_channels,
					"kernel_size": layer._kernel_size,
					"stride": layer._stride,
					"padding": layer._padding,
					"input_data": input_data,
					"weight": layer.weight,
					"out_data": out_data,
				}
		results = self.infer(params)
	

class GeneralMaxPoolUnit(GeneralUnit):
	def gen_perf_trace(self,network_layer, mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):	
		super().gen_perf_trace(network_layer, mapping, SIM_PARAMS)


		layer = network_layer['layer']
		input_data = network_layer['input_data']
		output_data = network_layer['input_data']
		#print(layer)	
		#print(dir(layer))
	
		params = {
					"kernel_size": layer.ksize,
					"stride": layer.stride,
					"padding": layer.padding,
					"input_data": input_data,
					"out_data": output_data,
					"SIM_PARAMS": SIM_PARAMS,
				}
		
		results = self.infer(params)
	
		return results


class GeneralLinearUnit(GeneralUnit):
	def gen_perf_trace(self,network_layer,mapping, SIM_PARAMS = { "SIM_CYCLES": -1,  } ):

		super().gen_perf_trace(network_layer, mapping, SIM_PARAMS)

		layer = network_layer['layer']
		input_data = network_layer['input_data']
		output_data = network_layer['input_data']
	
		
		params = {
			"in_features": layer.weight.shape[1],
			"out_features": layer.weight.shape[0],
			"input_data": input_data,
			"weight": layer.weight,
			"out_data": output_data,
			"SIM_PARAMS": SIM_PARAMS
		}
		results = self.infer(params)		
		return results

###################################################


#A multi-dataflow architecture
#like NVDLA, Thinker, EyerissV2...
#DianNao
class MultiFlowArch:
	
	def __init__(self, hardware_config):
		self.hc = hardware_config
		

	def gen_perf_trace(self,intermediate_outputs, flow_mapper, skips=[]):
		return {}	


#CONV converted to FC, has POOL, RELU, Simple Activations, Element-wise addition
#can do AlexNet, Resnet
#Other types of Conv?

class SimpleArchV2(SingleFlowArch):
	def infer_fc(self, p):
		return []
	def infer_maxpool(self,p ):
		return []
	def infer_avgpool(self, p):
		return []
	def infer_eltadd(self, p):
		return []
	def infer_conv(self, p):
		return []	
	def infer_fused_conv_pool_act(self, p):
		return []
	def infer_activation(self, p):
		return []

	#statistics on the hardware used
	#based on the hardware parameters
	def get_primitive_statistics(self):

		primitives = []
		primitives.append
			

		return {
		}
class SystolicConv(GeneralConvUnit):
	pass

class WinogradConv(GeneralConvUnit):
	pass

class SparseConv(GeneralConvUnit):
	pass


class DirectConv(GeneralConvUnit):
	def infer(self, params):
		print(params)
		return {}
class SparseLinear(GeneralLinearUnit):
	def infer(self, params):
		print(params)
		return {}
#################################################


#given a network, mapping, hardware
#output the trace and ppa
class GeneralArch:
	def __init__(self, hc, nc, mapping):
		self.hc = hc
		self.nc = nc
		self.mapping = mapping
	
	def get_hardware_statistics(self):
		return {}

	def gen_perf_trace_full(self,intermediate_outputs,SIM_CYCLES):
		self.SIM_CYCLES = SIM_CYCLES
		for layer_name, layer, input_data, out_data in intermediate_outputs:
			if isinstance(layer, nn.Conv2D):
				params = {
					"in_channels": layer._in_channels,
					"out_channels": layer._out_channels,
					"kernel_size": layer._kernel_size,
					"stride": layer._stride,
					"padding": layer._padding,
					"input_data": input_data,
					"weight": layer.weight,
					"out_data": out_data,
				}
				results = self.infer_conv(params)
			elif isinstance(layer, nn.Linear):
				params = {
					"in_features": layer.weight.shape[1],
					"out_features": layer.weight.shape[0],
					"input_data": input_data,
					"weight": layer.weight,
					"out_data": out_data
				}
				results = self.infer_fc(params)	
			elif isinstance(layer, nn.MaxPool2D):
				print(input_data, out_data)
				print(layer)
				print("todos - maxpool")
				#results = self.infer_maxpool(params)	
			elif isinstance(layer, nn.AvgPool2D):
				print(input_data, out_data)
				print(layer)
				print("todos - maxpool")	
				#results = self.infer_avgpool(params)
			elif isinstance(layer, nn.ReLU) or isinstance(layer, nn.BatchNorm2D) or isinstance(layer, nn.Sigmoid):
				print("do ReLU")
				#results = self.infer_activations(params)		

			#self.save_results(layer_name,results)
			print(f"arch sim of Layer: {layer_name}")



if __name__ == "__main__":

	hc = {
		"conv1": {
			
		},
	}
	ga = SingleFlowArch(hc)
	#FLOW 1: PERF ARCH +GOLDEN+ ESTIMATE POWER+BASELINE
	#simple 
	#for layer_name, layer, input_data, out_data in intermediate_outputs:
	network_configs = [
		["cnn1", nn.Conv2D(
 		   in_channels=3,  # Input channels, for example, RGB images have 3 channels
		    out_channels=16,  # Output channels
		    kernel_size=3,  # Convolutional kernel size of 3x3
		    stride=1,  # Stride of 1
		    padding=1  # Padding of 1
		  ), np.random((8, 3, 16, 16)), np.random((16, 3, 3, 3)) , np.random((8, 16, 14, 14))],
	]
	#mapping between network_configs layer and a dataflow
	mapping = {
		"cnn1": "conv1",
	}
	nc = network_configs
	ga.gen_perf_trace(hc, nc, mapping, SIM_CYCLES = 100) 
	ga.estimate_golden_pwr(nc)
	ga.estimate_our_pwr(nc)
	ga.estimate_b1_pwr(nc)
	ga.estimate_b2_pwr(nc)

#FLOW 2: FOR DSE
#1. ga = GenArch(hardware_configs)
#2. ga.gen_perf_trace(network_configs, SIM_CYCLE = FULL)
#3. ga.estimate_our_pwr(network_configs)

#FLOW 3: LONG PERF ARCH, already run, changing updating our power model
#1. ga = GenArch(hardware_configs)
#2. ga.estimate_our_pwr(network_configs)


