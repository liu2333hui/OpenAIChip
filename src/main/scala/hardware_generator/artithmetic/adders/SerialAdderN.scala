// // See LICENSE.txt for license details.
// package adders

// import chisel3._
// import chisel3.util._

// //Accumulator

// // A serial-based multiplier ==> accumulator1 ==> AddSerial1

// //Data can come serially from a FIFO or a shift register (i.e. like a FIFO)
// class Accumulator1( terms :Int, 
//      prec_in : Int, 
// 	 prec_out : Int,
// 	 adder2Type: String = "SimpleAdder2", 
// 	 pipelined: Boolean = false,
// 	 buffered : Boolean = false
// 	) extends GenericAdderN(terms=1, prec_in, prec_out) {
	
	
	
	
	
	
	
// 	val adder = Module(Adder2Factory.create(adderType=adder2Type,
// 	 prec_in, prec_out, prec_out,
//   buffered= buffered))
// 	val cycles = terms
	
	
// 	// //FSM
// 	val ready :: processing :: final_processing :: Nil = Enum(3)
// 	val stateReg = RegInit(ready)
	
	
// 	// //replace with a real counter ?
// 	val cnt = Reg(UInt((log2Ceil(terms)+1).W))
// 	val sum = Reg(UInt(prec_out.W))
	
// 	val validReg = Reg(Bool())
	
// 	validReg := 0.U
// 	io.Sum := sum
// 	io.entry.ready := 1.U
	
// 	adder.io.Cin := 0.U
// 	adder.io.A := io.A(0)
// 	adder.io.B := sum
// 	sum := adder.io.Sum
	
// 	adder.io.entry.valid := io.entry.valid
// 	adder.io.exit.ready := io.exit.ready
// 	io.exit.valid := validReg
	
// 	switch(stateReg){
// 	    is (ready){
// 			when(io.entry.valid & io.entry.ready){
// 				stateReg := processing
// 				sum := io.A(0)
				
// 				cnt := 1.U
// 			}
// 		}	
// 		is (processing){
// 			when(cnt === (cycles-1).U){
// 				validReg := 1.U
// 				stateReg := ready
// 				cnt := 0.U
// 			}
// 			.otherwise{
// 				cnt := cnt + 1.U
// 			}
			
// 			// sum := sum + io.A(0)
			
			
// 		}
// 		is (final_processing){
			
// 		}
	
	
// 	}
	
	

//  //    io.entry.ready := 1.U
// 	// io.exit.valid := 1.U
// }
