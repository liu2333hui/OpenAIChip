
def arch_analysis(arch):
	#from a given arch calculate the number of primitives and needed 
	ANALYSIS = {}
	
	# Go through each component and get the number of primitives
	g = arch["GENERAL"]
	TI = g['TI']
	TN = g['TN']
	TB = g['TB']
	TKX = g['TKX']
	TKY = g['TKY']
	TX = g['TX']
	TY = g['TY']
	
	#1.PE
	PE = {	
		"Multiplier2": {
			"number": TI*TN*TB*TKX*TKY*TX*TY,
			"config": arch["PE_ARRAY"]	
		}
	}
	ANALYSIS["PE"] = PE
			

	#2. ADDER_TREE
	ADDER_TREE_CONFIG = arch["ADDER_TREE"]
	ADDER_TREE_CONFIG.update({
		"terms": TI*TKX*TKY
	})
	ADDER_TREE = {
		"AdderN": {
			"number": TN*TB*TX*TY,
			"config": ADDER_TREE_CONFIG,
		}
	}
	ANALYSIS["ADDER_TREE"] = ADDER_TREE
	

	#3. ACCUMULATOR
	ACCUM_CONFIG = arch["ACCUMULATOR"]
	ACCUMULATOR_CONFIG = arch["ACCUMULATOR"]
	ACCUMULATOR_CONFIG.update({
		"terms": 1,
	})
	ACCUMULATOR = {
		"Accumulator": {
			"number": TN*TB*TX*TY,
			"config": ACCUMULATOR_CONFIG,
		}
	}
	ANALYSIS["ACCUMULATOR"] = ACCUMULATOR
	

	
	#4. BUFFERS
	WEI_BUF_CONFIG = arch["WEI_LOADER"]
	WEI_BUF = {
		"SRAM": {
			"number": TN*TB*TX*TY,
			"config": WEI_BUF_CONFIG,
		},
		"Network":{
			
		},
	}
	ANALYSIS["WEI_LOADER"] = WEI_BUF
	

def generate(analysis):
	#create json
	#send to sbt test:runMain units.SystolicUnit json_config	

if __name__ == "__main__":
	WEI_PREC = 8
	ACT_PREC = 8
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


