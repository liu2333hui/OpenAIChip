// See LICENSE.txt for license details.
package adders

import chisel3._

import chisel3.util._

//Ripploe carry 加法器

class RCAAdder2( HardwareConfig : Map[String, String]) extends GenericAdder2(HardwareConfig) {
	
	var LEN = prec1
	if(prec2 > prec1){
		LEN = prec2
	}
	
	//Module(new FullAdder())
	
	val sum   = Wire(Vec(LEN, Bool()))
	
	val m = Module(new FullAdder())
	m.io.a := io.A(0)
	m.io.b := io.B(0)
	m.io.cin := io.Cin
	sum(0) := m.io.sum
	
	var prev_m = m
	
	// val mods = Array[FullAdder]()
	
	for (i <- 1 until LEN){
		val m = Module(new FullAdder())
		
		if (i < prec1 ){
			m.io.a := io.A(i)
		}else{
			m.io.a := 0.U
		}
		
		if(i < prec2){
			m.io.b := io.B(i)
		}else{
			m.io.b := 0.U
		}
		
		m.io.cin := prev_m.io.cout
		
		sum(i) := m.io.sum
		// mods += m
		
		prev_m = m
	}
	
	
	if(prec_sum-LEN>1){
		io.Sum := Cat(  Fill( prec_sum-LEN-1, io.Cout) , io.Cout ,  sum.asUInt )
	}else if (prec_sum-LEN==1){
		io.Sum := Cat(  io.Cout ,  sum.asUInt )
	}else{
		io.Sum := sum.asUInt
	}
	// io.Sum := Cat(  Fill( prec_sum-LEN-1, io.Cout) , io.Cout ,  sum.asUInt )
	// io.Sum := Cat(  Fill( prec_sum-LEN, io.Cout) ,  sum.asUInt ).asSInt
	
	
	// if(prec_sum > LEN){
	// 	io.Sum(LEN) := prev_m.io.cout
	// 	for(i <- LEN+1 until prec_sum){
	// 			io.Sum(i) := io.Sum(LEN)
	// 	}	
	// }	
	
  io.Cout := prev_m.io.cout
  
  io.entry.ready := 1.U
  io.exit.valid := 1.U
  

}
	
