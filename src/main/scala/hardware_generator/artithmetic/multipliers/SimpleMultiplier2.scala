package multipliers

import chisel3._
import chisel3.util._
import helper._

/*
  0 cycle multiplier, completely laid out
*/
class SimpleMultiplier2(HardwareConfig : Map[String, String]) 
	extends GenericMultiplier2( HardwareConfig ) {
		
	io.Out := io.A*io.B
	io.entry.ready := 1.U
	io.exit.valid := 1.U
	
}
