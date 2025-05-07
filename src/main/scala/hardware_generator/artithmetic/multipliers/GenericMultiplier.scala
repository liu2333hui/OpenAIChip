package multipliers

import chisel3._

import helper._
import chisel3.util._

//A 2-entry multiplier (UInt)
//  default: io.A is the multiplicant
class GenericMultiplier2( HardwareConfig : Map[String, String]) extends Module {
	
  val prec1:Int     = HardwareConfig("prec1").toInt
  val prec2:Int     = HardwareConfig("prec2").toInt
  val radix = HardwareConfig("radix").toInt
  
  
	var prec_out:Int = prec1+prec2
  if(HardwareConfig("auto_prec_out").toBoolean){
  	prec_out = (Math.ceil((prec1+prec2+0.0)/log2Ceil(radix))*log2Ceil(radix)).toInt // need to take care of radix8 cases
	// println("prec_out"+prec_out +"\t"+Math.ceil((prec1+prec2+0.0)/log2Ceil(radix)))
	// sys.exit(0)	
	//because then is 9 bits ==> 18 bits, 16 / 3 == 5.33 --> 6 * 3 ==> 18
  }else{
  	prec_out = HardwareConfig("prec_out").toInt
  }
  
  // val prec_out: Int = HardwareConfig("prec_out").toInt
	
  val io = IO(new Bundle {
    val A    = Input(UInt(prec1.W))
    val B    = Input(UInt(prec2.W))
    val Out  = Output(UInt(prec_out.W))
	val entry = new EntryIO()
	val exit = new ExitIO()
	
  })
  
  
}



object Multiplier2Factory {

  //Create Core Adder (i.e. combinational logic)
  def create( HardwareConfig : Map[String, String]): GenericMultiplier2 = {
	  val buffered = HardwareConfig("buffered").toBoolean
	  // if(buffered == false){
		 //  create_general(HardwareConfig)
	  // }else{
		 //  create_buffered(HardwareConfig)
	  // }
	  create_general(HardwareConfig)
  }
  
  def create_general( HardwareConfig : Map[String, String] ): GenericMultiplier2 = {
		val signed = HardwareConfig("signed").toBoolean
		val multiplierType = HardwareConfig("multiplierType")

		//todos (sign)
		val out =   multiplierType match {
			case "SimpleMutiplier2" => new SimpleMultiplier2(HardwareConfig)
			case "HighRadixMultiplier" => new UIntHighRadixMultiplier2(HardwareConfig)
			case "BitSerialMultiplier" => new UIntBitSerialMultiplier(HardwareConfig)
			//case "ConstantMultiplier" => new ConstantMultiplier(HardwareConfig)
			//case "ConstantMultiplier2" => new ConstantMultiplier2(HardwareConfig)
	
	
			//Laconic, Pragmatic, Bitfusion, multi-precision, systolic, ...
			case _     => throw new IllegalArgumentException("Unknown mult2 type")
		}
	  
	  // if(signed == true ){
		  
		 //  class GenericSignedAdder2(HardwareConfig:Map[String,String]) extends GenericAdder2(HardwareConfig) {
			  
			//   val adder_core =  Module(create_general(HardwareConfig))
			  
			//   adder_core.io.A := io.A
			//   adder_core.io.B := io.B
			//   adder_core.io.entry <> io.entry
			//   adder_core.io.exit <> io.exit
			  
			//  var LEN = prec2
			//  if(prec1 > prec2){
			// 	 LEN = prec1
			//  }
			//   if(prec_sum <= LEN  ){
			// 	  io.Sum := adder_core.io.Sum 
			//   } else if (prec_sum == LEN + 1){
			// 	  io.Sum := Cat(  io.Cout , io.A + io.B )
			//   }else{
			// 	 io.Sum := Cat(  Fill( prec_sum-LEN-1, io.Cout) , io.Cout , io.A + io.B )
			//   }
			  
			  
		 //  }
		  
		 //  new GenericSignedAdder2(HardwareConfig)
		  
	  // }else{
		 //  out
	  // }
	  out
	  
  }
  

  
  
  
  // //Create Core Adder + input Buffer (i.e. 1-cycle adder)
  // def create_buffered( HardwareConfig : Map[String, String]): GenericAdder2 = {
	  
	 //  class GenericBufferedAdder2(HardwareConfig : Map[String, String]) 
		// extends GenericAdder2(HardwareConfig){
	    
		
	 //    val adder_core =  Module(create_general(HardwareConfig))
	    
		// val bufA = RegInit(0.U(prec1.W))
		// val bufB = RegInit(0.U(prec2.W))

		
		// val bufValid = RegInit(0.U(1.W))
		// //io.entry.ready := adder_core.io.entry.ready 
		// adder_core.io.A := bufA
		// adder_core.io.B := bufB
		// when(io.entry.ready & io.entry.valid){
		// 	bufA := io.A
		// 	bufB := io.B
		//     bufValid := 1.U
		// }  .otherwise {
		// 	bufValid := 0.U
		// }
		// io.Sum := adder_core.io.Sum
		// io.Cout := adder_core.io.Cout
		// io.exit.valid := bufValid & adder_core.io.exit.valid
		// adder_core.io.Cin := io.Cin
		// adder_core.io.entry <> io.entry
		// adder_core.io.exit.ready := io.exit.ready
		// io.entry.ready := adder_core.io.entry.ready
		// adder_core.io.entry.valid := io.entry.valid 
	 //  }

	 //  new GenericBufferedAdder2(HardwareConfig)
	  
  // }
  
  
  
  
  
}
