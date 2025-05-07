			"""
			for n in NET_DATA:


				net = n.lower()
				n = NET_DATA[n]
		
		
				#"in_function": "weight_data * input_data",
				#"post_function": "",#after accumulation
				#"accumulate": True
		
				units = n['units']
				accumulate = n['accumulate']
				accumulate_op = n['accumulate_op']
	
				accumulated_input = n.get('accumulated_input',False)
				num_inputs =len( n['input_bins'])
				prev_update = n.get('prev_update', '0')
				cur_update = n.get('cur_update', '0')
	
				output_update = n.get('output_update', '0')
				group = n['input_group']
	
				if(accumulated_input):
					continue
	

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
						//(TODOS) {m}_{net}[{net}][{meta_update}]++; 
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
			"""

















	if(len(inputs) != 0):
		hardware_config = inputs
	else:
		hardware_config = {

	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 1,
	"TN": 1,
	"TI": 4,
	"TX": 1,
	"TY": 1,
	"TKX": 1,
	"TKY": 1,
	"LOOP_ORDER": ["B", "N", "I", "X", "Y", "KX", "KY"],

	"MULT_TYPE": "HighRadixMultiplier",
	"MULT_SIDE": "weight",
	"MULT_RADIX": 2,
	"MULT_CORE_ADDER_TYPE": "SimpleAdder2",


	"ADDER_TREE_CORE_ADDER_TYPE": "SimpleAdder2",
	"ADDER_TREE_TYPE": "AdderTreeN",
	"ADDER_TREE_PREC": 16,
	"ADDER_TREE_DEPTH": 1, #i.e. number of cycles to output
	#"ADDER_TREE_PIPELINE": 0, #whether is pipelined / buffered at the output or not
				  #pipeline generally, maybe skip this for now improves slack clock timing but worsens power

	"ACCUM_TYPE": "AccumulatorN",
	"ACCUM_CORE_ADDER_TYPE": "SimpleAdder2",
	"ACCUM_PREC": 32,

	#this is the bank size, not the actual SRAM length or buffer size
	"L1_WEI_SRAM_SIZE": [16, 256],
	"L1_ACT_SRAM_SIZE": [16, 256],	
	
	"L1_WEI_SRAM_TYPE": "Reg",
	"L1_ACT_SRAM_TYPE": "Reg",	
	"L1_WEI_TOTAL_SIZE" : 48000,
	"L1_ACT_TOTAL_SIZE" : 48000,


	"L1_OUT_SRAM_SIZE": [8, 64],
	"L1_OUT_SRAM_TYPE": "Reg",
	"L1_OUT_TOTAL_SIZE" : 48000,
	
	#assume the OUTPUT for data-reuse will go to the L2 SRAM, instead of DRAM otherwise too wasteful for time
	#THerefore, L2 buffer is connected to DRAM, L1 WEI, L1 ACT and L1 OUT
	"L2_SRAM_SIZE": [8, 64],	
	"L2_TOTAL_SIZE": 512000,

	#skip DRAM for now... no discussion.
	"DRAM_LEN": 512,

	"INTERCONNECT_TYPE": "Multicast_Tree",#Multicast,

	"INTERCONNECT_WEI_TYPE": "MuxDeserializer",#mux based or shift serializer/deserializers

	"INTERCONNECT_WEI_SYSTOLIC_CAST_RATIO": 1,
	"INTERCONNECT_ACT_SYSTOLIC_CAST_RATIO": 1,
		

	"INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO": 1, #1 means matched bandwidth with PE, N means N cycles longer to load, i.e. unit unrolled by N, serial2parallel, -N means incoming longer, parallel2serial 
	"INTERCONNECT_ACT_SYSTOLIC_LOAD_RATIO": 1,	
	"INTERCONNECT_OUT_SYSTOLIC_LOAD_RATIO": 1,
	
	"INTERCONNECT_ACT_INTER_PE_X": False,
	"INTERCONNECT_ACT_INTER_PE_Y": False,
	#"INTERCONNECT_PSUM_SYSTOLIC_LOAD_RATIO": 1,

	"INTERCONNECT_L2_SYSTOLIC_LOAD_RATIO": 1,#compared to max(L1_WEI_LEN, L1_ACT_LEN)
	
	"CLOCK": 1,
	"cap_load": 1.0,
	"tech":"tsmc40",

	}
		input_data = paddle.randn([4, 3, 224, 224])
		layer = nn.Conv2D(in_channels=3, out_channels=64, kernel_size=3)#skip bias for now
		output_data = layer(input_data) 	

		network_layer = {
	"layer_name": "Conv1",
	"layer": layer,
	"input_data": input_data,
	"output_data": output_data,
	}
		mapping = {
	"Linear1": "df1",
	}

		design = dict_to_str(hardware_config)

		SIM_PARAMS = {
	"name": network_layer['layer_name'],
	"root": f"generated/Arch/SystolicConv/{design}",
	"SIM_CYCLES": 1000,
	"Randomize": 1,
	"Wei_Sparsity": 0.2,
	"Act_Sparsity": 0.2,	
	'save_np':True,#False,# True,

	#0: Baseline compare against golden
	#generate trace and cpp 
	#use specified sim-cycles

	#1: inference time
	#no trace, run_cpp, simcycles is -1

	#2: Debug-mode
	#Assume trace generated
	#only fine-tune the model powers
	'MODE': 0,
	"RUN_GOLDEN_SBT": 1,
	
	#'GEN_TRACE':True,
	#'RUN_CPP': True
}
		SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])










