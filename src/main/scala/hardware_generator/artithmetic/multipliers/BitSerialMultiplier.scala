//Bit-serial multipliers

// Fully bit-serial, N cycles
// Skip serial, unpredictable cycles
// pragmatic, laconic multipliers
// High-radix multipliers


package multipliers

import chisel3._
import chisel3.util._
import helper._

import accumulators.{UpCounter}
import networks.{MuxN,Mux2}
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
class UIntBitSerialMultiplier(HardwareConfig : Map[String, String]) 
	extends GenericMultiplier2( HardwareConfig ) {

	// val extendedIO = IO(new Bundle {
	// 	val side_selection  = Input(Bool())
	// })

    // val radix = HardwareConfig("radix").toInt
	val side  = HardwareConfig("side") //A, B, dual
	
	var max_cycles = prec1
	var multiplier_port = io.A
	var multiplicand_port = io.B
	var multiplier_prec = prec1
	var multiplicand_prec = prec2
	if(side == "A"){
		max_cycles = prec1
		multiplier_port = io.A
		multiplicand_port = io.B
		
		multiplier_prec = prec1
		multiplicand_prec = prec2
		
	}else if (side == "B"){
		max_cycles = prec2
		multiplier_port = io.B
		multiplicand_port = io.A
		
		multiplier_prec = prec2
		multiplicand_prec = prec1
		
	}else{
		max_cycles = prec1.max(prec2)
		
		val multiplier_selector = Module(new Mux2(Map(
			("prec",  (max_cycles).toString   )								  
		)))
		val multiplicand_selector = Module(new Mux2(Map(
			("prec",  (max_cycles).toString   )								  
		)))
		val side_selection = Wire(Bool())
		//Two priority encoders and compare
		// val top_prec1 = Wire(UInt(prec1).W)
		// val top_prec2 = Wire(UInt(log2Ceil(prec2).W))
		
		
		val top_prec1 = PriorityEncoder(Reverse(io.A))
		val top_prec2 = PriorityEncoder(Reverse(io.B))
		
		side_selection := (top_prec1 <= top_prec2) //Which one's top-zeros are longer
		
		multiplier_selector.io.sel   :=  side_selection
		multiplicand_selector.io.sel :=  side_selection
		multiplier_selector.io.in0     := io.A
		multiplier_selector.io.in1     := io.B
		multiplicand_selector.io.in0     := io.B
		multiplicand_selector.io.in1     := io.A
		
		multiplier_port = multiplier_selector.io.out
		multiplicand_port = multiplicand_selector.io.out
		
		multiplier_prec   = prec1.max(prec2)
		multiplicand_prec = prec1.max(prec2) //cover worst case
		
	}
	
	val counter = Module( new UpCounter(
		Map(  
			("max_cnt",max_cycles.toString),
			("up"	  ,"1".toString)
		)))

	val mux = Module(new MuxN(Map(
		("prec",  (max_cycles+log2Ceil(radix)).toString ),
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
	
	val multiplier = Reg(UInt(max_cycles.W))

	for(i <- 0 until radix){
		mux.io.in(i) := i.asUInt*multiplicand_port
	}
	
	val partial_sum = Reg(UInt((prec1+prec2).W))
	
	adder.io.A   := mux.io.out
	adder.io.B   := partial_sum(prec1+prec2-1, max_cycles )
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
	
	// multiplicand_selector
	
	val remaining = Reg(UInt((log2Ceil(max_cycles)+1).W))
	
	io.Out :=  partial_sum >> (remaining)
	
	counter.io.en := 0.U
	counter.io.clear := 0.U
	remaining := 0.U
	
	switch(stateReg){
		is (idle){
			when(io.entry.valid & io.entry.ready){
				stateReg := processing
				validReg := 0.U
				multiplier :=   multiplier_port
				counter.io.clear := 1.U
				counter.io.en := 0.U
				partial_sum := 0.U
				
			}
		}//idle state
		is (processing){
			when(adder.io.exit.valid){
				
				when((counter.io.Out === (( max_cycles/log2Ceil(radix) ) -1).U) 
					| (multiplier === 0.U) ){
					when(io.entry.ready){
						multiplier := multiplier_port
						stateReg := processing
					}.otherwise{
						stateReg := idle
					}
					validReg := 1.U
					counter.io.en := 0.U
					counter.io.clear := 1.U
				
					multiplier := multiplier_port
					// println((max_cycles/log2Ceil(radix) - 1-1))
					remaining := (( ( max_cycles/log2Ceil(radix) ) ).U-counter.io.Out-1.U)<<(log2Ceil(radix)-1)
				}.otherwise {
					validReg := 0.U
					counter.io.en := 1.U
					counter.io.clear := 0.U
				}
				
				multiplier  := Cat(0.U(log2Ceil(radix).W), multiplier(max_cycles-1 , log2Ceil(radix)) )
				partial_sum := Cat(adder.io.Sum, partial_sum( max_cycles-1,log2Ceil(radix)) )
			
			}
			
		}//is_processing state
	
	
	}
	
	
}
