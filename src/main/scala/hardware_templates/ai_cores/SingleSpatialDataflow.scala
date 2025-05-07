// package HardwareTemplates

// import chisel3._
// import scala.math.{ceil}

// object SingleSpatialDataflowArchTest extends App{
	
// 	val hw = Map(
// 		( "DRAM_WRITE_DELAY","128"), 
// 		( "DRAM_READ_DELAY","128"), 
// 		( "DRAM_ENTRY_BITS","512"), 
// 		( "DRAM_THROUGHPUT","4"), 
		
// 		( "L2_WRITE_DELAY","1"), 
// 		( "L2_ENTRY_BITS","256"), 
// 		( "L2_READ_DELAY",1), 
// 		( "L2_THROUGHPUT",1), 
		
// 		( "L1_WEIGHT_WRITE_DELAY",1), 
// 		( "L1_WEIGHT_ENTRY_BITS",128), 
// 		( "L1_WEIGHT_READ_DELAY",1), 
// 		( "L1_WEIGHT_THROUGHPUT",1), 
		
// 		( "L1_ACT_WRITE_DELAY",1), 
// 		( "L1_ACT_ENTRY_BITS",64), 
// 		( "L1_ACT_READ_DELAY",1), 
// 		( "L1_ACT_THROUGHPUT",1), 
				
// 		( "L1_PSUM_WRITE_DELAY",1), 
// 		( "L1_PSUM_ENTRY_BITS",32), 
// 		( "L1_PSUM_READ_DELAY",1), 
// 		( "L1_PSUM_THROUGHPUT",1), 
		
// 		( "WEIGHT_PRECISION", 4),
// 		( "ACT_PRECISION", 8),
// 		( "PSUM_PRECISION", 16),
// 		( "ACCUM_PRECISION", 20),
// 		( "OUT_PRECISION", 8),
		
// 		( "PE_DELAY",4), 
// 		( "PE_THROUGHPUT",4), 
// 		( "ADDER_TREE_DELAY",1), 
// 		( "ADDER_TREE_THROUGHPUT",1,
// 		( "ACCUMULATOR_DELAY",1),
// 		( "ACCUMULATOR_THROUGHPUT",1),
// 		( "LOOP_ORDER","B.N.X.Y.KX.KY.I"), 
		
// 		( "TN",8), 
// 		( "TI",8), 
// 		( "TY",1), 
// 		( "TX",1), 
// 		( "TKY",1),
// 		( "TKX",1), 
// 		( "TB",1)
// 	)
	
	
// 	val I = RuntimeConfig("I")   .toInt
// 	val N = RuntimeConfig("N")   .toInt
// 	val Y = RuntimeConfig("Y")   .toInt
// 	val X = RuntimeConfig("X")   .toInt 
// 	val KY =RuntimeConfig("KY") .toInt //Or pooling KX
// 	val KX =RuntimeConfig("KX") .toInt //Or pooling KY
// 	val B = RuntimeConfig("B")   .toInt
// 	val PADDING_X = RuntimeConfig("PX").toInt
// 	val PADDING_Y = RuntimeConfig("PY").toInt
// 	val STRIDE_X = RuntimeConfig("STRIDE_X").toInt
// 	val STRIDE_Y = RuntimeConfig("STRIDE_Y").toInt
// 	val OPERATION = RuntimeConfig("Operation").toInt // Pool, Conv, FC
// 	val CLOCK = RuntimeConfig("CLOCK").toInt	
	
// 	object OPS extends Enumeration {
// 	  type OPS = Value
// 	  val CONV2D, CONV2D_BIAS, CONV2D_ACTIVATION, CONV2D_BN, MAX_POOL, AVG_POOL = Value
// 	}
	
// 	val rc = Map(("I", 1),
// 				 ("N", 1),
// 				 ("Y", 128),
// 				 ("X", 128),
// 				 ("KY", 3),
// 				 ("KX", 3),
// 				 ("B", 1),
				 
// 				 ("PADDING_X", 0),
// 				 ("PADDING_Y", 0),
// 				 ("STRIDE_X", 1),
// 				 ("STRIDE_Y", 1),
// 				 ("OPERATION", OPS.CONV2D),
// 				 ("CLOCK", 1)
// 				 )
	