if __name__ == "__main_2_":
	import sys
	
	MODE = sys.argv[-1]
	print(MODE)
	input("MODE OK?")
	core(MODE = MODE)


	combos = []


	base_hc = {
	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 1,
	"TN": 1,
	"TI": 1,
	"TX": 2,
	"TY": 2,
	"TKX": 3,
	"TKY": 3,
	"LOOP_ORDER": ["B", "N", "I", "X", "Y", "KX", "KY"],

	"MULT_TYPE": "HighRadixMultiplier",
	"MULT_SIDE": "weight",
	"MULT_RADIX": 2,
	"MULT_CORE_ADDER_TYPE": "SimpleAdder2",


	"ADDER_TREE_CORE_ADDER_TYPE": "SimpleAdder2",
	"ADDER_TREE_TYPE": "AdderTreeN",
	"ADDER_TREE_PREC": 16,
	"ADDER_TREE_DEPTH": 1, #i.e. number of cycles to output
	#"ADDER_TREE_PIPELINE": 0, #whether is pipelined / buffered at the output or not
				  #pipeline generally, maybe skip this for now improves slack clock timing but worsens power

	"ACCUM_TYPE": "AccumulatorN",
	"ACCUM_CORE_ADDER_TYPE": "SimpleAdder2",
	"ACCUM_PREC": 32,

	#this is the bank size, not the actual SRAM length or buffer size
	"L1_WEI_SRAM_SIZE": [16, 64],
	"L1_ACT_SRAM_SIZE": [16, 64],	
	"L1_WEI_SRAM_TYPE": "Reg",
	"L1_ACT_SRAM_TYPE": "Reg",	
	"L1_WEI_TOTAL_SIZE" : 48000,
	"L1_ACT_TOTAL_SIZE" : 48000,


	"L1_OUT_SRAM_SIZE": [8, 64],
	"L1_OUT_SRAM_TYPE": "Reg",
	"L1_OUT_TOTAL_SIZE" : 48000,
	
	#assume the OUTPUT for data-reuse will go to the L2 SRAM, instead of DRAM otherwise too wasteful for time
	#THerefore, L2 buffer is connected to DRAM, L1 WEI, L1 ACT and L1 OUT
	"L2_SRAM_SIZE": [8, 64],	
	"L2_TOTAL_SIZE": 512000,

	#skip DRAM for now... no discussion.
	"DRAM_LEN": 512,

	"INTERCONNECT_TYPE": "Multicast_Tree",#Multicast,

	"NETWORK_WEI_TYPE": "Mux",#mux based or shift serializer/deserializers
	"NETWORK_ACT_TYPE": "Mux",#mux based or shift serializer/deserializers



	"INTERCONNECT_WEI_SYSTOLIC_CAST_RATIO": 1,
	#ACT Is a special case because the casting ratio, i.e. is dynamic.
	"INTERCONNECT_ACT_SYSTOLIC_CAST_RATIO": 1,

	"INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO": 1,
	"INTERCONNECT_ACT_SYSTOLIC_LOAD_RATIO": 1,	
	"INTERCONNECT_OUT_SYSTOLIC_LOAD_RATIO": 1,
	
	"INTERCONNECT_ACT_INTER_PE_X": False,
	"INTERCONNECT_ACT_INTER_PE_Y": False,
	#"INTERCONNECT_PSUM_SYSTOLIC_LOAD_RATIO": 1,

	"INTERCONNECT_L2_SYSTOLIC_LOAD_RATIO": 1,#compared to max(L1_WEI_LEN, L1_ACT_LEN)
	
	"CLOCK": 1,
	"cap_load": 1.0,
	"tech":"tsmc40",

	}

	pes = []
	for tb,tn,ti,tx,ty,tkx,tky in [
	[1,2,2,4,4,1,1],
	[1,2,2,4,2,2,1],
	[1,4,2,4,8,2,2],
	[3,3,8,4,8,2,1],
	[2,2,8,4,8,2,1],
]:	
		if 1:
			if 1:
				if 1:
					if 1:
						if 1:
							if 1:
								if lp in [ 
	["B", "N", "I", "X", "Y", "KX", "KY"],
	["B", "N", "I", "KX", "KY", "X", "Y"],
	["B", "N", "Y", "X", "I", "KX", "KY"],
	["B", "Y", "X", "KY", "KX", "I", "N"],
	["KY", "KX", "I", "X", "Y", "B", "N"],
	["I", "N", "KX", "KY", "Y", "X", "B"],

       ]:
									for radix in [2,4,8,16]:
										hc = dict(base_hc)
										hc["TB"] =  tb
										hc["TI"] =  ti
										hc["TN"] =  tn
										hc["TX"] =  tx
										hc["TY"] =  ty
										hc["TKX"] =  tkx
										hc["TKY"] =  tky		
										pes.append(tb*ti*tn*tx*ty*tkx*tky)
										hc["LOOP_ORDER"] = lp
										hc["MULT_RADIX"] = radix
										combos.append(hc)								
				
	print(len(combos))


	benchmarks = []
	
	#import matplotlib.pyplot as plt
	#plt.hist(pes)
	#plt.show()
	#exit(0)
	for inputs in combos:
		for benchmark in benchmarks:
			core(MODE=MODE, inputs=inputs, benchmark=benchmark)








	base_hardware_config_old = {

	"WEI_PREC": 8,
	"ACT_PREC": 8,

	"TB": 1,
	"TN": 1,
	"TI": 4,
	"TX": 1,
	"TY": 1,
	"TKX": 1,
	"TKY": 1,
	"LOOP_ORDER": ["B", "N", "I", "X", "Y", "KX", "KY"],

	"MULT_TYPE": "HighRadixMultiplier",
	"MULT_SIDE": "weight",
	"MULT_RADIX": 2,
	"MULT_CORE_ADDER_TYPE": "SimpleAdder2",


	"ADDER_TREE_CORE_ADDER_TYPE": "SimpleAdder2",
	"ADDER_TREE_TYPE": "AdderTreeN",
	"ADDER_TREE_PREC": 16,
	"ADDER_TREE_DEPTH": 1, #i.e. number of cycles to output
	#"ADDER_TREE_PIPELINE": 0, #whether is pipelined / buffered at the output or not
				  #pipeline generally, maybe skip this for now improves slack clock timing but worsens power

	"ACCUM_TYPE": "AccumulatorN",
	"ACCUM_CORE_ADDER_TYPE": "SimpleAdder2",
	"ACCUM_PREC": 32,

	#this is the bank size, not the actual SRAM length or buffer size
	"L1_WEI_SRAM_SIZE": [16, 256],
	"L1_ACT_SRAM_SIZE": [16, 256],	
	
	"L1_WEI_SRAM_TYPE": "Reg",
	"L1_ACT_SRAM_TYPE": "Reg",	
	"L1_WEI_TOTAL_SIZE" : 48000,
	"L1_ACT_TOTAL_SIZE" : 48000,


	"L1_OUT_SRAM_SIZE": [8, 64],
	"L1_OUT_SRAM_TYPE": "Reg",
	"L1_OUT_TOTAL_SIZE" : 48000,
	
	#assume the OUTPUT for data-reuse will go to the L2 SRAM, instead of DRAM otherwise too wasteful for time
	#THerefore, L2 buffer is connected to DRAM, L1 WEI, L1 ACT and L1 OUT
	"L2_SRAM_SIZE": [8, 64],	
	"L2_TOTAL_SIZE": 512000,

	#skip DRAM for now... no discussion.
	"DRAM_LEN": 512,

	"INTERCONNECT_TYPE": "Multicast_Tree",#Multicast,


	"NETWORK_WEI_TYPE": "Mux",#mux based or shift serializer/deserializers
	"NETWORK_ACT_TYPE": "Mux",#mux based or shift serializer/deserializers



	"INTERCONNECT_WEI_SYSTOLIC_CAST_RATIO": 1,
	#ACT Is a special case because the casting ratio, i.e. is dynamic.
	"INTERCONNECT_ACT_SYSTOLIC_CAST_RATIO": 1,
	

	"INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO": 1, #1 means matched bandwidth with PE, N means N cycles longer to load, i.e. unit unrolled by N, serial2parallel, -N means incoming longer, parallel2serial 
	"INTERCONNECT_ACT_SYSTOLIC_LOAD_RATIO": 1,	
	"INTERCONNECT_OUT_SYSTOLIC_LOAD_RATIO": 1,
	
	"INTERCONNECT_ACT_INTER_PE_X": False,
	"INTERCONNECT_ACT_INTER_PE_Y": False,
	#"INTERCONNECT_PSUM_SYSTOLIC_LOAD_RATIO": 1,

	"INTERCONNECT_L2_SYSTOLIC_LOAD_RATIO": 1,#compared to max(L1_WEI_LEN, L1_ACT_LEN)
	
	"CLOCK": 1,
	"cap_load": 1.0,
	"tech":"tsmc40",

	}






	
		self.MODULES =  {
		#if the wei systolic load ratio is > 1, then the output is slowed down by half, but better power due to smaller SRAM
#offset these ratios in the TIMING simulator, not here
#HARDWARES: L1_WEI_BUFFER



		#deserializer, only if necessary (systolic movement)
			"L1_WEI_LOAD_NETWORK": {
				"loop_order" : self.hc["LOOP_ORDER"],
				"cast_skips": ["TB", "TX", "TY"],
				"runtime": 0, 
				"data_obj":[ "weights_obj"],
				
				"units": L1_WEI_BUF_BIT_LEN,
				"input_metadata": {"toggles": {"update": "1"}},#j"bits": {		
				"input_bins": [self.hc["WEI_PREC"]],	
				'cur_update': ['weights_data'],
				'input_group': 1,

				"unit_time_unrolled": [ self.hc["INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO"] ],
				"config": {
					"primitive": "networks.Deserializer",
					"hardwareType": self.hc["L1_WEI_SRAM_TYPE"],
					"out_terms": self.hc["INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO"], 
				}
			
				
			},
			#deserializer, if necessary (systolic movement)
			"L1_WEI_CAST_NETWORK": {	
				"loop_order" :filter_loop_order(self.hc["LOOP_ORDER"], ["KX", "KY", "N", "I"]),
				#"cast_skips": ["TB", "TX", "TY"],
				"runtime": lambda p: p['FILTER_KX']*p['FILTER_KY']*p['INPUT']*p['OUTPUT']// L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
				"data_obj": ["weights_obj"],	

				"units": L1_WEI_BUF_BIT_LEN,
				"input_metadata": {},#j"bits": {
				"input_bins": [self.hc["WEI_PREC"]],	
				'cur_update': ['weights_data'],
				'prev_update': ['weights_data'],
				'input_group': 1,

				"output_metadata": { },
				"output_bins": self.hc["WEI_PREC"],
				"output_update": '0',#weights_data',

				"unit_time_unrolled": [ self.hc["INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO"] ],
				"trace_merge_units": self.hc["L1_WEI_SRAM_SIZE"][0] // self.hc["WEI_PREC"],
				"trace_merge_prec": self.hc["WEI_PREC"],
				"config": {
					"primitive": "memories.SRAMS",
					"type": self.hc["L1_WEI_SRAM_TYPE"],
					"entry_bits": self.hc["L1_WEI_SRAM_SIZE"][0],
					"rows": self.hc["L1_WEI_SRAM_SIZE"][1],	
				}
			},


			"L1_INPUT_READ": {

				"loop_order": self.hc["LOOP_ORDER"],
				"cast_skips": ["TX","TY","TB"],
				"runtime": lambda p: p['FILTER_KX']*p['FILTER_KY']*p['INPUT']*p['OUTPUT']*p["INPUT_X"]*p["INPUT_Y"]*p["BAT"] // L1_ACT_BUF_BIT_LEN * p['avg_cycle_per_op'],
				"data_obj": ["inputs_obj"],

				"units": L1_ACT_BUF_BIT_LEN,
				"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
				"input_bins": [self.hc["WEI_PREC"]],	
				'cur_update': ['weights_data'],
				'input_group': 1,
				"unit_time_unrolled": [ self.hc["INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO"] ],
				"trace_merge_units": self.hc["L1_WEI_SRAM_SIZE"][0] // self.hc["WEI_PREC"],
				"trace_merge_prec": self.hc["WEI_PREC"],
				"config": {
					#"DynamicHardwareMap": {"in_1": "fanout"},
					"primitive": "memories.SRAMS",
					"type": self.hc["L1_WEI_SRAM_TYPE"],
					"entry_bits": self.hc["L1_WEI_SRAM_SIZE"][0],
					"rows": self.hc["L1_WEI_SRAM_SIZE"][1],	
					"mode": 0,#0 is read, 1 is write
				}
			},
	
			"L1_ACT_READ": {
				"units": self.hc["TI"]*self.hc["TB"]*(self.hc["TKX"]+self.hc["TX"]-1)*(self.hc["TKY"]+self.hc["TY"]-1),
				"input_metadata": {},#j"bits": {
				"input_bins": [self.hc["ACT_PREC"]],
				'cur_update': ['inputs_data'],
				'input_group': 1,
				"output_metadata": { },
				"output_bins": self.hc["ACT_PREC"],
				"output_update": '1',#weights_data',
				"unit_time_unrolled": [ self.hc["INTERCONNECT_ACT_SYSTOLIC_LOAD_RATIO"] ],
				"trace_merge_units": self.hc["L1_ACT_SRAM_SIZE"][0] // self.hc["ACT_PREC"],
				"trace_merge_prec": self.hc["ACT_PREC"],
				"accumulated_input": False,
				'reset_trigger': [],
				'accumulate': False,
				'accumulate_op': '',
				"config": {
					"primitive": "memories.SRAMS",
					"type": self.hc["L1_ACT_SRAM_TYPE"],
					"entry_bits": self.hc["L1_ACT_SRAM_SIZE"][0],
					"rows": self.hc["L1_ACT_SRAM_SIZE"][1],	
					"mode": 0,#,remember ot change, 0 is read, 1 is write
				}
			},

			"L2_GLOBAL": {
				"units": self.hc["TI"]*self.hc["TB"]*(self.hc["TKX"]+self.hc["TX"]-1)*(self.hc["TKY"]+self.hc["TY"]-1),
				"input_metadata": {},#j"bits": {
				"input_bins": [self.hc["ACT_PREC"]],
				'cur_update': ['inputs_data'],
				'input_group': 1,
				"output_metadata": { },
				"output_bins": self.hc["ACT_PREC"],
				"output_update": '1',#weights_data',
				"unit_time_unrolled": [ self.hc["INTERCONNECT_ACT_SYSTOLIC_LOAD_RATIO"] ],
				"trace_merge_units": self.hc["L1_ACT_SRAM_SIZE"][0] // self.hc["ACT_PREC"],
				"trace_merge_prec": self.hc["ACT_PREC"],
				"accumulated_input": False,
				'reset_trigger': [],
				'accumulate': False,
				'accumulate_op': '',
				"config": {
					"primitive": "memories.SRAMS",
					"type": self.hc["L1_ACT_SRAM_TYPE"],
					"entry_bits": self.hc["L1_ACT_SRAM_SIZE"][0],
					"rows": self.hc["L1_ACT_SRAM_SIZE"][1],	
					"mode": 0,#,remember ot change, 0 is read, 1 is write
				}
			},





		if("L1_WEI_WRITE_NETWORK" in net):
			ratio = self.hc["LOAD_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"L1_WEI_WRITE_NETWORK": {	
					"loop_order" : filter_loop_order(self.hc["LOOP_ORDER"], ["KX", "KY", "N", "I"]),
					#"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: WEIGHT_SIZE(p) // L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],		
					"units": L1_WEI_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['weights_data'],
					'input_group': 1,

					"unit_time_unrolled": [ -ratio  ],
				},
			}
			# meaning small2big at read, so write big2small, serializer 
			if(ratio < 0): #meaning we are small to big, Deserializer. But switch at write.
				config["L1_WEI_WRITE_NETWORK"].update({	
					"config": {
						"primitive": "networks.Parallel2Serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": 1,
						}
					})	
			else:
				config["L1_WEI_WRITE_NETWORK"].update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": 1,
						}
					})	
			self.MODULES.update(config)









		if("L1_WEI_READ_NETWORK" in net):
			ratio = self.hc["LOAD_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"L1_WEI_READ_NETWORK": {	
					"loop_order" : self.hc["LOOP_ORDER"],
					"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: WEIGHT_SIZE(p) // L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],		
					"units": TILE,#L1_WEI_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['weights_data'],
					'input_group': 1,

					"unit_time_unrolled": [ ratio  ],
				},
			}
			# meaning small2big at read, so write big2small, serializer 
			if(ratio > 0): #meaning big to small
				config["L1_WEI_READ_NETWORK"].update({	
					"config": {
						"primitive": "networks.Parallel2Serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": 1,
						}
					})	
			else:
				config["L1_WEI_READ_NETWORK"].update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": 1,
						}
					})	
			self.MODULES.update(config)








		if("L1_ACT_READ_NETWORK" in net):
			ratio = self.hc["LOAD_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"L1_ACT_READ_NETWORK": {	
					"loop_order" : self.hc["LOOP_ORDER"],
					"cast_skips": [ "TN"],
					"runtime": lambda p:INPUT_SIZE(p) // L1_ACT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["inputs_obj"],		
					"units": TILE,#L1_ACT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['inputs_data'],
					'input_group': 1,

					"unit_time_unrolled": [ ratio  ],
				},
			}
			# meaning small2big at read, so write big2small, serializer 
			if(ratio > 0): #meaning big to small
				config["L1_ACT_READ_NETWORK"].update({	
					"config": {
						"primitive": "networks.Parallel2Serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": 1,
						}
					})	
			else:
				config["L1_ACT_READ_NETWORK"].update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": 1,
						}
					})	
			self.MODULES.update(config)





	
		if("L1_ACT_WRITE_NETWORK" in net):
			ratio = self.hc["LOAD_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"L1_ACT_WRITE_NETWORK": {	
					"loop_order" : filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "B", "I", "KX", "KY"]),
					#"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: INPUT_SIZE(p) // L1_ACT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["inputs_obj"],		
					"units": L1_ACT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['inputs_data'],
					'input_group': 1,

					"unit_time_unrolled": [ -ratio  ],
				},
			}
			# meaning small2big at read, so write big2small, serializer 
			if(ratio > 0): #meaning we are small to big, Deserializer. But switch at write.
				config["L1_ACT_WRITE_NETWORK"].update({	
					"config": {
						"primitive": "networks.Parallel2Serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": 1,
						}
					})	
			else:
				config["L1_ACT_WRITE_NETWORK"].update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": 1,
						}
					})	
			self.MODULES.update(config)






	if("WEI_PE_CAST" in net):
			ratio = self.hc["CAST_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"WEI_PE_CAST": {	
					"loop_order" : self.hc["LOOP_ORDER"],
					#want the broadcated results, but unrolled in time
					#"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: WEIGHT_SIZE(p) // L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],		
					"units":TILE,# L1_WEI_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [prec],	
					'cur_update': ['weights_data'],
					'input_group': 1,
					"unit_time_unrolled": [ ratio  ],

					"config": {
						#ACT will need dynamic casting calculation
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": max(1, (self.hc["TB"]*self.hc["TX"]*self.hc["TY"])//ratio),
						}
					}
			}
			self.MODULES.update(config)

		if("ACT_PE_CAST" in net):
			ratio = self.hc["CAST_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"ACT_PE_CAST": {	
					"loop_order" : self.hc["LOOP_ORDER"],
					#"cast_skips": ["TN"],
					"runtime": lambda p: WEIGHT_SIZE(p) // L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["inputs_obj"],		
					"units": L1_ACT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	

					"input_bins": [prec, 32],	
					#assume stride = 1 for now
					'cur_update': ['inputs_data', f'{self.hc["TN"]}*std::min({self.hc["TKX"]} - std::abs(x % {self.hc["TX"]} - {self.hc["TKX"]} + 1) , {self.hc["TKX"]})* std::min({self.hc["TKY"]} - std::abs(y % {self.hc["TY"]} - {self.hc["TKY"]} + 1) , {self.hc["TKY"]})'],
					'input_group': 1,
					"unit_time_unrolled": [ ratio , ratio ],


					"config": {
						#ACT will need dynamic casting calculation
						"CustomMap": { "in_1": "fanout"  },
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						#"fanout": 
						"fanout": max(1, (self.hc["TN"]*self.hc["TKX"]*self.hc["TKY"])//ratio),
						}
					}
			}
			self.MODULES.update(config)





		'''
		if("PE_ARRAY" in net):
			if(self.hc["MULT_SIDE"] == "weight"):
				MULTIPLIER_bins = ['weights_data', 'inputs_data']		
				MULT_prec1 = self.hc['WEI_PREC']
				MULT_prec2 = self.hc["ACT_PREC"]	
			else:
				MULTIPLIER_bins = ['weights_data', 'inputs_data'][::-1]
				MULT_prec1 = self.hc['ACT_PREC']
				MULT_prec2 = self.hc["WEI_PREC"]	
			self.MODULES.update({
				"PE_ARRAY": {
					"loop_order": self.hc["LOOP_ORDER"],
					"runtime": lambda p: MAC_NO //  p['avg_cycle_per_op'],
					"data_obj": ["inputs_obj","weights_obj"],

					"units": TILE,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": MULTIPLIER_bins,#[MULT_prec1, MULT_prec2],	
					'cur_update': ['weights_data', "inputs_data"],
					'input_group': 1,

					"config": {
						"primitive": "multipliers.Multiplier2",
						"multiplierType": self.hc["MULT_TYPE"],
						"radix": self.hc["MULT_RADIX"],
						"prec1": MULT_prec1,
						"prec2": MULT_prec2,
						"side": self.hc.get("SIDE", "weight"),
						"adderType": self.hc["MULT_CORE_ADDER_TYPE"],
					}
				},

			
			})
		'''

		if("L1_OUT_READ" in net):
			self.MODULES.update({
				"L1_OUT_READ": {
					"loop_order": filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "N", "B"]),
					"cast_skips": [],
					"runtime": lambda p: OUTPUT_SIZE(p) // L1_OUT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["outputs_obj"],

					"units": L1_OUT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['outputs_data'],
					'input_group': 1,
					"unit_time_unrolled": [ self.hc["LOAD_RATIO"] ],
					"trace_merge_units": self.hc["L1_OUT_SRAM_SIZE"][0] // self.hc["PREC"],
					"trace_merge_prec": self.hc["PREC"],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc["L1_OUT_SRAM_TYPE"],
						"entry_bits": self.hc["L1_OUT_SRAM_SIZE"][0],
						"rows": self.hc["L1_OUT_SRAM_SIZE"][1],	
						"mode": 0,#0 is read, 1 is write
					}
				},

			})




		if("L1_OUT_WRITE" in net):
			self.MODULES.update({
				"L1_OUT_WRITE": {
					"loop_order": filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "N", "B"]),
					"cast_skips": [],
					"runtime": lambda p: OUTPUT_SIZE(p) // L1_OUT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["outputs_obj"],

					"units": L1_OUT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['outputs_data'],
					'input_group': 1,
					"unit_time_unrolled": [ self.hc["LOAD_RATIO"] ],
					"trace_merge_units": self.hc["L1_OUT_SRAM_SIZE"][0] // self.hc["PREC"],
					"trace_merge_prec": self.hc["PREC"],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc["L1_OUT_SRAM_TYPE"],
						"entry_bits": self.hc["L1_OUT_SRAM_SIZE"][0],
						"rows": self.hc["L1_OUT_SRAM_SIZE"][1],	
						"mode": 1,#0 is read, 1 is write
					}
				},

			})




		if("L1_ACT_WRITE" in net):
			self.MODULES.update({
				"L1_ACT_WRITE": {	
					"loop_order" :filter_loop_order(self.hc["LOOP_ORDER"], ["B","X", "Y", "KX", "KY", "I"]),
					#"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: p['FILTER_KX']*p['FILTER_KY']*p['INPUT']*p['OUTPUT']// L1_ACT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["inputs_obj"],	
	
					"units": L1_ACT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['inputs_data'],
					'input_group': 1,

					"unit_time_unrolled": [ self.hc["LOAD_RATIO"] ],
					"trace_merge_units": self.hc["L1_ACT_SRAM_SIZE"][0] // self.hc["PREC"],
					"trace_merge_prec": self.hc["PREC"],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc["L1_ACT_SRAM_TYPE"],
						"entry_bits": self.hc["L1_ACT_SRAM_SIZE"][0],
						"rows": self.hc["L1_ACT_SRAM_SIZE"][1],	
						"mode": 1,#0 is read, 1 is write
					}
				},
	
			})



		if("L1_ACT_READ" in net):
			self.MODULES.update({
				"L1_ACT_READ": {
					"loop_order": self.hc["LOOP_ORDER"],
					"cast_skips": ["TN"],
					"runtime": lambda p: MAC_NO // L1_ACT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["inputs_obj"],

					"units": TILE,#L1_ACT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['inputs_data'],
					'input_group': 1,
					"unit_time_unrolled": [ self.hc["LOAD_RATIO"] ],
					"trace_merge_units": self.hc["L1_ACT_SRAM_SIZE"][0] // self.hc["PREC"],
					"trace_merge_prec": self.hc["PREC"],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc["L1_ACT_SRAM_TYPE"],
						"entry_bits": self.hc["L1_ACT_SRAM_SIZE"][0],
						"rows": self.hc["L1_ACT_SRAM_SIZE"][1],	
						"mode": 0,#0 is read, 1 is write
					}
				},

			})





		if("L1_WEI_READ" in net):
			self.MODULES.update({
				"L1_WEI_READ": {
					"loop_order": self.hc["LOOP_ORDER"],
					"cast_skips": ["TX","TY","TB"],
					"runtime": lambda p: MAC_NO // L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],

					"units": TILE,#L1_WEI_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['weights_data'],
					'input_group': 1,
					"unit_time_unrolled": [ self.hc["LOAD_RATIO"] ],
					"trace_merge_units": self.hc["L1_WEI_SRAM_SIZE"][0] // self.hc["PREC"],
					"trace_merge_prec": self.hc["PREC"],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc["L1_WEI_SRAM_TYPE"],
						"entry_bits": self.hc["L1_WEI_SRAM_SIZE"][0],
						"rows": self.hc["L1_WEI_SRAM_SIZE"][1],	
						"mode": 0,#0 is read, 1 is write
					}
				},

			})
		if("L1_WEI_WRITE" in net):
			self.MODULES.update({
				"L1_WEI_WRITE": {	
					"loop_order" :filter_loop_order(self.hc["LOOP_ORDER"], ["KX", "KY", "N", "I"]),
					#"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: p['FILTER_KX']*p['FILTER_KY']*p['INPUT']*p['OUTPUT']// L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],	
	
					"units": L1_WEI_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['weights_data'],
					'prev_update': ['weights_data'],
					'input_group': 1,

					"unit_time_unrolled": [ self.hc["LOAD_RATIO"] ],
					"trace_merge_units": self.hc["L1_WEI_SRAM_SIZE"][0] // self.hc["PREC"],
					"trace_merge_prec": self.hc["PREC"],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc["L1_WEI_SRAM_TYPE"],
						"entry_bits": self.hc["L1_WEI_SRAM_SIZE"][0],
						"rows": self.hc["L1_WEI_SRAM_SIZE"][1],	
						"mode": 1,#0 is read, 1 is write
					}
				},
	

			})




