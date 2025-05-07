package accumulators

import chisel3._

import chisel3.util._
import helper._

//A prec-bit integer accumulator
//For non-integer accumulation, see the "floating_point" folder
class GenericAccumulator( HardwareConfig : Map[String, String]) extends Module {
	
  val prec_in:Int     = HardwareConfig("prec_in").toInt
  val prec_out:Int    = HardwareConfig("prec_out").toInt
  val terms: Int = HardwareConfig("terms").toInt
	
  val io = IO(new Bundle {
    val A    = Input(Vec(terms, UInt(prec_in.W)) )
	val en   = Input(Bool()) //enable the accumulator
	val clear = Input(Bool()) //clear the accumulator
    val Sum  = Output(UInt(prec_out.W))
	val entry = new EntryIO()
	val exit = new ExitIO()
	
  })
  
  
}


class GenericCounter( HardwareConfig : Map[String, String]) extends Module {
	
  val max_cnt: Int = HardwareConfig("max_cnt").toInt
  val out_prec:Int = (log2Ceil(max_cnt)+1)
  
  val io = IO(new Bundle {
    val en   = Input(Bool()) //enable the accumulator
	val clear = Input(Bool()) //clear the accumulator
    val Out  = Output(UInt(out_prec.W))
  })
  
  
}