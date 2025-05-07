

package accumulators

import chisel3._
import chisel3.util._

import helper._

import adders.{Adder2Factory,AdderNFactory}


class RegAccumulatorN( HardwareConfig : Map[String, String])
	extends GenericAccumulator(HardwareConfig) {
		
	val total_sum = Reg(UInt(prec_out.W))
	
	val accum = Module(Adder2Factory.create(HardwareConfig 
		+ (("prec1",prec_in.toString), ("prec2", prec_out.toString),
			 ("prec_sum", prec_out.toString))
	))	
	
	accum.io.Cin := 0.U
	accum.io.B := total_sum
	
	
	accum.io.exit.ready := io.exit.ready
	
	
	
	if(terms == 1){
		io.entry <> accum.io.entry
		// io.entry.ready       := accum.io.entry.ready
		// accum.io.entry.valid := io.entry.valid
		accum.io.A := io.A(0)
	}else{
		val pre_sum = Module(AdderNFactory.create(HardwareConfig
			+ (("prec_sum",prec_out.toString), ("prec_in",prec_in.toString)
			, ("adderType",HardwareConfig("multioperandAdderType")))   ))
		accum.io.A := pre_sum.io.Sum
		pre_sum.io.A := io.A
		io.entry <> pre_sum.io.entry
		pre_sum.io.exit <> accum.io.entry
		
		
		
	}
	
	val valid = Reg(Bool())
	
	when(io.clear){
		total_sum := 0.U
		valid := 0.U
	}.elsewhen(io.en & accum.io.exit.valid){
			valid := 1.U
			total_sum := accum.io.Sum
	}.otherwise{
		valid := 0.U
	}
	
	io.exit.valid := valid
	
	io.Sum := total_sum
	
}
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