// 	val m = SingleSpatialDataflowArch(hw, rc)
// 	m.schedule_v1()
// }

// class SingleSpatialDataflowArch(HardwareConfig: Map[String, String with Integer],
// 	RuntimeConfig: Map[String, String with Integer]){
	
// 	//Simplest full core
// 	val LOOP_ORDER = HardwareConfig("LOOP_ORDER").split(".", 0)
// 	val TN = HardwareConfig("TN")   .toInt
// 	val TI = HardwareConfig("TI")   .toInt
// 	val TY = HardwareConfig("TY")   .toInt
// 	val TX = HardwareConfig("TX")   .toInt
// 	val TKY = HardwareConfig("TKY") .toInt
// 	val TKX = HardwareConfig("TKX") .toInt
// 	val TB = HardwareConfig("TB")   .toInt
	
// 	val DRAM_WRITE_DELAY = HardwareConfig("DRAM_WRITE_DELAY").toInt
// 	val DRAM_READ_DELAY = HardwareConfig("DRAM_READ_DELAY").toInt
// 	val DRAM_ENTRY_BITS = HardwareConfig("DRAM_ENTRY_BITS").toInt
// 	val DRAM_THROUGHPUT = HardwareConfig("DRAM_THROUGHPUT").toInt //due to multi-line access
	
	
// 	val L2_WRITE_DELAY = HardwareConfig("L2_WRITE_DELAY").toInt
// 	val L2_ENTRY_BITS = HardwareConfig("L2_ENTRY_BITS").toInt
// 	val L2_READ_DELAY = HardwareConfig("L2_READ_DELAY").toInt
// 	val L2_THROUGHPUT = HardwareConfig("L2_THROUGHPUT").toInt
	
// 	val L1_WEIGHT_WRITE_DELAY = HardwareConfig("L1_WEIGHT_WRITE_DELAY").toInt
// 	val L1_WEIGHT_READ_DELAY = HardwareConfig("L1_WEIGHT_READ_DELAY").toInt
// 	val L1_WEIGHT_THROUGHPUT = HardwareConfig("L1_WEIGHT_THROUGHPUT").toInt
// 	val L1_WEIGHT_ENTRY_BITS = HardwareConfig("L1_WEIGHT_ENTRY_BITS").toInt


// 	val L1_ACT_WRITE_DELAY = HardwareConfig("L1_ACT_WRITE_DELAY").toInt
// 	val L1_ACT_READ_DELAY = HardwareConfig("L1_ACT_READ_DELAY").toInt
// 	val L1_ACT_THROUGHPUT = HardwareConfig("L1_ACT_THROUGHPUT").toInt
// 	val L1_ACT_ENTRY_BITS = HardwareConfig("L1_ACT_ENTRY_BITS").toInt
		
// 	val L1_PSUM_WRITE_DELAY = HardwareConfig("L1_PSUM_WRITE_DELAY").toInt
// 	val L1_PSUM_READ_DELAY = HardwareConfig("L1_PSUM_READ_DELAY").toInt
// 	val L1_PSUM_THROUGHPUT = HardwareConfig("L1_PSUM_THROUGHPUT").toInt
// 	val L1_PSUM_ENTRY_BITS = HardwareConfig("L1_PSUM_ENTRY_BITS").toInt
			
	
// 	val WEIGHT_PRECISION = HardwareConfig("WEIGHT_PRECISION").toInt
// 	val ACT_PRECISION = HardwareConfig("ACT_PRECISION").toInt
// 	val PSUM_PRECISION = HardwareConfig("PSUM_PRECISION").toInt
// 	val ACCUM_PRECISION = HardwareConfig("ACCUM_PRECISION").toInt
// 	val OUT_PRECISION = HardwareConfig("OUT_PRECISION").toInt
	
// 	// what if the delay is multi-cycle non determinisitc?
// 	val PE_DELAY = HardwareConfig("PE_DELAY").toInt
// 	val PE_THROUGHPUT = HardwareConfig("PE_THROUGHPUT").toInt
// 	//non-pipelined, delay == throughput
	
// 	val ADDER_TREE_DELAY = HardwareConfig("ADDER_TREE_DELAY").toInt
// 	val ADDER_TREE_THROUGHPUT = HardwareConfig("ADDER_TREE_THROUGHPUT").toInt
	