print(self.MODULES)

		'''
		if("L1_WEI_READ" in net):
			self.MODULES.update({
				"L1_WEI_READ": {
					"loop_order": self.hc["LOOP_ORDER"],
					"cast_skips": ["TX","TY","TB"],
					"runtime": lambda p: MAC_NO // L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],

					"units": TILE,#L1_WEI_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['weights_data'],
					'input_group': 1,
					"unit_time_unrolled": [ self.hc["LOAD_RATIO"] ],
					"trace_merge_units": self.hc["L1_WEI_SRAM_SIZE"][0] // self.hc["PREC"],
					"trace_merge_prec": self.hc["PREC"],
					"config": {
						"primitive": "memories.SRAMS",
						"type": self.hc["L1_WEI_SRAM_TYPE"],
						"entry_bits": self.hc["L1_WEI_SRAM_SIZE"][0],
						"rows": self.hc["L1_WEI_SRAM_SIZE"][1],	
						"mode": 0,#0 is read, 1 is write
					}
				},

			})
		'''
		#print(self.MODULES)
		#exit()





		if("WEI_WINO_G_MULT" in net):
			config = {
				"WEI_WINO_G_MULT": {
					"loop_order": self.hc["LOOP_ORDER"],
					"runtime": lambda p: MAC_NO //  p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],
					"units": self.hc["TN"]*self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]*self.hc["TG"],
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [ self.hc["WEI_PREC"], self.hc['WEI_PREC']  ],		
					"input_trace_name": [ "in1", "in2"],
					"cur_update": [  'weights_data', 'winoG_data'   ],
					'input_group': 1,
				}}

			if(self.hc["MULT_TYPE"] == "ConstantMultiplier2"):
				"config": {	
					"primitive": "multipliers.ConstantMultiplier2",
					"multiplierType": self.hc["MULT_TYPE"],
					"out_prec": self.hc["WEI_PREC"]+8,
					"terms": 1,
					"prec1": self.hc["WEI_PREC"],
					"prec2": 8,
					"side": self.hc.get("SIDE", "weight"),
					"adderType": self.hc["MULT_CORE_ADDER_TYPE"],	
				},
			else:	
				"config": {
					"primitive": "multipliers.Multiplier2",
					"multiplierType": self.hc["MULT_TYPE"],
					"out_prec": self.hc["WEI_PREC"]+8,
					"radix": self.hc["MULT_RADIX"],
					"prec1": self.hc["WEI_PREC"],
					"prec2": 8,
					"side": self.hc.get("SIDE", "weight"),
					"adderType": self.hc["MULT_CORE_ADDER_TYPE"],
				}
	
				
			
			
			})

	




					"loop_order": self.hc["LOOP_ORDER"],
					"data_obj": ["weights_obj"],
					"units": self.hc["TN"]*self.hc["TI"]*self.hc["TKX"]*self.hc["TKY"]*self.hc["TG"],
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [ self.hc["WEI_PREC"], self.hc['WEI_PREC']  ],		
					"input_trace_name": [ "in1", "in2"],
					"cur_update": [  'weights_data', 'winoG_data'   ],
					'input_group': 1,
				}}

			if(self.hc["MULT_TYPE"] == "ConstantMultiplier2"):
				"config": {	
					"primitive": "multipliers.ConstantMultiplier2",
					"multiplierType": self.hc["MULT_TYPE"],
					"out_prec": self.hc["WEI_PREC"]+8,
					"terms": 1,
					"prec1": self.hc["WEI_PREC"],
					"prec2": 8,
					"side": self.hc.get("SIDE", "weight"),
					"adderType": self.hc["MULT_CORE_ADDER_TYPE"],	
				},
			else:	
				"config": {
					"primitive": "multipliers.Multiplier2",
					"multiplierType": self.hc["MULT_TYPE"],
					"out_prec": self.hc["WEI_PREC"]+8,
					"radix": self.hc["MULT_RADIX"],
					"prec1": self.hc["WEI_PREC"],
					"prec2": 8,
					"side": self.hc.get("SIDE", "weight"),
					"adderType": self.hc["MULT_CORE_ADDER_TYPE"],
				}
	
				
			
			
			})

	


		if("WEI_WINO_G_ADD" in net):
			self.MODULES.update({
				"WEI_WINO_G_ADD": {
					"loop_order": self.hc["LOOP_ORDER"],
					"runtime": lambda p: MAC_NO //  p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],

					"units": TILE,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {
					"input_bins": [prec],	
					'cur_update': ['weights_data', "inputs_data"],
					'input_group': 1,

					"config": {
						"primitive": "multipliers.Multiplier2",
						"multiplierType": self.hc["MULT_TYPE"],
						"radix": self.hc["MULT_RADIX"],
						"prec1": prec,
						"prec2": 8,
						"side": self.hc.get("SIDE", "weight"),
						"adderType": self.hc["MULT_CORE_ADDER_TYPE"],
					}
				},

			
			})


































if __name__ == "__main__":

	import sys	

	MODE = sys.argv[-2]	
	combos = []

	#hardware_config = "src/test/

	#Hierarchy based modelling parameters
	#GENERAL
	# -> PE_ARRAY (Multiplier2)
	# -> L1_WEI_LOADER (Serializer/Deserializer + L1 SRAM)
	# -> L1_ACT_LOADER	(..)
	# -> GLOBAL_L2       (Serializer/Deserializer + L2 SRAM)
	# -> ADDER_TREE      (ADDER TREE or Serializer + Accumulator)
	# -> ACCUMUALTOR     (Accumulator w/ Reg, Accumulator w/ SRAM)
	# -> OUTPUT_LOADER   (Serializer/Deserializer + L1 SRAM)
	# -> OUTPUT_DRAM_L2_BUS   (MUX2)
	# -> L2_L1_ACT_L1_WEI_BUS  (MULTICAST)
	base_hardware_config = {

		"GENERAL": {
			"LOOP_ORDER": ["B", "N", "I",  "KX", "KY", "X", "Y"],
			"TB": 1,
			"TN": 1,
			"TI": 4,
			"TX": 1,
			"TY": 1,
			"TKX": 1,
			"TKY": 1,
	
			"CLOCK": 1,
			"cap_load": 0.1,
			"tech":"tsmc40",

			"GENERAL_PREC": 8, #General PREC if non specified
		},
		"PE_ARRAY": {
			"VALID_NETS": ["PE_ARRAY"],
			"ACT_PREC": 8,
			"WEI_PREC": 8,

			"MULT_TYPE": "HighRadixMultiplier",
			"MULT_SIDE": "weight",
			"MULT_RADIX": 2,
			"MULT_CORE_ADDER_TYPE": "SimpleAdder2",
		},
		"ADDER_TREE": {
			"VALID_NETS": ["ADDER_TREE"],
			"ADDERN_TYPE": "AddTreeN",
			"CORE_ADDER_TYPE": "SimpleAdder2",
			#"TYPE": "AdderTreeN",#AdderTree, i.e. Accumulator
			"PREC": 16,
			"OUT_PREC": 32,
			"DEPTH": 1, #i.e. number of cycles to output	
		},	
		"ACCUMULATOR": {
			"VALID_NETS": ["ACCUMULATOR"],
			"TYPE": "AccumulatorN",
			"CORE_ADDER_TYPE": "SimpleAdder2",
			"ACCUM_PREC": 32,
		},
		"WEI_LOADER": {
			"VALID_NETS": ["L1_WEI_READ", "L1_WEI_WRITE", "L1_WEI_READ_NETWORK"],
	#		"VALID_NETS": ["L1_WEI_READ", "L1_WEI_WRITE"],#"L1_WEI_WRITE_NETWORK", "L1_WEI_READ_NETWORK"],
			#
			#"VALID_NETS": ["L1_WEI_READ_NETWORK"],
	
			"L1_WEI_SRAM_SIZE": [16, 256],
			"L1_WEI_SRAM_TYPE": "Reg",
			"L1_WEI_TOTAL_SIZE" : 48000,		
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers	
			"LOAD_RATIO": 1,			
			"PREC": 8,
		},
		"ACT_LOADER": {
			"VALID_NETS": ["L1_ACT_READ", "L1_ACT_WRITE", "L1_ACT_READ_NETWORK"],
#, "L1_ACT_WRITE_NETWORK", "L1_ACT_READ_NETWORK"],	
	#		"VALID_NETS": ["L1_ACT_READ_NETWORK"],
	
			"L1_ACT_SRAM_SIZE": [16, 256],	
			"L1_ACT_SRAM_TYPE": "Reg",		
			"L1_ACT_TOTAL_SIZE" : 48000,	
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers
			"LOAD_RATIO": 1,		
			"PREC": 8,
		},
		"OUT_LOADER": {	
			"VALID_NETS": ["L1_OUT_READ", "L1_OUT_WRITE", "L1_OUT_WRITE_NETWORK", "L1_OUT_READ_NETWORK"],		
			"VALID_NETS": ["L1_OUT_READ", "L1_OUT_WRITE", "L1_OUT_WRITE_NETWORK"],#, "L1_OUT_READ_NETWORK"],		
		#	"VALID_NETS": [ "L1_OUT_WRITE_NETWORK"],#, "L1_OUT_READ_NETWORK"],		



			"L1_OUT_SRAM_SIZE": [16, 256],
			"L1_OUT_SRAM_TYPE": "Reg",
			"L1_OUT_TOTAL_SIZE" : 48000,
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers	
			"LOAD_RATIO": 1,	
			"PREC": 16,
		},
		"WEI_PE_CAST": {
			"VALID_NETS": ["WEI_PE_CAST"],			
			"CAST_RATIO": 1,	
			"PREC": 8,
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers		
		},
		"ACT_PE_CAST": {
			"VALID_NETS": ["ACT_PE_CAST"],
			#ACT Is a special case because the casting ratio, i.e. is dynamic.
			"CAST_RATIO": 1,	
			"INTER_PE_X": False,
			"INTER_PE_Y": False,
			#"INTERCONNECT_PSUM_SYSTOLIC_LOAD_RATIO": 1,
			"PREC": 8,
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers		
	
		},
		"L2": {
			"VALID_NETS": ["L2_OUT_WRITE", "L2_WEI_READ", "L2_ACT_READ", "L2_ACT_WRITE", "L2_WEI_WRITE",
		"OUTPUT_DRAM_L2_BUS",
			],
			"L2_SRAM_SIZE": [8, 64],
			"L2_SRAM_TYPE": "Reg",	
			"LOAD_RATIO": 1,#compared to max(L1_WEI_LEN, L1_ACT_LEN)	
			"WEI_PREC": 8,
			"ACT_PREC": 8,
		},

	}
	#VALID_UNITS = ["ACT_LOADER"]#["PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]#["WEI_PE_CAST"]#[k  for k in  base_hardware_config] #["PE_ARRAY"]  #[,"WEI_LOADER"]#, "WEI_PE_CAST", "ACT_PE_CAST"]#[k  for k in  base_hardware_config]#["PE_ARRAY"]
	
	#VALID_UNITS = ["ACT_PE_CAST"]

	VALID_UNITS = ["OUT_LOADER"]#, "PE_ARRAY", "WEI_LOADER", "ACT_LOADER","WEI_PE_CAST", "ACT_PE_CAST"]#[k  for k in  base_hardware_config] #["PE_ARRAY"]  #[,"WEI_LOADER"]#, "WEI_PE_CAST", "ACT_PE_CAST"]#[k  for k in  base_hardware_config]#["PE_ARRAY"]
	VALID_UNITS = ["ADDER_TREE"]
	#VALID_UNITS = ["OUT_LOADER", "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]
	#VALID_UNITS = ["PE_ARRAY"]
	#VALID_UNITS = ["OUT_LOADER"]#, "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]

	#VALID_UNITS = ["WEI_LOADER"]#, "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]	
	#VALID_UNITS = ["ACT_LOADER"]#, "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]
	#VALID_UNITS = ["PE_ARRAY"]#, "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]
	
	
	
	#VALID_UNITS = ["WEI_PE_CAST", "ACT_PE_CAST"]
	#VALID_UNITS = ["PE_ARRAY"]#, "PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]
	
	
	#reference
	input_data = paddle.randn([4, 32, 28, 28])
	layer = nn.Conv2D(in_channels=32, out_channels=64, kernel_size=3)#skip bias for now
	output_data = layer(input_data) 	
	repr_str = repr(layer)
	weight_name = repr(layer).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")
	input_name = repr(input_data.shape).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")

	network = {
	"input_data" :input_name,
		"layer": weight_name,	
	}
	
	#print(layer)
	base_network_layer = {
	"layer_name": dict_to_str(network),#"Conv1",
	"layer": layer,
	"input_data": input_data,
	"output_data": output_data,
	}

	base_mapping = {
		"SparseConv": "df1",
	}
	
	design = dict_to_str(base_hardware_config["GENERAL"])
	#Should be hierarchical

	base_SIM_PARAMS = {
	"SAVE_RESULTS": "analyzed_04_03",

		"name": base_network_layer['layer_name'],
		"root": f"generated/Arch/SystolicConv/{design}",

		"SIM_CYCLES": 1000,
		"Randomize": 1,
		"Wei_Sparsity": 0.1,
		"Act_Sparsity": 0.1,	
		'save_np':True,#False,# True,
		'MODE': MODE,
		"RUN_GOLDEN_SBT": 1,	
		'RUN_CPP': True,
		"SKIP_IF_EXISTING_GOLDEN":1,#True,#False,#False,#False,# True,#don't run the golden related flow if we see the golden power is there
	}
	#SIM_PARAMS = base_SIM_PARAMS
	#base_SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])


	run_fig6(base_hardware_config, base_mapping, base_network_layer, base_SIM_PARAMS, VALID_UNITS)




'''
def SparseOurModel(hardware_config, benchmark):
	N = 1024
	
	h = hardware_config["GENERAL"]

	pe = h['TI']*h['TN']*h['TKX']*h['TKY']*h['TX']*h['TY']*h['TB']

	hp = {}	
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
			
		print("wei_reuse", "act_reuse")
		print(wei_reuse, act_reuse)
		input()
		in_a = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N, REUSE = act_reuse)
		in_w = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N, REUSE = wei_reuse)
		in_o = [in_w[idx] *in_a[idx] for idx in range(min(len(in_w), len(in_a)))]
	
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
					in_0 = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N)
					in_1 = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N)
				else:
					in_0 = gen_in(b['ACT_SPARSITY'], b['ACT_BIT_ZERO'], prec = 'ACT_PREC', N = N)
					in_1 = gen_in(b['WEI_SPARSITY'], b['WEI_BIT_ZERO'], prec = 'WEI_PREC', N = N)
					side_cycle = hh["ACT_PREC"]/ratio				
					prec2 = hh["WEI_PREC"]
					prec1 = hh["ACT_PREC"]	
					side_bits =1 -  b["ACT_BIT_ZERO"]/hh['ACT_PREC']

				cc = min(len(in_0), len(in_1))
				in_0 = in_0[0:cc]
				in_1 = in_1[0:cc]
		
				#power model
				res = Multiplier2Block(h, hh, in_0, in_1, prec1, prec2, side, mode=modes)

				units = pe
				#powers[c] = res['Total_Pwr']['res'][-1] * units
				powers[c] = res['Total_Pwr']['res'][-1][-1] *units



			
			elif(component == "ADDER_TREE"):
			
				if(hh["ADDERN_TYPE"] == "AddTreeN"):
					side_cycle = 1
				if(hh["ADDERN_TYPE"] == "SimpleAdderN"):
					side_cycle = 1
	
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					side_cycle = INNER
				else:
					print("invalid ADDERN_TYPE", hh["ADDERN_TYPE"])
					exit()

				#power model
				if(hh["ADDERN_TYPE"] == "AddTreeN"):
					ap = AdderNPrimitive()
					input_data = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['PREC']],
					"prec_sum": [hh['OUT_PREC']],
					"terms": [INNER],
					"adderNType": [hh["ADDERN_TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					}	
					for t in range(INNER):
						input_data[f"in_{t}"] =[ in_o]
					res = ap.execute_testing(
					name = "AdderN",
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = input_data
					)
	
				elif(hh["ADDERN_TYPE"] == "Accumulator"):
					ap = AccumulatorPrimitive()
					res = ap.execute_testing(
					name = "Accumulator",
					out_features = ['Total_Pwr'],#,'Unit_Cycles', 'Energy'],
					input_data = {
					"CLOCK": [h['CLOCK']],
					"cap_load": [h['cap_load']],
					"prec_in" : [hh['PREC']],
					"prec_out": [hh['OUT_PREC']],
					"terms": [1],
					"adderNType": [hh["ADDERN_TYPE"]], 
					"adderType": [hh["CORE_ADDER_TYPE"]],
					"in_0": [in_o],
					})

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

				res_r, res_w = SRAMBlock(h, hh, in_a)
				res = NetworkBlock(h, hh,ratio, in_a)
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

				res_r, res_w = SRAMBlock(h, hh, in_w)
				res = NetworkBlock(h, hh,ratio, in_w)
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

				res_r, res_w = SRAMBlock(h, hh, in_a)
				res = NetworkBlock(h, hh,ratio, in_a)
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
				res = MulticastBlock(h, hh, ratio, np.repeat(in_w,1), fanout = (pe//WEI_TILE)//ratio )

				units = WEI_TILE* ratio
				res = res['Total_Pwr']['res'][-1][-1] *units 
				powers[c] = {"NETWORK": res}	
			elif(component == "ACT_PE_CAST"):
				ratio = min(hh['CAST_RATIO']		, pe//ACT_TILE)
				fanout = (pe//ACT_TILE)//ratio	#this is the maximum fanout, the real fanout is actually lower, 'diagonal' fanout, we can assume worst case for now
				#i.e. in practice, it should be ~1 2 2 2 2 1, 
				#WORST:TN*TKX*TKY 
				#APPROX: 
				#print("ACT_CAST")
				#print(fanout, ratio)
				#print(ACT_TILE)
				#input()
				res = MulticastBlock(h, hh, ratio, np.repeat(in_a, ratio), fanout = (pe//ACT_TILE)//ratio )
				units = ACT_TILE*ratio #can multiply by the array size, not the entire ACT_TILE if there are diagnoal movements
				
				res = res['Total_Pwr']['res'][-1][-1] *units 
				powers[c] = {"NETWORK": res}	
				pass
	
			elif(component == "L2"):
				pwrs = []
				for busunit,in_0,tile in [("ACT_LOADER", in_a,ACT_TILE), ("OUT_LOADER", in_o,OUT_TILE), ("WEI_LOADER", in_w,WEI_TILE)]:

					if((hh['BIT_LEN']//hh['PREC']) > tile):
						ratio = (hh['BIT_LEN']//hh['PREC']) // tile
					else:
						ratio = -tile //( hh['BIT_LEN']//hh['PREC'])

					if(ratio < 0):
						side = abs(ratio)
					else:
						side = 1/abs(ratio)
					#hh['PREC'] = h['WEI_PREC']
					res_r, res_w = SRAMBlock(h, hh, in_0)
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


					res = NetworkBlock(h, hh,ratio, in_0)
					res = res['Total_Pwr']['res'][-1][-1] *units / hh['PREC']	

					
					pwrs.append((res_r, res_w,res))	
				powers[c] = {
					"BUS": pwrs}

				pass
	
		#print(bb,cycles, max([cycles[t] for t in cycles]))
		#print(bb, hp)
		print(bb)
		pprint(powers)# max([cycles[t] for t in cycles]))
		#print(bb, hp)






	pass
'''


