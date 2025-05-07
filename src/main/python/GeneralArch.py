
#Helpers
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
				# 若结果列表为空，先初始化结果列表
				if not result:
					result = [[] for _ in range(len(row_data))]
				# 将每行数据添加到对应列的列表中
				for i, num in enumerate(row_data):
					result[i].append(num)
		input_data[f"in_{t}"] = [r*re for re in result]
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


class GeneralArch:
    def __init__(self, config, model_name = "Testing", run_cpp = True, np_save = True,
		RUN_PE = True, RUN_WEI_BUFFERS = True, RUN_ACT_BUFFERS = True,
		RUN_MODEL = True,
		RUN_GOLDEN=True,
		SIM_CYCLES = 88888888888888, #some gigantic number
		Randomize = False, Wei_Sparse = 0.5, Act_Sparse = 0.5,
		EDAVerification = False,

		RUN_L1 = True,
		RUN_L2 = True,
		RUN_ADDERS = True,

		logs = "logs2",
		
		):
        pass
    

class ComponentModel:
	def __init__(self):
		pass

	def infer(self, components = ["pe", "psum", "out"]):
		#1. file
		CPP_FILE = self.root + "/" + self.name + ".cpp"
		OUT_FILE = self.root + "/" + self.name + ".out"
		TRACE_FILE = self.root+"/"+name+f".{TYPE_NAME}.trace"
		JSON_FILE = self.root+"/"+name+f".{TYPE_NAME}.json"
		POWER_GOLDEN_FILE = self.root+"/"+name+f".{TYPE_NAME}.golden"
		RUNTIME = self.root+"/"+name+".runtime.txt" #cycles

		#2.0 Params exterior the cpp
		## need to multiply terms and collect them together to generate
		TYPE_NAME = "ADDER_ACCUM"
		buffer_loop_order = self.FC_LOOP_ORDER

		NEED_TOGGLES = 1
		NEED_BITS = 0

		#2.1 Params within the cpp
		PARAMETERS =  {
			"BAT": 123,
			"OUT": 321,
			"IN": 123
		}

			# int w_idx = i*{OUT} + n;
			# int i_idx = b*{BAT} + i;
		DATA = [
			{
			"name": "weight",
			"file": "my_weight_file.txt",
			"size": "OUT*IN",
			"indexing": "i*OUT + n"
		},
		{
				"name": "input",
				"file": "my_input_file.txt",
				"size": "BAT*IN",
				"indexing": "b*BAT + i"
			},
		# {
				# "name": "output",
				# "file": "my_output"file.txt"
				# "size": "BAT*OUT"
		# 	}

		]


		outer_loop = ["I", "B", "N"]
		inner_tiles = ['TI','TB', 'TN']	
		prec = 32#2*(self.WEI_PREC + self.ACT_PREC)

		#3. main file
		with open(TOGGLE_FILE, "w") as f:
			#3.1. common
			f.write("#include <iostream>\n")
			f.write("#include <algorithm>\n")
			f.write(cpp_read_file_helper())
			f.write(bit_count_helper())
			f.write("int main(){\n")
			
			
			#3.2. 读数据
			for p,v in PARAMETERS.items():
				f.write(f"int {p} = {v};\n")

			for i in DATA:
				name = i['name']
				filename = i['file']
				size = i['size']
				f.write(f"int {name}_size;\n")
				f.write(f"int* {name} = lireFichierEtRemplirTableau(\"{filename}\", &{name}_size, {size});\n") 	

		#3.3. 保存的类别，如toggles或bits
		#neck
		#sum_toggle 可以之后获得，不难的
		NET_DATA = [
			{
				"net": "PE_OUT",
				"units":self.c["FC_PES"],
				"bins":self.c["ACT_PREC"]+self.c["WEI_PREC"], #usually related with precision
				"group":self.c["FC_TI"], #meaning the outputs are grouped by 16
				"metadata": ["toggle"], #"bits", "sum_toggle", 
				"reset_trigger": [], #none
			},
			{
				"net": "ACCUM_OUT",
				"units": self.c["FC_PES"]//self.c["FC_TI"],
				"bins": self.c["ACCUM_PREC"],
				"group":1,
				"metadata": ["toggle"],
				"reset_trigger": ["I"]
			},
		]

		for n in NET_DATA:
			net = n["net"]
			units = n['units']
			prec = n['bins']
			for m in n['metadata']:
					
				f.write(f'''
					int {m}_{net}[{units}][{prec}];
					for (int k = 0; k < {units}; k++)
						for (int j = 0; j < {prec}; j++) {{
							{m}_{net}[k][j] = 0;
					}}''')

			f.write(f'''
					int prev_{net}[{units}];
					for(int k = 0; k < {units}; k++)
						prev_{net}[k] = 0;
				''')

		#3.4 
		#Golden trace init
		#body 
		f.write(f'std::cout << "// Analyzing Workload" << std::endl;\n')
		if(self.RUN_GOLDEN):

			for n in NET_DATA:
				net = n["net"]
				group = n['group']
				TRACE_FILE = self.root+"/"+name+f".{net}.trace"
				for i in range(group):#terms = FC_TI for adder tree	
					f.write(f'std::ofstream goldenOutFile_{net}_{i}("{TRACE_FILE}_{i}");\n');

		#3.5
		#variable init
		#body
		f.write(f'int sim_cycles = -1;\n')	
		for n in NET_DATA:
			net = n["net"].lower()
			f.write('int {net} = 0;\n')

		#3.6
		#body
		#outer loop
		loop_order = ["B", "N", "I"]
		#use single letter to signify
		valid_loops = {
			"B": {
				"LIM": "BAT",
				"STRIDE": 1,
				"GROUP": "OUTER"
			},
			"I": {
				"LIM": "IN",
				"STRIDE": 1,
				"GROUP": "INNER", #meaning can be collected together in the sum
			},
			"N": {
				"LIM": "OUT",
				"STRIDE": 1,
				"GROUP": "OUTER"
			},

		}


		# B_DEPTH = "BAT"
		# N_DEPTH = "OUT"
		# I_DEPTH = "IN"
		# B_START = "0"
		# N_START = "0"
		# I_START = "0"

		START = {}
		DEPTH = {}
		for v in valid_loops:
			START[v] = "0"
			DEPTH[v] = valid_loops[v]["LIM"]

		cnt = 0
		PRE = "FC_T"


		for lp in loop_order:
			for v in valid_loops:
				if(lp[0] == v and self.c[PRE+lp] != 0):
					f.write(f'''int prev_{v} = 0;\n''')

		for lp in loop_order:
			for v in valid_loops:
				if(lp[0] == v and self.c[PRE+lp] != 0):
					start = START[lp[0]]
					depth = DEPTH[lp[0]]
					f.write(f"for(int {lp} = {start}; {lp} < {start+'+'+depth}; \
						{lp} += {self.c[PRE+lp]})"+"{")
					DEPTH[lp[0]] = PRE+lp
					START[lp[0]] = lp
					cnt += 1

		self.outer_cnt = cnt

		#3.7
		#body
		#inner loop

		b_up = ""
		i_up = ""
		n_up = ""

		INNER_LOOPS = {}
		inner_cnt = 0
		for v in inner_tiles:
			variable = v[-1].upper() #TB, the B here
			lowv = variable.lower()
			lim = valid_loops[variable]["LIM"]
			INNER_LOOPS[variable] = f'''for (int {lowv} = {variable}; \
					{lowv} < std::min({variable} + {self.c[PRE+variable]}, {lim}); {lowv}++){{'''
			inner_cnt += 1

		self.INNER_LOOPS = INNER_LOOPS
		self.inner_cnt = inner_cnt
		self.DATA = DATA
		# if("TB" in inner_tiles):
		# 	b_up = f'''for (int b = B; b < std::min(B + {self.FC_TB}, {BAT}); b++){{'''
		# if("TI" in inner_tiles):
		# 	i_up = f'''for (int i = I; i < std::min(I + {self.FC_TI}, {IN}); i++){{'''
		# if("TN" in inner_tiles):
		# 	n_up = f'''for (int n = N; n < std::min(N + {self.FC_TN}, {OUT}); n++){{'''

		#3.8
		#interior core
		#dantian
		#(this part is the custom part that one should write, is functional too)
		CYCLE_LIMIT = self.c["SIM_CYCLE_LIM"]
		f.write(f'''
			sim_cycles++;
			if(sim_cycles > {CYCLE_LIMIT})
				break;
			''')

		self.NET_DATA = NET_DATA
		self.PRE = PRE
		def inner_core(self, core="",
			core_init_hook = "",
			core_before_inner_group_hook = "int sum = 0;",
			core_after_inner_group_hook = "",
			core_after_data_fetch_hook =  ""):

			if(len(core) != 0):
				return core
			
			core = ""

			f'''
				//(todos) technically, psum does not go to 0 immediately
				// It will depend on different dataflows ...
				// etc.   TN TI TB, clearly accumulator will accumulate
				// next cycle, meaning the psum will not be reset yet
				// It will only reset on TIs
				// Maybe we let users define this part?
				'''

			#Method
			#1. Reset unit indices
			#1.1 initial hook, if any
			#2. before inner hook loop
			# an inner group hook is like TI, terms can be combined together
			#3. after inner hook loop
			# at the core now

			for n in self.NET_DATA:
				net = n["net"].lower()
				if("reset_trigger" not in n):
					f.write(f'{net} = 0;\n')
				else:
					for trigger in n.get("reset_trigger", []):
						f.write(f'if(prev_{trigger[-1]} != {trigger[-1]})\n\
							{net} = 0;\n\
							')
					f.write(f'''prev_{net.upper()} = {net.upper()};\n''')
				#maybe we shouldn't reset every cycle? some toggle? (done)

			core += core_init_hook

			outer_loops = 0
			for v in self.valid_loops:
				group = self.valid_loops[v]['group']
				if(group != "INNER"):
					core += self.INNER_LOOPS[inner_tiles[v]]
					outer_loops += 1

			core += core_before_inner_group_hook

			for n in self.NET_DATA:
				net = n["net"].lower()
				group = n['group']
				f.write("int accumulate_{net} = 0;\n")
			
			inner_loops = 0
			for v in self.valid_loops:
				group = self.valid_loops[v]['group']
				if(group == "INNER"):
					core += INNER_LOOPS[inner_tiles[v]]
					inner_loops += 1

			core += core_after_inner_group_hook

			for d in DATA:

				name = d['name']
				size = d['size']
				indexing = d['indexing']
				f.write(f'''
					int {name}_idx = {indexing};
					int {name}_data = {name}[{name}_idx];
					''')
			core += core_after_data_fetch_hook
			
			#update toggle bins and previous values

			for n in NET_DATA:
				net = n["net"].lower()
				f.write('int {net} = 0;\n')

				"in_function": "weight_data * input_data",
				"post_function": "",#after accumulation
				"accumulate": True
				update = n['update']

				f.write(f'''
					if(sim_cycles > 0)
						int update = {update}; 
						toggle_bins[{unit}][__builtin_popcount(update^prev_{net}[{net}])]++; 
						prev_{net}[{net}] = {update};
						''')
				
				if(accumulate):
					f.write(f"accumulate_{net} += prev_{net}[{net}]")
				
				f.write(f'''
						{net} = ({net}+1);
					''')

				for i in inner_loops:
					f.write(f'}}')

					# //(todos) may have to change, 1. not every cycle the same accumulator, 2. maybe there is resets as well
					int new_sum = prev_out[psum] + sum;
					if(sim_cycles > 0){{	
					toggle_psum[psum][__builtin_popcount(sum^prev_psum[psum])]++; 
					toggle_output[psum][__builtin_popcount(new_sum^prev_out[psum])]++;
					}}
					prev_psum[psum] = sum;	
					prev_out[psum] = new_sum;
					psum += 1;
				
				for i in outer_loops:
					f.write(f'}}')
				# 	{(len(inner_tiles)-1)*"}"}
				# ''')			

			# int w_idx = i*{OUT} + n;
			# int i_idx = b*{BAT} + i;
			# int wb = weight[w_idx];
			# int ib = input[i_idx];	

			return core

				
			if(sim_cycles > 0)						
			toggle_bins[pe][__builtin_popcount(wb^prev_val[pe])]++; 
			prev_val[pe] = wb*ib;
			sum += prev_val[pe];
			pe = (pe+1);
			}}
			//(todos) may have to change, 1. not every cycle the same accumulator, 2. maybe there is resets as well
			int new_sum = prev_out[psum] + sum;
			if(sim_cycles > 0){{	
			toggle_psum[psum][__builtin_popcount(sum^prev_psum[psum])]++; 
			toggle_output[psum][__builtin_popcount(new_sum^prev_out[psum])]++;
			}}

			prev_psum[psum] = sum;	
			prev_out[psum] = new_sum;
			psum += 1;
			{(len(inner_tiles)-1)*"}"}
			''')
				

				if(self.RUN_GOLDEN):
					for i in range(self.FC_TI):	
						for psum in range(self.FC_PES//self.FC_TI):
							pe = i + self.FC_TI*psum
							f.write(f'goldenOutFile_PE_{i} << prev_val[{pe}] <<"\t";\n')

	
					for i in range(1):
						for psum in range(self.FC_PES//self.FC_TI):
							f.write(f'goldenOutFile_OUT_{i} << prev_out[{psum}] <<"\t";\n')
							f.write(f'goldenOutFile_PSUM_{i} << prev_psum[{psum}] <<"\t";\n')
	

				if(self.RUN_GOLDEN):

					for i in range(self.FC_TI):	
						f.write(f'goldenOutFile_PE_{i} << "\\n";\n')	
					for i in range(1):	
						f.write(f'goldenOutFile_OUT_{i} << "\\n";\n')
						f.write(f'goldenOutFile_PSUM_{i} << "\\n";\n')

				
				for i in range(cnt):
					f.write("}\n")
				
				# tail
				#SAVE RESULTS
				# f.write(f'std::cout << "// Analyzing Workload - DONE" << std::endl;\n')
				# f.write(f'std::cout << "// Saving Data" << std::endl;\n')
				f.write(f'''
					std::ofstream timeFile("{RUNTIME}");
					timeFile << sim_cycles << "\\n";
					timeFile.close();					
	
					std::ofstream outFile_0("{PE_OUT_FILE}"); // 创建或覆盖文件
					std::ofstream outFile_2("{OUT_OUT_FILE}"); // 创建或覆盖文件
					std::ofstream outFile_1("{PSUM_OUT_FILE}"); // 创建或覆盖文件
	
				
					//save psum_toggles
					for (int i = 0; i < {self.FC_PES}; i++){{
						for (int j = 0; j < {prec}; j++) {{
							outFile_0 << toggle_bins[i][j] << "\\n";
						}}
					}}
					//save adder_N toggles
					for (int i = 0; i < {self.FC_PES//self.FC_TI}; i++){{
						for (int j = 0; j < {prec}; j++) {{
							outFile_1 << toggle_psum[i][j] << "\\n";
						}}
					}}
					//save output_toggles (todos)
					for (int i = 0; i < {self.FC_PES//self.FC_TI}; i++){{
						for (int j = 0; j < {prec}; j++) {{
							outFile_2 << toggle_output[i][j] << "\\n";
						}}
					}}
	

					''')

				if(self.RUN_GOLDEN):
					#f.write('goldenOutFile_OUT.close();\n')
					#f.write('goldenOutFile_PSUM.close();\n')
					#f.write('goldenOutFile_PE.close();\n')
					for i in range(self.FC_TI):#}; i++){{')		
						f.write(f'goldenOutFile_PE_{i}.close();\n');
					for i in range(1):
						f.write(f'goldenOutFile_PSUM_{i}.close();\n');
	
						f.write(f'goldenOutFile_OUT_{i}.close();\n');
	


					#f.write(f'for(int i = 0; i < {self.FC_PES//self.FC_TI}; i++){{')		
					#f.write(f'std::ofstream goldenOutFile_PSUM_{i}.close();\n');
					#f.write(f'std::ofstream goldenOutFile_PE_{i}.close();\n');
					#f.write(f'std::ofstream goldenOutFile_OUT_{i}.close();\n');


	
	
				f.write(f'''		
					
					outFile_0.close();
					outFile_1.close();
					outFile_2.close();



					//std::cout << "// Saving ADDER/ACCUM Data - DONE" << std::endl;	
					free(weight);
					free(input);
	
					return 0;
				}}''')
			
		if(True):
			if(self.run_cpp):	
				if(not IS_LINUX):
					os.system(f"g++ -O3 {TOGGLE_FILE}") #make this as fast as possible please	
					os.system(".\\a.exe")
				else:
					os.system(f"g++ -O3 {TOGGLE_FILE} -Wl,-rpath,/nfs/project/JayMok/power_experiments_xie/primitives")
					os.system("./a.out")
		
			#we should run the power of the golden as well, as well as (todos)
			#inference of the power estimated by our power model
					
			if(self.RUN_GOLDEN):
				#GOLDEN FILE FOR ADDER TREE
				CONFIG = {
						"EDAVerification": self.EDAVerification,
						"CLOCK": self.clock,
						"cap_load": self.cap_load,
						"fanout_load": 0.0,
						"tech": self.tech,
						
						"terms": self.FC_TI,#tile,
						"adderType": "AddTreeN",
						"prec_in": prec,
						"prec_sum": prec,	
						
						"OutputPowerFile": ADDER_TREE_POWER_GOLDEN_FILE				  
					}
				with open(JSON_FILE, "w") as json_file:
					json.dump(CONFIG, json_file, indent=4)  # indent 用于格式化输出	
	
					PE_TRACE_FILES = " ".join([PE_TRACE_FILE+"_"+str(i) for i in range(self.FC_TI)])
					print(self.FC_TI)
					print("run sbt")

				print(f'{SBT} "test:runMain adders.AdderNSpecFromFile {PE_TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')


				os.system(f'{SBT} "test:runMain adders.AdderNSpecFromFile {PE_TRACE_FILES} {JSON_FILE}"')# > golden.addern.log')

				#GOLDEN FILE FOR ACCUMULATOR
				CONFIG = {
						"EDAVerification": self.EDAVerification,
						"CLOCK": self.clock,
						"cap_load": self.cap_load,
						"fanout_load": 0.0,
						"tech": self.tech,
						
						"terms": 1,#(todos), could be more tile,
						"prec_in": prec,
						"prec_sum": prec,	
						
						"OutputPowerFile": ACCUMULATOR_POWER_GOLDEN_FILE				  
					}
				with open(JSON_FILE, "w") as json_file:
					json.dump(CONFIG, json_file, indent=4)  # indent 用于格式化输出	
	
					ACCUM_TRACE_FILE = OUT_TRACE_FILE
					ACCUM_TRACE_FILES = " ".join([ACCUM_TRACE_FILE+"_"+str(i) for i in range(1)])
				os.system(f'{SBT} "test:runMain accumulators.RegAccumulatorNSpecFromFile {ACCUM_TRACE_FILES} {JSON_FILE}"')# > golden.accum.log')



					#GOLDEN_FILE for Accumulator
					#with open(POWER_GOLDEN_FILE) as f:
					#	for l in f.readlines():
					#		print(l)
					
				
			#ADDER TREE:
			at_estimate_pwr = 0	
			at_estimate_runtime = 0
			at_estimate_energy = 0

			at_baseline1_pwr = 0	
			at_baseline1_runtime = 0
			at_baseline1_energy = 0

			at_baseline2_pwr = 0	
			at_baseline2_runtime = 0
			at_baseline2_energy = 0

			at_golden_pwr = 0
			at_golden_runtime = 0
			at_golden_energy = 0
	
			acc_estimate_pwr = 0	
			acc_estimate_runtime = 0
			acc_estimate_energy = 0

			acc_baseline1_pwr = 0	
			acc_baseline1_runtime = 0
			acc_baseline1_energy = 0

			acc_baseline2_pwr = 0	
			acc_baseline2_runtime = 0
			acc_baseline2_energy = 0

			acc_golden_pwr = 0
			acc_golden_runtime = 0
			acc_golden_energy = 0
	

			#with open(RUNTIME, 'r') as f:
			#	estimate_runtime = int(f.readlines()[0].strip())	
			if(self.RUN_MODEL):
				#Get power of the Adder Tree
				with open( PE_OUT_FILE , "r") as f:
					toggle_bins = np.zeros((self.FC_PES*prec))#custom in the future;
					for idx,l in enumerate(f.readlines()):
						toggle_bins[idx] = int(l)
					toggle_bins = toggle_bins.reshape((self.FC_PES//self.FC_TI, self.FC_TI, prec))#.reshape((-1))
					
					
					from power_models.AdderNPrimitive import AdderNPrimitive
					ap = AdderNPrimitive()
					# ap.execute_get_lut(out_features=["Total_Pwr"], constant_features = {
					# 	"CLOCK": self.clock,
					# 	"cap_load": self.cap_load,
					# 	"prec_in": prec,
					# 	"prec_sum": prec,
					# 	"terms": self.FC_TI
					# },
					# variable_features = {

					# })
					#(just do direct inference for now)
					#input_data, simply read it from the 
					# 初始化一个空列表用于存储最终结果
					r = 5
					input_data = {
							"CLOCK": [self.clock],
							"cap_load": [self.cap_load],
							"prec_in" : [prec],
							"prec_sum": [prec],
							"terms": [self.FC_TI]
						}

					input_data = trace_file(num=self.FC_TI, TRACE_FILE=PE_TRACE_FILE, input_data=input_data, r = r)


					#print(input_data)
					res = ap.execute_testing(
						name = "AdderN",
						out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
						input_data = input_data
					)
					#print(res)
					at_estimate_pwr = res['Total_Pwr']['res_sum']
					
					power_per_toggle, avg_pwr = ap.execute_get_lut(name="AdderN",out_features="Total_Pwr", constant_features = {
					 	"CLOCK": self.clock,
					 	"cap_load": self.cap_load,
					 	"prec_in": prec,
					 	"prec_sum": prec,
					 	"terms": self.FC_TI
					},
						variable_features = {
						"sum_toggles_in": [i for i in range(prec*self.FC_TI)] ,
						"toggles_out_0": [i for i in range(prec)]
					})


					at_baseline1_pwr = self.FC_PES//self.FC_TI * avg_pwr
					at_baseline2_pwr = at_baseline1_pwr#assume same for now

					print("BASELINE1 ADDERTREE", at_baseline1_pwr)
					print("ESTIMATE ADDERTREE", at_estimate_pwr)
	
					if(self.RUN_GOLDEN):
					 	gold = pd.read_csv(ADDER_TREE_POWER_GOLDEN_FILE,  delimiter="\t")
					 	#get relevant rows
					 	rel = gold.tail(n=self.FC_PES//self.FC_TI)['Total_Pwr']
					 	print(rel, np.sum(rel))
					 	print("GOLDEN ADDER TREE", np.sum(rel))
					 	at_golden_pwr = np.sum(rel)
					

				#Get power of the Accumulator

				with open( OUT_OUT_FILE , "r") as f:
					acc = AccumulatorPrimitive()
					#acc.load("Accumulator1", ["Total_Pwr"] )
	
					#(ad-hoc)
					prec = 32
					r = 1
					input_data = {
							"CLOCK": [self.clock],
							"cap_load": [self.cap_load],
							"prec_in" : [prec],
							"prec_out": [prec],
							"terms": [1]
						}

					input_data = trace_file(num=1, TRACE_FILE=OUT_TRACE_FILE, input_data=input_data, r = 1)


					#print(input_data)
					#(please debug, why cannot load the pickle?)
					res = acc.execute_testing(
						name = "Accumulator1",
						out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
						input_data = input_data
					)
					#print(res)
					acc_estimate_pwr = res['Total_Pwr']['res_sum']
					
					power_per_toggle, avg_pwr = acc.execute_get_lut(name="Accumulator1",out_features="Total_Pwr", constant_features = {
					 	"CLOCK": self.clock,
					 	"cap_load": self.cap_load,
					 	"prec_in": prec,
					 	"prec_out": prec,
					 	"terms": 1
					},
						variable_features = {
						"toggles_in_0": [i for i in range(prec)] ,
						"toggles_out_0": [i for i in range(prec)]
					})
					acc_baseline1_pwr = self.FC_PES//self.FC_TI * avg_pwr
					acc_baseline2_pwr = acc_baseline1_pwr#assume same for now
					print("BASELINE1 ACCUM", acc_baseline1_pwr)
					print("ESTIMATE ACCUM", acc_estimate_pwr)
					if(self.RUN_GOLDEN):
					 	gold = pd.read_csv(ACCUMULATOR_POWER_GOLDEN_FILE,  delimiter="\t")
					 	#get relevant rows
					 	rel = gold.tail(n=self.FC_PES//self.FC_TI)['Total_Pwr']
					 	print(rel, np.sum(rel))
					 	print("GOLDEN ACCUM", np.sum(rel))
					 	acc_golden_pwr = np.sum(rel)
					



			results = []

	
			res = {}
			res['name'] = "ADDER_TREE"

			res['estimate_pwr'] = at_estimate_pwr 
			res['estimate_runtime'] = at_estimate_runtime
			res['estimate_energy'] = at_estimate_energy

			res['baseline1_pwr'] = at_baseline1_pwr 
			res['baseline1_runtime'] = at_baseline1_runtime
			res['baseline1_energy'] = at_baseline1_energy

			res['baseline2_pwr'] = at_baseline2_pwr 
			res['baseline2_runtime'] = at_baseline2_runtime
			res['baseline2_energy'] = at_baseline2_energy	

			res['golden_pwr'] = at_golden_pwr
			res['golden_runtime'] = at_golden_runtime
			res['golden_energy'] = at_golden_energy

			results.append(res)

			res = {}
			res['name'] = "ACCUMULATOR"

			res['estimate_pwr'] = acc_estimate_pwr 
			res['estimate_runtime'] = acc_estimate_runtime
			res['estimate_energy'] = acc_estimate_energy

			res['baseline1_pwr'] = acc_baseline1_pwr 
			res['baseline1_runtime'] = acc_baseline1_runtime
			res['baseline1_energy'] = acc_baseline1_energy

			res['baseline2_pwr'] = acc_baseline2_pwr 
			res['baseline2_runtime'] = acc_baseline2_runtime
			res['baseline2_energy'] = acc_baseline2_energy	

			res['golden_pwr'] = acc_golden_pwr
			res['golden_runtime'] = acc_golden_runtime
			res['golden_energy'] = acc_golden_energy

			results.append(res)	
			#exit()
			return results
	

		
		
		#runtime = 0
		#power = 0
		#return runtime, power
	
