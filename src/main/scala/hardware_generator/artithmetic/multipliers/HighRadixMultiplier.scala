// High-radix multipliers


package multipliers

import chisel3._
import chisel3.util._
import helper._

import accumulators.{UpCounter}
import networks.MuxN
import adders.Adder2Factory

/*
  multiplicant_precision/radix cycle multiplier, completely laid out
	prec1 is the multiplicant
	
	multiplier = io.A
	multiplicand = io.B
	Right shifting
	multiplier should be non-negative in this case
	
	//If we want to treat negative numbers, we use Booth, Baughly
	//Or other multipliers
	
*/
class UIntHighRadixMultiplier2(HardwareConfig : Map[String, String]) 
	extends GenericMultiplier2( HardwareConfig ) {

	val counter = Module( new UpCounter(
		Map(  
			("max_cnt",prec1.toString),
			("up"	  ,"1".toString)
		)))

	val mux = Module(new MuxN(Map(
		("prec",  (prec2+log2Ceil(radix)).toString   ),
		("terms", radix.toString)								  
		)
	))
	
	val adder = Module( Adder2Factory.create(this.HardwareConfig
		   	+   ( 
					("prec1" , (prec2+log2Ceil(radix)).toString),
				    ("prec_sum", (prec2+log2Ceil(radix)).toString),
					("same_prec", true.toString),
					("buffered" , false.toString),
					("signed"   , false.toString)  
				
				)
	))
	
	val multiplier = Reg(UInt(prec1.W))

	for(i <- 0 until radix){
		mux.io.in(i) := i.asUInt*io.B
	}
	
	val partial_sum = Reg(UInt((prec_out).W))
	
	// val w = Wire(UInt((prec1+prec2).W))
	
	// // val width 
	// w := // , prec1 + prec2)
	
	adder.io.A   := mux.io.out
	adder.io.B   := partial_sum(prec_out-1, (Math.ceil((0.0+prec1)/log2Ceil(radix))*log2Ceil(radix)).toInt )
	adder.io.Cin    := 0.U
	adder.io.exit.ready := 1.U
	adder.io.entry.valid := 1.U
	
	
	// mux.io.in, mux.io.sel, mux.io.out
	mux.io.sel := multiplier(log2Ceil(radix)-1,0)
	
	//FSM
	val idle :: processing :: Nil = Enum(2)
	val stateReg = RegInit(idle)
	val validReg = RegInit(0.U)
	
	// io.Out := io.A*io.B
	io.entry.ready := (stateReg === idle)
	io.exit.valid := validReg
	
	// val out = Wire(UInt((prec1+prec2).W))
	io.Out :=  partial_sum
	
	counter.io.en := 0.U
	counter.io.clear := 0.U
	
	
	switch(stateReg){
		is (idle){
			when(io.entry.valid & io.entry.ready){
				stateReg := processing
				validReg := 0.U
				multiplier :=   io.A
				counter.io.clear := 1.U
				counter.io.en := 0.U
				partial_sum := 0.U
				
			}
		}//idle state
		is (processing){
			when(adder.io.exit.valid){

				when(counter.io.Out === (Math.ceil((prec1+0.0)/log2Ceil(radix)) -1).toInt.U){
					when(io.entry.ready){
						multiplier := io.A
						stateReg := processing
					}.otherwise{
						stateReg := idle
					}
					validReg := 1.U
					counter.io.en := 0.U
					counter.io.clear := 1.U
				
					multiplier := io.A
					
				}.otherwise {
					validReg := 0.U
					counter.io.en := 1.U
					counter.io.clear := 0.U
				}
				
				multiplier  := Cat(0.U(log2Ceil(radix).W), multiplier(prec1-1 , log2Ceil(radix)) )
				partial_sum := Cat(adder.io.Sum, partial_sum((Math.ceil((0.0+prec1)/log2Ceil(radix))*log2Ceil(radix)).toInt-1,log2Ceil(radix)) )
			
			}
			
		}//is_processing state
	
	
	}
	
	
}
