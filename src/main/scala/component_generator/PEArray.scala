package components

// A simple MAC array
// Multiplier + adder tree
// Customize based on TI, TB, TN parameters

import chisel3._
import chisel3.util._
import helper._
import multipliers.{GenericMultiplier2,Multiplier2Factory}
import adders.{GenericAdderN,AdderNFactory}

class SimplePEArray(HardwareConfig: Map[String, String]) extends Module {
	val number = HardwareConfig("number").toInt
			
  	val prec1 = HardwareConfig("prec1").toInt
  	val prec2 = HardwareConfig("prec2").toInt

	val prec_out = HardwareConfig("prec_out").toInt	

	val io = IO(new Bundle {
		
        	val in0 = Input (Vec(number , UInt (prec1.W) ) )
	        val in1 = Input (Vec(number , UInt (prec2.W) ) )
	        val Out  = Output(Vec(number , UInt(prec_out.W)))	
		val entry = new EntryIO()
		val exit = new ExitIO()

	})

	


	val readies = VecInit(Seq.fill(number)(Wire(Bool())))
	val valids = VecInit(Seq.fill(number)(Wire(Bool())))
	val pea = Array.fill(number)(Multiplier2Factory.create(HardwareConfig))	

	for(n <- 0 until number){

		val m = pea(n)
		m.io.A := io.in0(n)
		m.io.B := io.in1(n)
		//m.io.entry <> io.entry
		//array1 += m.io.entry.ready
		readies(n) := m.io.entry.ready
		valids(n) := m.io.exit.valid

		m.io.entry.valid := io.entry.valid
		
		m.io.exit.ready := 1.B

	}

	val combinedAnd0 = readies.reduce(_ & _)
	io.entry.ready := combinedAnd0	
	val combinedValid = valids.reduce(_ & _)
	io.exit.valid := combinedValid


	


}



