//CrossbarN_M

package networks

import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue



class Crossbar( HardwareConfig:Map[String, String]) extends Module {

 val prec:Int  = HardwareConfig("prec").toInt
 val in_terms:Int = HardwareConfig("in_terms").toInt
 val out_terms:Int = HardwareConfig("out_terms").toInt

   val io = IO(new Bundle {
	val in     = Input( Vec(in_terms, UInt(prec.W)))
  	val sel   = Input( Vec(out_terms, UInt(log2Ceil(in_terms).W) ) )
	val out  = Output( Vec(out_terms, UInt(prec.W)))
  })  

	for ( o <- 0 until out_terms) {
		val bar = Module(new MuxN(HardwareConfig
	+ (("prec",prec.toString) , ("terms",in_terms.toString) )  ))
		for (i <- 0 until in_terms){
			bar.io.in(i) := io.in(i)
		}		
		bar.io.sel := io.sel(o)
		io.out(o) := bar.io.out
	}

}

/*
class ZeroRemoveCrossbar( HardwareConfig: Map[String, String]) extends Module {
  val io = IO(new Bundle {
	val in     = Input( Vec(in_terms, UInt(prec.W)))
  	val sel   = Input( Vec(out_terms, UInt(log2Ceil(in_terms).W) ) )
	val out  = Output( Vec(out_terms, UInt(prec.W)))
	val entry = new EntryIO()
	val exit = new ExitIO()
  })  

   //FSM
   val idle :: processing :: Nil = Enum(2)
   val stateReg = RegInit(idle)
	
   switch(stateReg){
     is(idle){

     } 
     is (processing){

      }

   }




}

//Butterfly, Benes, Partial Crossbar, Full Crossbar, 4 main types
*/
