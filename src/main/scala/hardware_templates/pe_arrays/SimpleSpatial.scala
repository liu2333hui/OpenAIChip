package units
// A simple MAC array
// Multiplier + adder tree
// Customize based on TI, TB, TN parameters

import chisel3._
import chisel3.util._
import helper._
import multipliers.{GenericMultiplier2,Multiplier2Factory}
import adders.{GenericAdderN,AdderNFactory}

class SimpleSpatial(HardwareConfig: Map[String, String]) extends Module {
	val TI = HardwareConfig("TI").toInt
	val TN = HardwareConfig("TN").toInt
	val TB = HardwareConfig("TB").toInt
		
	
  	val prec_in = HardwareConfig("prec_in").toInt
	val prec_sum = HardwareConfig("prec_sum").toInt
	
	

	val io = IO(new Bundle {
		
        	val in0 = Input (Vec(TI*TN*TB , UInt (prec_in.W) ) )
	        val in1 = Input (Vec(TI*TN*TB , UInt (prec_in.W) ) )
	        val Sum  = Output(Vec(TN*TB, UInt(prec_sum.W)))	
		val entry = new EntryIO()
		val exit = new ExitIO()

	})

	
	//val array0 = Array()


	val readies = VecInit(Seq.fill(TI*TN*TB)(Wire(Bool())))
	val pea = Array.fill(TI*TN*TB)(Multiplier2Factory.create(HardwareConfig))
  	val accum = Array.fill(TN*TB)(AdderNFactory.create(HardwareConfig))


	

	for(n <- 0 until TN){
	for(b <- 0 until TB){
	for(i <- 0 until TI){

		val m = pea(i+TI*b+TI*TB*n)
		m.io.A := io.in0(i+TI*b+TI*TB*n)
		m.io.B := io.in1(i+TI*b+TI*TB*n)
		//m.io.entry <> io.entry
		//array1 += m.io.entry.ready
		readies(i+TI*b+TI*TB*n) := m.io.entry.ready
		m.io.entry.valid := io.entry.valid
		
		m.io.exit.ready := 1.B

	}
	}
	}




	val combinedAnd0 = readies.reduce(_ & _)
	io.entry.ready := combinedAnd0	

	for(n <- 0 until TN){
	for(b <- 0 until TB){

		val m =accum(b+TB*n)// AdderNFactory.create(HardwareConfig)	
		//val array1 = Array[Bool]()
		val readies2 = VecInit(Seq.fill(TI)(Wire(Bool())))



		for(i <- 0 until TI){	      
			val mult:GenericMultiplier2 =  pea(i+TI*b+TI*TB*n)
			m.io.A(i) := mult.io.Out
			//array1 += mult.io.exit.valid
			readies2(i) := mult.io.exit.valid
		}
		val combinedAnd = readies2.reduce(_ & _)
		m.io.entry.valid := combinedAnd
		m.io.exit.ready := 1.U
		io.Sum(b+TB*n) := m.io.Sum 

		io.exit.valid := m.io.exit.valid

	      //accum += m
	}
	}



	


}



