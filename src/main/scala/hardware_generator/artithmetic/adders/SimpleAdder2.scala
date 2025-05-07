// See LICENSE.txt for license details.
package adders

import chisel3._
import chisel3.util._
//A n-bit adder, 两个输入
// 1。n比特
// 2。是否

class SimpleAdder2(HardwareConfig : Map[String, String]) extends GenericAdder2( HardwareConfig) {
	//val sum = Wire(UInt(prec_sum.W)) 
	
	//println(sum, io.Sum)
	var LEN = prec1
	if(prec2 > prec1){
		LEN = prec2
	}
		
	//Is actually buggy (i.e. 127 + 192 = 63?)
	io.Sum := io.A+io.B//Cat(  Fill( prec_sum-LEN-1, io.Cout) , io.Cout , io.A + io.B ).asUInt
	// io.Sum := Cat(  Fill( prec_sum-LEN, io.Cout) , io.A + io.B).asSInt
	io.entry.ready := 1.U
	io.exit.valid := 1.U
	io.Cout := io.A(prec1-1) ^ io.B(prec2-1)
	
	// if(prec_sum > LEN){
	// 	io.Sum(LEN) := io.Cout 
	// 	for(i <- LEN+1 until prec_sum){
	// 			io.Sum(i) := io.Sum(LEN)
	// 	}	
	// }	
	
}


// /*deprecated
// */
// class SimpleAdd2(val n:Int, val buffered : Int  ) extends Module {
//   val io = IO(new Bundle {
//     val A    = Input(UInt(n.W))
//     val B    = Input(UInt(n.W))
//     val Sum  = Output(UInt(n.W))
//     val ready= Input(UInt(1.W))
//     val valid = Output(UInt(1.W))
//   })

//   if(buffered == 1) {
//     val AB = RegInit(0.U(n.W))
//     val validReg = RegNext(io.ready)
//     io.valid := validReg
//     AB := io.A + io.B
//     io.Sum := AB
 
//   } else {
//   val AB = Wire(UInt(n.W))       
//   io.valid := 1.U
//   AB := io.A + io.B
//   io.Sum := AB

//   }
  
// }
