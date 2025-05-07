package accumulators

import chisel3._

import chisel3.util._

class UpCounter( HardwareConfig : Map[String, String])
	extends GenericCounter(HardwareConfig) {
		
	   val cnt = Reg(UInt(out_prec.W) )
	   val up = HardwareConfig("up").toInt
	   
	   when(io.clear){
		    cnt := 0.U
	   }.elsewhen(io.en){
			cnt := cnt + up.asUInt
	   }
	   
	   io.Out := cnt
		
}