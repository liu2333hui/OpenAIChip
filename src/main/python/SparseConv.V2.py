from ArchTemplates import GeneralConvUnit, GeneralLinearUnit, generate_cpp, dict_to_str,filter_loop_order
import copy

import numpy as np
import paddle.nn as nn
import pandas as pd
import paddle

from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive
	




class SparseConv(SystolicConv):

	def get_primitive_statistics(self, hc):
		super.get_primitive_statistics(self, hc)	

		self.MODULES = {}	

		net = hc["VALID_NETS"]
		ADDER_TREE_UNITS = self.hc["TN"] * self.hc["TB"]* self.hc["TX"]* self.hc["TY"]
		INNER_GROUP = self.hc["TKX"]*self.hc["TKY"]*self.hc["TI"]

		WEIGHT_SIZE = lambda p: p['FILTER_KX']*p['FILTER_KY']*p['INPUT']*p['OUTPUT'] 

		MAC_NO = lambda p: p['FILTER_KX']*p['FILTER_KY']*p['INPUT']*p['OUTPUT']*p["INPUT_X"]*p["INPUT_Y"]*p["BAT"] 

		ACT_SIZE = lambda p: p["INPUT_KX"]*(p["INPUT_X"] - p['FILTER_KX'] + 1)*p['FILTER_KY']*(p["INPUT_Y"]-p["FILTER_KY"] +1)*p['INPUT']*p["BAT"] 

		OUTPUT_SIZE =  lambda p: p["INPUT_X"]*p["INPUT_Y"]*p['OUTPUT']*p["BAT"] 

		
		L1_OUT_BUF_BIT_LEN = (self.hc["TN"]*self.hc["TB"]*self.hc["TX"]*self.hc["TY"])#//*self.hc["WEI_PREC"])//self.hc["INTERCONNECT_OUT_SYSTOLIC_LOAD_RATIO"]
		L1_OUT_BUF_UNITS = L1_OUT_BUF_BIT_LEN #// self.hc["L1_OUT_SRAM_SIZE"][0]



		#If INTER-PE enabled, ACT_SIZE is 
		INTER_PE_ACT_SIZE = lambda p: p["INPUT_X"]*p["INPUT_Y"]*p['INPUT']*p["BAT"] 
		#If INTER-PE enabled, more power is spent on the interconnect
		#this can be done at the L2->L1, or L1->PE level. Which one is better ? Preferably closer to PE otherwise L1 loading a lot more
		# --> after L1, --> DATA1, DATA2 (i.e. generally two tiles needed, so need a Parallel2Serial
		# Then, D1D2 --> get the strided input (i.e. d1d2 d3d4 --> d2d3, shift register by TX)
		# Then shift in the next DATA3, until end.., (i.e. d3d4 d5d6 --> d3d4, d4d5)
		# OUtput is a parallel2Serial, d1d2d3d4 --> d1d2,

		# D1 D2 --> (d1d2)d3d4 --> (d2d3)d4 --> (d3d4)

		# (d1d2) d3d4 d5d6 d7d8 d9d10    VS     (d1d2) d3d4 , d3d4 d5d6 , d5d6 d7d8
		# regs 5                         ,        2
		#      this is a shifter !
		#      Serial2Serial   (in_terms, shift_terms, out_terms)
		#      


		L1_WEI_BUF_BIT_LEN = (self.hc["TI"]*self.hc["TN"]*self.hc["TKX"]*self.hc["TKY"])#*self.hc["WEI_PREC"])//self.hc["INTERCONNECT_WEI_SYSTOLIC_LOAD_RATIO"]
		L1_WEI_BUF_UNITS = L1_WEI_BUF_BIT_LEN #// self.hc["L1_WEI_SRAM_SIZE"][0]
		
		TILE = self.hc["TI"]*self.hc["TN"]*self.hc["TKX"]*self.hc["TKY"]*self.hc["TX"]*self.hc["TY"]*self.hc["TB"]


		L1_ACT_BUF_BIT_LEN = self.hc["TI"]*self.hc["TB"]*(self.hc["TKX"] + self.hc["TX"]-1)*(self.hc["TKY"]+self.hc["TY"]-1)
	

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
					"input_bins": [MULT_prec1, MULT_prec2],	
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
		if("L1_WEI_READ" in net):
			self.MODULES.update({
				"L1_WEI_READ": {
					"loop_order": self.hc["LOOP_ORDER"],
					"cast_skips": ["TX","TY","TB"],
					"runtime": lambda p: MAC_NO // L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],

					"units": L1_WEI_BUF_BIT_LEN,
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
					"units": L1_WEI_BUF_BIT_LEN,
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
					'cur_update': ['inputs_data', f'{self.hc["TN"]}*std::min({self.hc["TKX"]} - std::abs(x - {self.hc["TKX"]} + 1) , {self.hc["TKX"]})* std::min({self.hc["TKY"]} - std::abs(y - {self.hc["TKY"]} + 1) , {self.hc["TKY"]})'],
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
						"primitive": "networks.parallel2serial",
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
					"units": L1_WEI_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['weights_data'],
					'input_group': 1,

					"unit_time_unrolled": [ ratio  ],
				},
			}
			# meaning small2big at read, so write big2small, serializer 
			if(ratio > 0): #meaning big to small
				config.update({	
					"config": {
						"primitive": "networks.parallel2serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": 1,
						}
					})	
			else:
				config.update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": 1,
						}
					})	
			self.MODULES.update(config)




		if("L1_ACT_READ" in net):
			self.MODULES.update({
				"L1_WEI_READ": {
					"loop_order": self.hc["LOOP_ORDER"],
					"cast_skips": ["TN"],
					"runtime": lambda p: MAC_NO // L1_ACT_BUF_BIT_LEN * p['avg_cycle_per_op'],
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
						"mode": 0,#0 is read, 1 is write
					}
				},

			})
		if("L1_ACT_WRITE" in net):
			self.MODULES.update({
				"L1_ACT_WRITE": {	
					"loop_order" :filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "KX", "KY", "N", "I"]),
					#"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: p['FILTER_KX']*p['FILTER_KY']*p['INPUT']*p['OUTPUT']// L1_WEI_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["inputs_obj"],	
	
					"units": L1_WEI_BUF_BIT_LEN,
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




		if("L1_OUT_WRITE" in net):
			self.MODULES.update({
				"L1_OUT_WRITE": {
					"loop_order": filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "N"]),
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


		if("L1_OUT_READ" in net):
			self.MODULES.update({
				"L1_OUT_READ": {
					"loop_order": filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "N"]),
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



		if("L1_OUT_WRITE_NETWORK" in net):
			ratio = self.hc["LOAD_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"L1_OUT_WRITE_NETWORK": {	
					"loop_order" : filter_loop_order(self.hc["LOOP_ORDER"], ["X", "Y", "N", "B"]),
					#"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: OUTPUT_SIZE(p) // L1_OUT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["outputs_obj"],		
					"units": L1_OUT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['outputs_data'],
					'input_group': 1,

					"unit_time_unrolled": [ -ratio  ],
				},
			}
			# meaning small2big at read, so write big2small, serializer 
			if(ratio < 0): #meaning we are small to big, Deserializer. But switch at write.
				config["L1_OUT_WRITE_NETWORK"].update({	
					"config": {
						"primitive": "networks.parallel2serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": 1,
						}
					})	
			else:
				config["L1_OUT_WRITE_NETWORK"].update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": 1,
						}
					})	
			self.MODULES.update(config)

		if("L1_OUT_READ_NETWORK" in net):
			ratio = self.hc["LOAD_RATIO"]
			prec = self.hc["PREC"]
			typ  = self.hc["NETWORK_TYPE"]
			config = {
				"L1_OUT_READ_NETWORK": {	
					"loop_order" : self.hc["LOOP_ORDER"],
					"cast_skips": ["TB", "TX", "TY"],
					"runtime": lambda p: OUTPUT_SIZE(p) // L1_OUT_BUF_BIT_LEN * p['avg_cycle_per_op'],
					"data_obj": ["weights_obj"],		
					"units": L1_OUT_BUF_BIT_LEN,
					"input_metadata": {"toggles": {"update": "1"}},#j"bits": {	
					"input_bins": [self.hc["PREC"]],	
					'cur_update': ['weights_data'],
					'input_group': 1,

					"unit_time_unrolled": [ ratio  ],
				},
			}
			# meaning small2big at read, so write big2small, serializer 
			if(ratio > 0): #meaning big to small
				config.update({	
					"config": {
						"primitive": "networks.parallel2serial",
						"hardwareType": typ,
						"prec": prec,
						"terms": abs(ratio),
						"fanout": 1,
						}
					})	
			else:
				config.update({	
					"config": {
						"primitive": "networks.Deserializer",
						"hardwareType": typ,
						"prec": prec,
						"out_terms": abs(ratio),
						"fanout": 1,
						}
					})	
			self.MODULES.update(config)





		#Lets SKIP L2 for now. .. because it is ... in some ways redundant or similar to L1.., only useful for multiple tilings flow, maybe we can add it for interest

		#from Out buffer
		if("L2_OUT_WRITE" in net):
			#is a bus connection, so there is some arbitration, switch between L1_WEI_BUF and L1_ACT_BUF
			L2_BUF_BIT_LEN = max(L1_ACT_BUF_BIT_LEN, L1_WEI_BUF_BIT_LEN)
			#i.e. L1_WEI = 64
			#i.e. L1_ACT = 16
			#i.e. L2     = 64
			#i.e. unroll = INTERCONNECT_LOAD_RATIO* 1, INTERCONNECT_LOAD_RATIO*-4
			#self.hc["INTERCONNECT_L2_SYSTOLIC_LOAD_RATIO"]*m
	
			L2_BUF_UNITS = L2_BUF_BIT_LEN #// self.hc["L2_SRAM_SIZE"][0]
			
	
			self.MODULES.update({

			})
		if("L2_WEI_READ" in net):
			self.MODULES.update({

			})
		if("L2_ACT_READ" in net):
			self.MODULES.update({

			})
		#from DRAM
		if("L2_ACT_WRITE" in net):
			self.MODULES.update({

			})
		if("L2_WEI_WRITE" in net):
			self.MODULES.update({

			})
		if("L2_WEI_WRITE" in net):
			self.MODULES.update({

			})
		if("OUTPUT_DRAM_L2_BUS" in net):
			self.MODULES.update({

			})
		if("L2_L1_BUS" in net):
			self.MODULES.update({

			})
		#missing ACCUMULATOR, ADDER TREE?

		#INTER_X = self.hc["INTERCONNECT_ACT_INTER_PE_X"]
		#INTER_Y = self.hc["INTERCONNECT_ACT_INTER_PE_Y"]
		#meaning we only save the weights once, the rest will be passed onto 
		#x1 x2 x3 x4
		# x1 x2 x3 --> casted, x1 x2, x2 x3
		# without inter-pe, next cycle
		# x2 x3 x4 --> casted, x2 x3, x3 x4
		# see that x2 x3 are read again!
		#if(INTER_X):
		#	TX = self.hc["TX"]	
		#else:
		#	TX = self.hc["TKX"]+self.hc["TX"]	
		#if(INTER_Y):
		#	TY = self.hc["TY"]	
		#else:
		#	TY = self.hc["TKY"]+self.hc["TY"]		
	
	






		#HARDWARES: L1_ACT_BUFFER
		#Assume L2 is a shared buffer
		#i.e. L1_row_len = 128
		#i.e. L2_row_len = 64
		#HARDWARES: L2_BUFFER
		#HARDWARE: L2_L1_BUS_READ_WEI
		#HARDWARE: L2_L1_BUS_WRITE_WEI
		#HARDWARE: L2_L1_BUS_READ_OUT
		#HARDWARE: L2_L1_BUS_WRITE_OUT
		#HARDWARE: L2_L1_BUS_READ_ACT
		#HARDWARE: L2_L1_BUS_WRITE_ACT
		# ---> we can use a multicast primitive to model this, fanout = 1, terms = BUS_LEN (i.e. L1 len)
		# ---> 
		# bus is a 1-->2 connection, parallel2serial generall because L2 >= L1	

		
	



	def prepare_data(self, params):
		#convolution data

		input_data = params['input_data']
		weights = params['weight']

		#convolution prepare
		#input_data = input_data[0] #if is tuple
		OUT =  weights.shape[0]
		IN = weights.shape[1]
		KX = weights.shape[2]
		KY = weights.shape[3]

		BAT = input_data.shape[0]
		input_IN = input_data.shape[1]
		X = input_data.shape[2]
		Y = input_data.shape[3]
		#print(input_data.shape)
		#print(weights.shape)
		assert(input_data.shape[1] == weights.shape[1])
		
		#quantize (fixed point)
		#(todos) some algorithm to choose the scaling ?
		WEI_PREC = self.hc.get('WEI_PREC', self.hc["PREC"])
		ACT_PREC = self.hc.get('ACT_PREC', self.hc["PREC"])
		weights    = ((weights*256*256) %WEI_PREC).astype(np.int32)
		input_data = ((input_data*256*256) %ACT_PREC).astype(np.int32)
		#Randomize weights and inputs (TODOS)
		Randomize = params["SIM_PARAMS"]["Randomize"]
		Wei_Sparsity = params["SIM_PARAMS"]["Wei_Sparsity"]
		Act_Sparsity = params["SIM_PARAMS"]["Act_Sparsity"]
		name = params["SIM_PARAMS"]["name"]
		root = params["SIM_PARAMS"]["root"]

		np_save= params['SIM_PARAMS']['save_np']
	

		#Randomize weights and inputs (TODOS)
		if(Randomize):
			n = IN*OUT*KX*KY
	
			k = int(n*Wei_Sparsity)
			rand_wei = np.random.randint(0, 1<< WEI_PREC, size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_wei[zero_indices] = 0
			
			n = IN*BAT*X*Y
	
			k = int(n*Act_Sparsity)
			rand_act = np.random.randint(0, 1<<ACT_PREC, size=n)
			zero_indices = np.random.choice(n, k, replace=False)
			rand_act[zero_indices] = 0
			
			weights = rand_wei.reshape((OUT, IN, KX, KY))
			input_data = rand_act.reshape((BAT, IN, X, Y))
		
		w_file = root+"/"+name+".weights.txt"
		i_file = root+"/"+name+".input.txt"
		if(np_save):
			weights = rand_wei.reshape((-1))#OUT, IN, KX, KY))
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))
	
			np.savetxt(w_file, weights, fmt='%d', delimiter='\n')
			np.savetxt(i_file, input_data, fmt='%d', delimiter='\n')
			weights = rand_wei.reshape((-1))#OUT, IN, KX, KY))
			input_data = rand_act.reshape((-1))#BAT, IN, X, Y))
	
			weights = rand_wei.reshape((OUT, IN, KX, KY))
			input_data = rand_act.reshape((BAT, IN, X, Y))


		self.LOOP_VAR_DEFINITIONS = {
			"N": {"LIM": "OUT","STRIDE": 1,"GROUP": "OUTER"},
			"I": {"LIM": "IN" ,"STRIDE": 1, "GROUP": "INNER"},
			"KX":{"LIM": "FILTER_KX","STRIDE": 1,"GROUP": "INNER"},
			"X":{"LIM": "INPUT_X", "STRIDE": params['stride'][0], "GROUP": "OUTER"},
			"Y":{"LIM": "INPUT_Y", "STRIDE": params['stride'][1], "GROUP": "OUTER"},
			"KY":{"LIM": "FILTER_KY","STRIDE":1,"GROUP": "INNER"},
			"B": {"LIM": "BAT" ,"STRIDE": 1, "GROUP": "OUTER"},	
		}



		return {
			"params":{
				"IN": IN,
				"OUT": OUT,
				"BAT": BAT,	
				"FILTER_KX": KX, 
				"FILTER_KY": KY,
				"INPUT_X": X,
				"INPUT_Y": Y,
			},
			"weights_obj": 
				{
				"name": "weights",
				"file": w_file,
				"size": len(weights.reshape((-1))),
				"indexing": "n*IN*FILTER_KX*FILTER_KY+i*FILTER_KX*FILTER_KY+ky*FILTER_KX+kx"
			},
			"inputs_obj":
				{
				"name": "inputs",
				"file": i_file,
				"size": len(input_data.reshape((-1))),
				"indexing": "b*IN*INPUT_X*INPUT_Y+i*INPUT_X*INPUT_Y + y*INPUT_X + x"	
			},
		}
	

	
		
	def infer(self, params):
		self.get_primitive_statistics(self.hc)

		p = params
		p.update(self.prepare_data(p))

		results = []
		
		VALID_NETS = self.hc['VALID_NETS'] 

		for NET in VALID_NETS:
			NET_META = self.MODULES[NET]#"L1_WEI_READ"]
			PARAMETERS = params['params']
			DATA = [
				params[obj]
				for obj in NET_META['data_obj']
			]
			NET_DATA = {
				NET: NET_META #self.MODULES["L1_WEI_READ"]
			}	
			#skip casting
			skips = NET_META.get('cast_skips', [])#["TB", "TX", "TY"]#["TB"]#["TB", "TX", "TY"]
			#self.MODULES["L1_WEI_READ"]['skips'] = skips
			LOOP_ORDER = NET_META.get('loop_order',self.hc["LOOP_ORDER"])
			LOOP_VAR_DEFINITIONS = NET_META.get("loop_var", self.LOOP_VAR_DEFINITIONS)
			hooks = NET_META.get('hooks', {})#self.MODULES["PE_ARRAY"]["hooks"]
			name = params["SIM_PARAMS"]["name"]
			root = params["SIM_PARAMS"]["root"]
			output_files= generate_cpp(root, name, PARAMETERS, DATA, NET_DATA, LOOP_ORDER, LOOP_VAR_DEFINITIONS,tiling_pre="T",hardware_config= self.hc, SIM_CYCLE_LIM = params['SIM_PARAMS']['SIM_CYCLES'], hooks = hooks, run_it = params['SIM_PARAMS']["RUN_CPP"], need_trace = params['SIM_PARAMS']['GEN_TRACE'] , inner_loops_skips = skips)

			#output_files['cycles'] 
			#return output_files
			results.append(output_files)	


		#arithmetic
		#results.append(self.infer_pe(p))
		#results.append(self.infer_adder_accum(p))
		#memory
		#results.append(self.infer_L1_WEI_buffers(p))
		#lianjie
		#results.append(self.infer_interconnect(p))
		return results