// 	val ACCUMULATOR_DELAY = HardwareConfig("ACCUMULATOR_DELAY").toInt
// 	val ACCUMULATOR_THROUGHPUT = HardwareConfig("ACCUMULATOR_THROUGHPUT").toInt
		

	
// 	//Supported 
// 	val I = RuntimeConfig("I")   .toInt
// 	val N = RuntimeConfig("N")   .toInt
// 	val Y = RuntimeConfig("Y")   .toInt
// 	val X = RuntimeConfig("X")   .toInt 
// 	val KY =RuntimeConfig("KY") .toInt //Or pooling KX
// 	val KX =RuntimeConfig("KX") .toInt //Or pooling KY
// 	val B = RuntimeConfig("B")   .toInt
	
	
	
// 	val PADDING_X = RuntimeConfig("PX").toInt
// 	val PADDING_Y = RuntimeConfig("PY").toInt
// 	val STRIDE_X = RuntimeConfig("STRIDE_X").toInt
// 	val STRIDE_Y = RuntimeConfig("STRIDE_Y").toInt
// 	val OPERATION = RuntimeConfig("Operation").toInt // Pool, Conv, FC
// 	val CLOCK = RuntimeConfig("CLOCK").toInt
// 	//Tech
	
// 	// Scheduler
// 	// Output:
// 	// Runtime, MAC counts, DRAM reads, minimum L1, L2 row sizes
// 	// Given Loop Order and Tiling, 
// 	// (0, )
	
// 	def schedule_v1() = {
		
// 		val XX = ceil((X - KX + 1)/STRIDE_X/TX).toInt
// 		val YY = ceil((Y - KY + 1)/STRIDE_Y/TY).toInt
// 		val NN = ceil(N/TN).toInt
// 		val II = ceil(I/TI).toInt
// 		val BB = ceil(B/TB).toInt
// 		val KKX = ceil(KX/TKX).toInt
// 		val KKY = ceil(KY/TKY).toInt
		
// 		var MACS = XX * YY * NN * II * BB * KKX * KKY

		
// 		var POOL_COMPARATOR_ACCUM_TERMS = 0
// 		var POOL_COMPARATOR_TREE_TERMS = 0
		
		
// 		var OUT_TERMS = XX*YY*NN*BB
// 		var OUT_TILE = TX*TY*TN*TB

// 		if(OPERATION == OPS.MAX_POOL){
// 			MACS = 0
// 			POOL_COMPARATOR_TREE_TERMS = OUT_TERMS
// 			POOL_COMPARATOR_ACCUM_TERMS = OUT_TERMS
// 		}
		
// 		// Different stage
// 		// Calculate minimum latencies, then get the maximum for overall latency estimate
// 		 // (todos) for unknown time multipliers, need to known average bit-length
// 		var PE_LATENCY = MACS *PE_THROUGHPUT + PE_DELAY
// 		var ADDER_TREE_LATENCY = MACS *ADDER_TREE_THROUGHPUT + ADDER_TREE_DELAY
// 		var ACCUMULATOR_LATENCY = MACS *ACCUMULATOR_THROUGHPUT + ACCUMULATOR_DELAY
		
// 		var POOL_COMPARATOR_TREE_TERMS = *POOL_TREE_THROUGHPUT + POOL_TREE_DELAY
// 		var POOL_
		
// 		var L1_OUT_WRITE_LATENCY = OUT_TERMS * (TX*TY*TN*TB*OUT_PRECISION / L1_PSUM_ENTRY_BITS)*L1_PSUM_THROUGHPUT + L1_PSUM_WRITE_DELAY
// 		var L1_OUT_READ_LATENCY = OUT_TERMS * (TX*TY*TN*TB*OUT_PRECISION / L1_PSUM_ENTRY_BITS)*L1_PSUM_THROUGHPUT + L1_PSUM_WRITE_DELAY
			
