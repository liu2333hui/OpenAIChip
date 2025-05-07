
package adders

import chisel3._

import helper._

//Some Different Type of FullAdder Implementations
//FAType = 0 (INTRINISIC)
//FAType = 1 (GATES)
//...

class FullAdder(Type: Int = 0) extends Module {
  val io = IO(new Bundle {
    val a    = Input(UInt(1.W))
    val b    = Input(UInt(1.W))
    val sum  = Output(UInt(1.W))
	
	val cin = Input(UInt(1.W))
	val cout = Output(UInt(1.W))
  })
  
  if(Type == 0){
	  io.sum := io.a ^ io.b ^ io.cin
	  io.cout := (io.b & io.cin) | (io.a & io.cin) | (io.a & io.b)
  }
  
}

class HalfAdder(Type: Int = 0) extends Module {
	val io = IO(new Bundle {
	  val a    = Input(UInt(1.W))
	  val b    = Input(UInt(1.W))
	  val sum  = Output(UInt(1.W))
		val cout = Output(UInt(1.W))
	})
	
	if(Type == 0){
		  io.sum := io.a ^ io.b
		  io.cout := io.a & io.b
	}
}

class CarrySaveAdder(Type: Int = 0){
	
}