#MODE: TRACE, TIME, GOLD, OUR, B1, B2	
def core(test_id = 0, MODE = "TRACE", inputs = {}, benchmark = {}):	

	

	#print(benchmark)
	SIM_PARAMS = benchmark["SIM_PARAMS"]
	network_layer = benchmark['network_layer']
	mapping = benchmark['mapping']	


	hc = inputs
	

	VU = hc["VALID_UNITS"] #should only be one unit

	hardware_config = dict(hc["GENERAL"])
	
	assert(len(VU) == 1)
	for kk in hc:
		if(kk in VU):
				#print(idx,c[kk])
				hardware_config.update(hc[kk])
				pass
	
	#exclude VALID_NETS
	EXCLUDE = ["VALID_NETS"] + [k for k in hc["GENERAL"]]
	hardware_config_filtered = {k: v for k, v in hardware_config.items() if k not in EXCLUDE }	
	#print(hardware_config)
	#exit()

	#/generated/Arch/SparseConv/GeneralConfic
	design = dict_to_str(hc["GENERAL"]) + "/" + VU[0]  + "/" + dict_to_str(hardware_config_filtered)

	SIM_PARAMS['name'] = network_layer['layer_name']
	SIM_PARAMS["root"] = f"generated/Arch/SparseConv/{design}"	
	SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])



	
	if(MODE == "GOLD"):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
	if(MODE == "TRACE"):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True

	if("DEBUG" in MODE):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True


	if(MODE == "GOLD_TRACE"):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = True
		SIM_PARAMS['save_np'] = True


	if(MODE == "OUR"):
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
	if(MODE == "B1"):#MAESTRO-like (i.e. fixed)
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False
	if(MODE == "B2"):#Accelergy-like (i.e. finite states)
		SIM_PARAMS['GEN_TRACE'] = True
		SIM_PARAMS['RUN_CPP'] = False
		SIM_PARAMS['save_np'] = False	

	#print(SIM_PARAMS)
	#print(hardware_config)
	#print(mapping)
	#print(network_layer)
	
	#input("SIM_PARAMS OK?")
	#FLOW 1. compare against baselines and 
	ld =  SparseConv(hardware_config)
	traces = ld.gen_perf_trace(network_layer,mapping, SIM_PARAMS) 
		
	if("DEBUG" in MODE):
		input("TRACE DONE: CONTINUE?")
	if( "GOLD" in MODE ):	
		print("GENERATE_POWER")
		ld.estimate_golden_pwr(traces, network_layer,mapping, SIM_PARAMS)

		if("DEBUG" in MODE):
			input("GOLD DONE: CONTINUE?")
	
	if("TIME" in MODE):
		ld.estimate_runtime(traces, network_layer, mapping, SIM_PARAMS)	
		if("DEBUG" in MODE):
			input("TIME DONE: CONTINUE?")
	

	if("OUR" in MODE):
		ld.estimate_our_pwr_v1(traces,network_layer,mapping, SIM_PARAMS)	
		if("DEBUG" in MODE):
			input("OUR DONE: CONTINUE?")
	

	if("OUR2" in MODE):
		ld.estimate_our_pwr(traces,network_layer,mapping, SIM_PARAMS)

	if("B1" in MODE):
		ld.estimate_b1_pwr(traces,network_layer, mapping,SIM_PARAMS)#maestro
		if("DEBUG" in MODE):
			input("B1 DONE: CONTINUE?")
	

	if("B2" in MODE):
		ld.estimate_b2_pwr(traces, network_layer,mapping,SIM_PARAMS)#accelergy 


	if("COMPARE" in MODE):
		ld.analyze_results(traces, network_layer,mapping, SIM_PARAMS)
		if("DEBUG" in MODE):
			input("COMPARISON DONE: CONTINUE?")
	
	#ld.estimate_b3_pwr(traces, network_layer,mapping,SIM_PARAMS)#others?