// 		//DRAM is blocked, so need to add the latencies
// 		var DRAM_WRITE_LATENCY = OUT_TERMS * (TX*TY*TN*TB*OUT_PRECISION / L1_PSUM_ENTRY_BITS)*L1_PSUM_THROUGHPUT + L1_PSUM_WRITE_DELAY
	
	
// 		var DRAM_READ_LATENCY = OUT_TERMS * (TX*TY*TN*TB*OUT_PRECISION / L1_PSUM_ENTRY_BITS)*L1_PSUM_THROUGHPUT + L1_PSUM_WRITE_DELAY		
// 		var DRAM_LATENCY = DRAM_WRITE_LATENCY + DRAM_READ_LATENCY
		
// 		if(OPERATION == OPS.POOL){
// 			MACS = 0
// 		}
		
// 		//cycles
// 		//Find Supremum
// 		val ESTIMATED_LATENCY = Array(DRAM_READ_LATENCY,L2_WRITE_LATENCY,
// 			L2_READ_LATENCY,L1_WEIGHT_WRITE_LATENCY,L1_ACT_WRITE_LATENCY,
// 			L1_WEIGHT_READ_LATENCY,L1_ACT_READ_LATENCY,
// 			PE_LATENCY,ADDER_TREE_LATENCY,ACCUMULATOR_LATENCY,
// 			L1_OUT_WRITE_LATENCY,L1_OUT_READ_LATENCY,
// 			DRAM_WRITE_LATENCY).max
		
// 		val ESTIMATED_CLOCK = ESTIMATED_LATENCY * 1e-9*CLOCK
		
// 		println("Architecture summary: ")
	
// 		println("MACS = "+MACS)
	
// 		println("---------------------------------------")
		
// 		println("DRAM_READ_LATENCY=" + DRAM_READ_LATENCY)
// 		println("L2_WRITE_LATENCY="+L2_WRITE_LATENCY)
// 		println("L2_READ_LATENCY="+L2_READ_LATENCY)
// 		println("L1_WEIGHT_WRITE_LATENCY="+L1_WEIGHT_WRITE_LATENCY)
// 		println("L1_ACT_WRITE_LATENCY="+L1_ACT_WRITE_LATENCY)
// 		println("L1_WEIGHT_READ_LATENCY="+L1_WEIGHT_READ_LATENCY)
// 		println("L1_ACT_READ_LATENCY="+L1_ACT_READ_LATENCY)
		
// 		println("PE_LATENCY="+PE_LATENCY)
// 		println("ADDER_TREE_LATENCY="+ADDER_TREE_LATENCY)
// 		println("ACCUMULATOR_LATENCY="+ACCUMULATOR_LATENCY)
		
// 		println("L1_OUT_WRITE_LATENCY="+L1_OUT_WRITE_LATENCY)
// 		println("L1_OUT_READ_LATENCY="+L1_OUT_READ_LATENCY)
		
// 		println("DRAM_WRITE_LATENCY=" + DRAM_WRITE_LATENCY)
		
// 		println("architecture test done CYCLES=" + ESTIMATED_LATENCY + " , CLOCK="+ESTIMATED_CLOCK)
// 	}
	
	
	
	
	
// }


// class SingleSpatialDataflowCore(HardwareConfig: Map[String, String]) extends Module {
// 	//Parameters
// 	//val adderNType = HardwareConfig("")
// 	//val adderTree_adder2Type = HardwareConfig("")
// 	//val mult2Type = HardwareConfig("")
// 	//val wei_prec = HardwareConfig("")
// 	//val act_prec = HardwareConfig("")
	
// 	//val TB =  
// 	//val TI =  
// 	//val TN =  
// 	//val TKX = 
// 	//val TKY = 
// 	//val TX  = 
// 	//val TY  = 
// 	//val LOOP_ORDER = HardwareConfig("")
	
// 	// Loop Counter
	
// 	// L1 Buffer
	
// 	// Interconnect
	
	
// 	// Multipliers
// 	// val mult = Array[GenericMultiplier2]
// 	// mult_array += mult
	
// 	// Adder Tree
// 	//val adder_tree = AdderNFactory.create(adderNType: String, adder2Type = , 
// 	//  terms:Int, prec_in:Int, prec_out: Int,
// 	//  buffered: Boolean = false, pipelined: Boolean = false)
// 	// adder_tree_array += adder_tree
	
	
	
// 	// Comparator Tree
	
// 	// Accumulator
	
// }
