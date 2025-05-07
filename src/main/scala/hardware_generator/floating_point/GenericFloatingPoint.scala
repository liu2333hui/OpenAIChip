// import chisel3._
// import chisel3.util._


// class GenericFloatingPoint2Port(  HardwareConfig : Map[String, String]) extends Module {
	
// 	val a_exponent = HardwareConfig("a_exponent").toInt
// 	val a_mantissa = HardwareConfig("a_mantissa").toInt
// 	val b_exponent = HardwareConfig("b_exponent").toInt
// 	val b_mantissa = HardwareConfig("b_mantissa").toInt
	
// 	val a_bias = math.log2(a_exponent).toInt/2 - 1
// 	val b_bias = math.log2(b_exponent).toInt/2 - 1

// 	var out_exponent = a_exponent.max(b_exponent)
// 	var out_mantissa = a_mantissa.max(b_mantissa)
// 	if(HardwareConfig("auto_out").toBoolean){
// 		out_exponent = a_exponent.max(b_exponent)
// 		out_mantissa = a_mantissa.max(b_mantissa)
// 	}else{
// 		val out_exponent = HardwareConfig("out_exponent").toInt
// 		val out_mantissa = HardwareConfig("out_mantissa").toInt			
// 	}
	
	
	
//   val io = IO(new Bundle {
//     val A    = new FloatingPoint(a_exponent, b_exponent )
//     val B    = new FloatingPoint(b_exponent, b_mantissa )
//     val Out  = Flipped(new FloatingPoint(out_exponent, out_mantissa ))
	
// 	val entry = new EntryIO()
// 	val exit = new ExitIO()
	
//   })
  
  
// }

	