if __name__ == "__main__2":
	import sys
	
	MODE = sys.argv[-1]
	print(MODE)
	input("MODE OK?")
	core(MODE = MODE)






#THe experiment where we compare our power model against baselines
def run_fig6(base_hardware_config, base_mapping, base_network_layer, base_SIM_PARAMS, VALID_UNITS):

	#test cases
	combos = []
	
	sparse_combos = []
	for     tb,tn,  ti,tx, ty,tkx,tky in [
		#64 pe case
		[1, 8,   8,1,  1,  1,1],
		[1, 8,   8,1,  1,  1,1],
	
		[1, 4,   4,2,  2,  1,1],
 		[1, 4,   4,1,  1,  2,2],
 		[1, 4,   4,2,  1,  2,1],
  		[1, 2,   2,2,  2,  2,2],
  		[2, 1,   2,2,  2,  2,2],
  		[1, 16,  4,1,  1,  1,1],  
  		[1, 4,  16,1,  1,  1,1],   
 
		#	[1,16,  16,1,  1,  1,1],
        	#	[1,8,  8,1,  1,  2,2],
        	#	[1,8,  8,1,  2,  1,2],	
        	#	[1,16,  4,1,  2,  1,2],	
        		#	[1,4,  16,2,  2,  1,2],			
        		#	[2,4,  8,2,  2,  1,1],			
	       		#	[2,2,  16,2,  2,  1,1],			
	       		#	[1,8,  32,1,  1,  1,1],			
				]:	
		for lp in [ 
				["B", "N", "I", "KX", "KY", "X", "Y"],
				["B", "N", "Y", "X", "I", "KX", "KY"],
				["B", "Y", "X", "KY", "KX", "I", "N"],
				["B", "Y", "X", "KY", "KX", "N", "I"],	
				["KY", "KX", "I", "X", "Y", "B", "N"],
				["I", "N", "KX", "KY", "Y", "X", "B"],
				["B", "N", "I", "X", "Y", "KX", "KY"],	
				["B",  "KX", "KY",  "N", "I","X", "Y", ],	
	
		      ]:
			for side in ['weights', 'inputs', 'both']:
	
				for sparse_ratio in [1, 2, 4, 8, 16]:
					if(sparse_ratio > ti*tkx*tky):
						continue
								
					sparse_combos.append([tb,tn,  ti,tx, ty,tkx,tky , lp, side, sparse_ratio])


	

	big_loop = -1
	BIG_LOOP_SAMPLE = 30
	for tb,tn,  ti,tx, ty,tkx,tky , lp, side, sparse_ratio in sparse_combos:
		if 1:
			big_loop = big_loop +1
			if(big_loop > BIG_LOOP_SAMPLE):
				continue

			#hc = dict(base_hardware_config)
			hc = copy.deepcopy(base_hardware_config)	
	
			hc["GENERAL"]["TB"] =  tb
			hc["GENERAL"]["TI"] =  ti
			hc["GENERAL"]["TN"] =  tn
			hc["GENERAL"]["TX"] =  tx
			hc["GENERAL"]["TY"] =  ty
			hc["GENERAL"]["TKX"] =  tkx
			hc["GENERAL"]["TKY"] =  tky		
			hc["GENERAL"]["LOOP_ORDER"] = lp

			hc["GENERAL"]["SPARSE_SIDE"] = side
			hc["GENERAL"]["SPARSE_RATIO"] = sparse_ratio

			#print(hc)
			#if(big_loop > 0):
			#print(combos[0])

			#NAIVE would have had total of 16 x 16 x 14 x 14 x 80 = 4,014,080  4 million already!
			#with 8 x 8 = 64 OUTER combinations --> 256 million !
			# Total Combos = 16 + 16 + 14 + 14 + 80 = 140
			#with outer combinations --> 140 
			# Total Combos = 8960 only, much better
				
			#WEI_LOADER variations
			# 2 x 4 x 2 = 16
			Flag = False
			sample = 0
			unit = "WEI_LOADER"
			SAMPLE = 10

			if(unit in VALID_UNITS):
				for wei_network in ["Mux", "Shift"]:
					for load_ratio in [1, 4, 16, 64]:
						for wei_prec in [8, 16]:
							if(Flag):
								continue

							#h = dict(hc)	
							h = copy.deepcopy(hc)	
	

							h[unit]["PREC"] = wei_prec
							h[unit]["NETWORK_TYPE"] = wei_network
							h[unit]["LOAD_RATIO"] = load_ratio
							h["VALID_UNITS"] = [unit]#hc[unit]["VALID_UNITS"]		
					
							h["VALID_NETS"] = hc[unit]["VALID_NETS"]

							combos.append(h)							
							#print("WEI_LOADER")
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True

			'''
			print("COMBOS",len(combos))
			for idx,c in enumerate(combos):
				#print(c)
				VU = c["VALID_UNITS"]
				print(idx, VU)
			'''


			#ACT_LOADER variations
			#16
			Flag = False
			sample = 0
			unit = "ACT_LOADER"
			SAMPLE = 10

			if(unit in VALID_UNITS):			
				for act_network in ["Mux", "Shift"]:
					for act_load_ratio in [1, 4, 16, 64]:
						for act_prec in [8, 16]:
							if(Flag):
								continue
							#h = dict(hc)	
							h = copy.deepcopy(hc)	
	

	
							h[unit]["PREC"] = act_prec
							h[unit]["NETWORK_TYPE"] = act_network
							h[unit]["LOAD_RATIO"] = act_load_ratio	
							h["VALID_UNITS"] = [unit]#hc[unit]["VALID_UNITS"]		
	
							h["VALID_NETS"] = h[unit]["VALID_NETS"]
							combos.append(h)							
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True

			'''
			print("COMBOS",len(combos))
			for idx,c in enumerate(combos):
				print("keys",c.keys())
				VU = c["VALID_UNITS"]
				#print(idx, VU, VALID_UNITS)
			'''



			#OUT_LOADER variations (todos)
						

			#WEI_PE_CAST	
			#2 x 7 = 14
			Flag = False
			sample = 0
			unit = "WEI_PE_CAST"
			SAMPLE = 10
			if(unit in VALID_UNITS):	
				for wei_prec in [8, 16]:
					for ratio in [1, 2, 4, 8, 16, 32, 64]:
						for network in ["Mux", "Shift"]:
	
							if(Flag):
								continue
	
							if(tb*tx*ty < ratio):
								continue
							#h = dict(hc)	
							h = copy.deepcopy(hc)	
	

		
							h["VALID_UNITS"] = [unit]#h[unit]["VALID_UNITS"]		
	
							h[unit]["PREC"] =wei_prec
							h[unit]["CAST_RATIO"] =ratio	
							h[unit]["NETWORK_TYPE"] = network

							h["VALID_NETS"] = h[unit]["VALID_NETS"]
							combos.append(h)							
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True	
						
			#ACT_PE_CAST
			#2 x 7 = 14
			Flag = False
			sample = 0
			unit = "ACT_PE_CAST"
			SAMPLE = 10
			if(unit in VALID_UNITS):
				for prec in [8, 16]:
					for ratio in [1, 2, 4, 8, 16, 32, 64]:
						for network in ["Mux", "Shift"]:
	
							if(Flag):
								continue
	
							if(tb*tx*ty < ratio):
								continue
							h = copy.deepcopy(hc)	
	

							#h = dict(hc)	
		
							h["VALID_NETS"] = h[unit]["VALID_NETS"]		
							h["VALID_UNITS"] = [unit]#h[unit]["VALID_UNITS"]			
	
							h[unit]["PREC"] = prec
							h[unit]["CAST_RATIO"] = ratio	
							combos.append(h)							
							sample = sample + 1
							if( sample >= SAMPLE):
								Flag = True	
	
												
			#L2 variations (todos)


			#PE Array variations
			#2 x 2 x 5 x (1 + 3) = 80
			Flag = False
			sample = 0
			unit = "PE_ARRAY"
			SAMPLE = 10			
			hc["VALID_UNITS"] = [unit]#hc[unit]["VALID_UNITS"]		
			if(unit in VALID_UNITS):
				for wei_prec in [8, 16]:
					for act_prec in [8, 16]:
						for radix_root in [1, 2, 4, 8, 16]:
							radix = 1<<radix_root
							if(radix_root > wei_prec or radix_root > act_prec):	
								continue

							for mult_type in ["HighRadixMultiplier", "BitSerialMultiplier"]:	
								if(Flag):
									continue
	
								if(mult_type == "BitSerialMultiplier"):	
									for side in ['weights', 'acts', 'both']:
										if(Flag):
											continue
	
										h = copy.deepcopy(hc)	
										h[unit]["WEI_PREC"] = wei_prec
										h[unit]["ACT_PREC"] = act_prec
										h[unit]["RADIX"] = radix
										h[unit]["MULT_TYPE"] =  mult_type
										h[unit]["SIDE"] = side		
		
										h["VALID_NETS"] = h[unit]["VALID_NETS"]		
										h["VALID_UNITS"] = [unit]#h[unit]["VALID_UNITS"]			
	
										combos.append(h)							
										sample = sample + 1

										#print(sample)
										#print(len(combos))
										#print(sample)
										#print(len(combos), Flag)
	
										for idx,c in enumerate(combos):
											VU = c["VALID_UNITS"]
											#print(idx,VU)

											for kk in c:
												if(kk in VALID_UNITS):
													#print(idx,c[kk])
													pass



		
										if( sample >= SAMPLE):
											Flag = True	
	

								elif(mult_type == "HighRadixMultiplier"):	
									h = copy.deepcopy(hc)	
	
									h[unit]["WEI_PREC"] = wei_prec
									h[unit]["ACT_PREC"] = act_prec
									h[unit]["RADIX"] = radix
									h[unit]["MULT_TYPE"] =  mult_type
	
									combos.append(h)												
									sample = sample + 1

									#print(sample)
									#print(len(combos), Flag)
									for idx,c in enumerate(combos):
										VU = c["VALID_UNITS"]
										#print(idx,VU)

										for kk in c:
											if(kk in VALID_UNITS):
												#print(idx,c[kk])
												pass



									if( sample >= SAMPLE):
										Flag = True	
										
	#print(combos)
	NUM = int(sys.argv[-1])
	
	
	print(len(combos))
	for idx,c in enumerate(combos):
		#print(c)
		VU = c["VALID_UNITS"]
		print(idx, c["GENERAL"])
		print(idx,VU)

		for kk in c:
			if(kk in VALID_UNITS):
				print(idx,c[kk])
				pass

		#if(idx > NUM):
		#exit()

	if("DEBUG" in MODE):
		input("COMBOS OK?")	

	benchmarks = []
	
	for Wei_Sparsity in [0.1, 0.8]:
		for Act_Sparsity in [0.1 ,0.8]:	
			for batch, in_channels, out_channels, kernel_size, stride, X, Y in [
			     #[4    ,   32,         64,            3,         1,    32, 64],
#         	             [4    ,   3,         64,            7,         2,    32, 64],
			     [4    ,   64,         64,            5,         2,    32, 64],
		   	     [4    ,   8,         8,            3,         1,    32, 32],
			     [4    ,   32,         32,            1,         1,    32, 32],
			     #[4    ,   8,         16,            1,         1,    16, 32],	
	
			]:	

				for SIM_CYCLES in [10]:#, 100]:
					
					benchmark = {
									'SIM_PARAMS': dict(base_SIM_PARAMS),
									'network_layer': dict(base_network_layer),
									'mapping': dict(base_mapping)
								}
		
					benchmark["SIM_PARAMS"]["Randomize"] = 1
					benchmark["SIM_PARAMS"]["Wei_Sparsity"] = Wei_Sparsity
					benchmark["SIM_PARAMS"]["Act_Sparsity"] = Act_Sparsity
					benchmark["SIM_PARAMS"]["SIM_CYCLES"] = SIM_CYCLES
					benchmark["SIM_PARAMS"]["MODE"] = MODE
	
	
					input_data = paddle.randn([batch, in_channels, X, Y])
					layer = nn.Conv2D(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride = stride)#skip bias for now
	
					output_data = layer(input_data) 	
					repr_str = repr(layer)
					weight_name = repr(layer).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")
					input_name = repr(input_data.shape).replace("(", "_").replace(")", "_").replace(",", "_").replace("=", "_").replace(" ", "_").replace("]","_").replace("[","_")
	
					network = {
								"input_data" :input_name,
								"layer": weight_name,	
								}
		
								#print(layer)
					network_layer = {
									"layer_name": dict_to_str(network),#"Conv1",
									"layer": layer,
									"input_data": input_data,
									"output_data": output_data,
								}
	
					#print(network)
					#print(network_layer)
					benchmark["network_layer"] = network_layer
					benchmarks.append(benchmark)
	
	
	'''
	combos = [base_hardware_config] + combos
	benchmarks = [ {
		'SIM_PARAMS': base_SIM_PARAMS,
		'network_layer': base_network_layer,
		'mapping': base_mapping,
		}] + benchmarks
	'''	

	tested = -1
	HW_NUM = int(sys.argv[-1])
	BENCH_NUM = int(sys.argv[-4])
	for inputs in combos:
		tested += 1
		if(tested < int(sys.argv[-3])):
			continue
		for benchmark in [benchmarks[i] for i in range(BENCH_NUM)]:
			core(tested, inputs=inputs, benchmark=benchmark, MODE=MODE)	
		#tested += 1
		if(HW_NUM > 0 and tested > HW_NUM):
			exit()	










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

			"SPARSE_RATIO": 4,
			"SPARSE_SIDE": "weights",
	
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
			"ADDER_TREE_CORE_ADDER_TYPE": "SimpleAdder2",
			"ADDER_TREE_TYPE": "AdderTreeN",#AdderTree, i.e. Accumulator
			"ADDER_TREE_PREC": 16,
			"ADDER_TREE_DEPTH": 1, #i.e. number of cycles to output	
		},	
		"ACCUMULATOR": {
			"VALID_NETS": ["ACCUMULATOR"],
			"TYPE": "AccumulatorN",
			"CORE_ADDER_TYPE": "SimpleAdder2",
			"ACCUM_PREC": 32,
		},
		"WEI_LOADER": {
			"VALID_NETS": ["L1_WEI_READ", "L1_WEI_WRITE", "L1_WEI_WRITE_NETWORK", "L1_WEI_READ_NETWORK"],
			#"VALID_NETS": ["L1_WEI_READ", "L1_WEI_WRITE"],#"L1_WEI_WRITE_NETWORK", "L1_WEI_READ_NETWORK"],
	
			"L1_WEI_SRAM_SIZE": [16, 256],
			"L1_WEI_SRAM_TYPE": "Reg",
			"L1_WEI_TOTAL_SIZE" : 48000,		
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers	
			"LOAD_RATIO": 1,			
			"PREC": 8,

			"WEIGHT_COMPRESSION": "none",

		},
		"ACT_LOADER": {
			"VALID_NETS": ["L1_ACT_READ", "L1_ACT_WRITE", "L1_ACT_WRITE_NETWORK", "L1_ACT_READ_NETWORK"],	
			"L1_ACT_SRAM_SIZE": [16, 256],	
			"L1_ACT_SRAM_TYPE": "Reg",		
			"L1_ACT_TOTAL_SIZE" : 48000,	
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers
			"LOAD_RATIO": 1,		
			"PREC": 8,
			"INPUT_COMPRESSION" : "none",

		},
		"OUT_LOADER": {	
			"VALID_NETS": ["L1_OUT_READ", "L1_OUT_WRITE", "L1_OUT_WRITE_NETWORK", "L1_OUT_READ_NETWORK"],		
			"L1_OUT_SRAM_SIZE": [8, 64],
			"L1_OUT_SRAM_TYPE": "Reg",
			"L1_OUT_TOTAL_SIZE" : 48000,
			"NETWORK_TYPE": "Mux",#mux based or shift serializer/deserializers	
			"LOAD_RATIO": 1,	
			"PREC": 16,
			"OUTPUT_COMPRESSION": "none",

		},
		"WEI_CROSSBAR": {
			"VALID_NETS": ["WEI_CROSSBAR"],
			"PREC": 8,
			"WEI_CROSSBAR_TYPE": "Full",
		},
		"ACT_CROSSBAR": {
			"VALID_NETS": ["ACT_CROSSBAR"],
			"PREC": 8,
			"ACT_CROSSBAR_TYPE": "Full",
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
	VALID_UNITS = ["PE_ARRAY", "WEI_LOADER", "ACT_LOADER"]#["WEI_PE_CAST"]#[k  for k in  base_hardware_config] #["PE_ARRAY"]  #[,"WEI_LOADER"]#, "WEI_PE_CAST", "ACT_PE_CAST"]#[k  for k in  base_hardware_config]#["PE_ARRAY"]
	
	#VALID_UNITS = ["ACT_PE_CAST"]

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
		"root": f"generated/Arch/SparseConv/{design}",

		"SIM_CYCLES": 1000,
		"Randomize": 1,
		"Wei_Sparsity": 0.1,
		"Act_Sparsity": 0.1,	
		'save_np':True,#False,# True,
		'MODE': MODE,
		"RUN_GOLDEN_SBT": 1,	
		'RUN_CPP': True,
		"SKIP_IF_EXISTING_GOLDEN": True,#don't run the golden related flow if we see the golden power is there
	}
	#SIM_PARAMS = base_SIM_PARAMS
	#base_SIM_PARAMS['name'] = SIM_PARAMS['name']+"_"+str(SIM_PARAMS["Wei_Sparsity"])+"_"+str(SIM_PARAMS['Act_Sparsity'])


	run_fig6(base_hardware_config, base_mapping, base_network_layer, base_SIM_PARAMS, VALID_UNITS)


