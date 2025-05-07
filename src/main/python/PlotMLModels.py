import sys


from power_models.AdderNPrimitive import *
from power_models.Multiplier2Primitive import *
from power_models.MaxNPrimitive import *
from power_models.SRAMSPrimitive import *
from power_models.MuxNPrimitive import *
from power_models.DeserializerPrimitive import *
from power_models.Parallel2SerialPrimitive import *
from power_models.MulticastPrimitive import *



if __name__ == "__main__":
	# print(sys.argv[-1])
	# s = ?sys.argv[-2]

	s = hw = sys.argv[-3]
	mode = sys.argv[-2]
	out = sys.argv[-1]


	if(out == "power"):
		out_features = ["Total_Pwr"]
	elif(out == "time"):
		out_features = ['Unit_Cycles']
	# out_features = ['Unit_Cycles']#['Total_Pwr']#,'Unit_Cycles']#, 'Energy']

	if(mode.lower() == "train" ):
		train = 1
	else:
		train = 0
	if(s == "MuxN"):
		MuxNPrimitiveTest(out_features = out_features, train = train)

	if(s == "Multiplier2"):
		Multiplier2PrimitiveTest(out_features = out_features, train = train)
	if(s == "AdderN"):
		AdderNPrimitiveTest(out_features = out_features, train = train)
	if(s == "MaxN"):
		MaxNPrimitiveTest(out_features = out_features, train = train)
	if(s == "Multicast"):
		MulticastPrimitiveTest(out_features = out_features, train = train)
	
	if(s == "SRAMS"):
		SRAMSPrimitiveTest(out_features = out_features, train = train)
	#	if(s == "Parallel2Serial"):
	#		Parallel2SerialPrimitiveTest(out_features = out_features, train = train)
	
	if(s == "Deserializer"):
		DeserializerPrimitiveTest(out_features = out_features, train = train)
	
	if(s == "Parallel2Serial"):
		Parallel2SerialPrimitiveTest(out_features = out_features, train = train)
	
	# 动态导入模块
	
