package multipliers

import chisel3._

import helper._
import chisel3.util._

//A 1-entry multiplier (UInt),  i.e. scaler
//This unit is used a lot in mappers, etc. Winograd Convolution

class ConstantMultiplier2(HardwareConfig : Map[String, String]) 
	extends GenericMultiplier2( HardwareConfig ) {
		
  val constant:Int = HardwareConfig("constant").toInt
	

	io.Out := io.A*constant.U
	io.entry.ready := 1.U
	io.exit.valid := 1.U
	
}

class ConstantMultiplier( HardwareConfig : Map[String, String]) extends Module {
	
    val prec1:Int     = HardwareConfig("prec1").toInt
  var prec_out:Int = prec1*2//double it otherwise will have some errors

  if(HardwareConfig("auto_prec_out").toBoolean){
  }else{
  	prec_out = HardwareConfig("prec_out").toInt
  }
  val constant:Int = HardwareConfig("constant").toInt
	
  val io = IO(new Bundle {
    val A    = Input(UInt(prec1.W))
    val Out  = Output(UInt(prec_out.W))
	val entry = new EntryIO()
	val exit = new ExitIO()	
  })
  
  	io.Out := io.A*constant.U
	io.entry.ready := 1.U
	io.exit.valid := 1.U
  
}
