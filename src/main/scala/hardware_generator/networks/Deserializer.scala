//Parallel2Serial, Serializer
package networks

import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._

//Used in systolic flows
class GenericDeserializer( HardwareConfig:Map[String, String]) extends Module {

   val prec:Int  = HardwareConfig("prec").toInt
   val out_terms:Int  = HardwareConfig("out_terms").toInt //Ratio, terms:1
   val fanout:Int  = HardwareConfig("fanout").toInt



	val io = IO(new Bundle{
		val in = Input( UInt(prec.W))
		val out = Output(Vec(out_terms, Vec(fanout, UInt(prec.W))))
		val en = Input(Bool())

		val entry = new EntryIO()
		val exit = new ExitIO()
	})


}


object DeserializerFactory {
  
  def create_general( HardwareConfig : Map[String, String] ): GenericDeserializer = {
		val hardwareType:String  = HardwareConfig("hardwareType").toString

		val out =  hardwareType match {
			case "MuxDeserializer" => new MuxDeserializer(HardwareConfig)
			case "ShiftDeserializer" => new ShiftDeserializer(HardwareConfig)

			case "Mux" => new MuxDeserializer(HardwareConfig)
			case "Shift" => new ShiftDeserializer(HardwareConfig)
	
			//Other types ...? SRAM or FIFO based?

			case _     => throw new IllegalArgumentException("Unknown GenericDeserializer type")
		}
	  out
	  
  }

  }
  

class MuxDeserializer( HardwareConfig:Map[String, String]) 
	extends GenericDeserializer(HardwareConfig){

		val onehot = RegInit(UIntToOH(0.U, width = out_terms))

		//special case = max_out terms ==1, then cannot use mux, must use the multicast
		if(out_terms == 1){

			io.entry.ready := 1.U
			io.exit.valid := 1.U		

			val multicast : Multicast = Module(new Multicast(HardwareConfig
				+  ("terms" -> 1.toString) 
				+ ("fanout" -> fanout.toString)
				+ ("buffered" -> true.toString)   
			))

			multicast.io.en := io.en
			multicast.io.in(0) := io.in
	
			for(j <- Array.range(0, fanout)){
				io.out(0)(j) := multicast.io.out(0)(j)
			}
	
		}else{	


		for (i <- Array.range(0, out_terms) ){


			val multicast : Multicast = Module(new Multicast(HardwareConfig
				+  ("terms" -> 1.toString) 
				+ ("fanout" -> fanout.toString)
				+ ("buffered" -> false.toString)   
			))
			val mux :MuxN= Module(new MuxN(HardwareConfig 
				+ ("terms" -> 2.toString) ))
			val data = Reg(UInt(prec.W))

			multicast.io.en := io.en
			multicast.io.in(0) := data
			for(j <- Array.range(0, fanout)){
				io.out(i)(j) := multicast.io.out(0)(j)
			}
			
			mux.io.in(0) := data
			mux.io.in(1) := io.in
			mux.io.sel := onehot(i)

			data := mux.io.out

		}

		val valid = Reg(UInt(1.W))
		// io.entry.ready := (cnt == 0) & io.entry.valid
		io.entry.ready := 1.U 
		valid := (onehot(out_terms-1) === 1.U)
		io.exit.valid := valid

		when(io.en){
			onehot := Cat(onehot(out_terms-2, 0), onehot(out_terms-1))
		}




	}//general case

		
}

class ShiftDeserializer( HardwareConfig:Map[String, String]) 
	extends GenericDeserializer(HardwareConfig){
	
		var data = Reg(Vec(out_terms ,UInt(prec.W)))

		data(out_terms - 1) := io.in

		for (i <- Array.range(1, out_terms)){
			when(io.en){
				data(i-1) := data(i)
			}
		}


		val cnt = Reg(UInt(prec.W))
		when(io.en){
			when(cnt === (out_terms-1).U){
				cnt := 0.U
			}.otherwise{
				cnt := cnt + 1.U
			}
		}


		for (i <- Array.range(0, out_terms) ){

			val multicast : Multicast = Module(new Multicast(HardwareConfig
				+  ("terms" -> 1.toString) 
				+ ("fanout" -> fanout.toString)
				+ ("buffered" -> false.toString)   
			))

			multicast.io.en := io.en
			multicast.io.in(0) := data(i)
			for(j <- Array.range(0, fanout)){
				io.out(i)(j) := multicast.io.out(0)(j)
			}
		}

		val valid = Reg(UInt(1.W))
		// io.entry.ready := (cnt == 0) & io.entry.valid
		io.entry.ready := 1.U 
		valid := (cnt === (out_terms-1).U)
		io.exit.valid := valid

		// 	// val mux :MuxN= Module(new MuxN(HardwareConfig 
		// 	// + ("terms" -> terms.toString) ))
		// val multicast : Multicast = Module(new Multicast(HardwareConfig
		// 	+  ("terms" -> 1.toString) 
		// 	+ ("fanout" -> fanout.toString)
		// 	+ ("buffered" -> false.toString)   
		// ))
	
		// val cnt = Reg(UInt(prec.W))
		// val data = Reg(Vec(terms,UInt(prec.W)))

		// // io.entry.ready := (cnt == 0) & io.entry.valid
		// io.entry.ready := (cnt === 0.U) && io.entry.valid
		// io.exit.valid := 1.U

		// when(cnt === 0.U){
		// 	data := io.in
		// }.otherwise{
		// 	for (i <- Array.range(1, terms)){
		// 		data(i-1) := data(i) 
		// 	}
		// }

		// multicast.io.in(0) := data(0)

		// when(io.en){
		// 	when(cnt === (terms-1).U){
		// 		cnt := 0.U
		// 	}.otherwise{
		// 		cnt := cnt + 1.U
		// 	}
		// }

		// multicast.io.en := io.en
		// // multicast.io.in(0) := mux.io.out

		// for(i <- Array.range(0, fanout)){
		// 	io.out(i) := multicast.io.out(0)(i)
		// }

}




/*
package networks

import chisel3._

import helper._
import chisel3.util._

//serial2parallel, a.k.a. deserializer
//deserializer

//1. Mux-based




//2. Shift Register-based



class GenericSerial2Parallel( HardwareConfig : Map[String, String]) extends Module {
	
  val prec:Int     = HardwareConfig("prec").toInt
  val terms:Int    = HardwareConfig("terms").toInt
  val fanout:Int   = HardwareConfig("fanout").toInt

  //1, 2, 4,.... meaning 1 term at a time until terms/inrate
  val inrate = HardwareConfig("inrate").toInt
		val io = IO(new Bundle{
			val in = Input(UInt(prec.W))
			val out = Output(Vec(fanout, UInt(prec.W)))
			val en = Input(Bool())
			val entry = new EntryIO()
			val exit = new ExitIO()
		})

}

class ShiftSerial2Parallel( HardwareConfig : Map[String, String]) extends GenericSerial2Parallel(HardwareConfig) {

	val buffers = Reg(Vec(UInt(prec.W)))	



  }




object Multiplier2Factory {

  //Create Core Adder (i.e. combinational logic)
  def create( HardwareConfig : Map[String, String]): GenericMultiplier2 = {
	  val buffered = HardwareConfig("buffered").toBoolean
	  // if(buffered == false){
		 //  create_general(HardwareConfig)
	  // }else{
		 //  create_buffered(HardwareConfig)
	  // }
	  create_general(HardwareConfig)
  }
  
  def create_general( HardwareConfig : Map[String, String] ): GenericMultiplier2 = {
		val signed = HardwareConfig("signed").toBoolean
		val multiplierType = HardwareConfig("multiplierType")

		//todos (sign)
		val out =   multiplierType match {
			case "SimpleMutiplier2" => new SimpleMultiplier2(HardwareConfig)
			case "HighRadixMultiplier" => new UIntHighRadixMultiplier2(HardwareConfig)
			case "BitSerialMultiplier" => new UIntBitSerialMultiplier(HardwareConfig)
			//Laconic, Pragmatic, Bitfusion, multi-precision, systolic, ...
			case _     => throw new IllegalArgumentException("Unknown mult2 type")
		}
	  
	  // if(signed == true ){
		  
		 //  class GenericSignedAdder2(HardwareConfig:Map[String,String]) extends GenericAdder2(HardwareConfig) {
			  
			//   val adder_core =  Module(create_general(HardwareConfig))
			  
			//   adder_core.io.A := io.A
			//   adder_core.io.B := io.B
			//   adder_core.io.entry <> io.entry
			//   adder_core.io.exit <> io.exit
			  
			//  var LEN = prec2
			//  if(prec1 > prec2){
			// 	 LEN = prec1
			//  }
			//   if(prec_sum <= LEN  ){
			// 	  io.Sum := adder_core.io.Sum 
			//   } else if (prec_sum == LEN + 1){
			// 	  io.Sum := Cat(  io.Cout , io.A + io.B )
			//   }else{
			// 	 io.Sum := Cat(  Fill( prec_sum-LEN-1, io.Cout) , io.Cout , io.A + io.B )
			//   }
			  
			  
		 //  }
		  
		 //  new GenericSignedAdder2(HardwareConfig)
		  
	  // }else{
		 //  out
	  // }
	  out
	  
  }
  

  
  
  
  // //Create Core Adder + input Buffer (i.e. 1-cycle adder)
  // def create_buffered( HardwareConfig : Map[String, String]): GenericAdder2 = {
	  
	 //  class GenericBufferedAdder2(HardwareConfig : Map[String, String]) 
		// extends GenericAdder2(HardwareConfig){
	    
		
	 //    val adder_core =  Module(create_general(HardwareConfig))
	    
		// val bufA = RegInit(0.U(prec1.W))
		// val bufB = RegInit(0.U(prec2.W))

		
		// val bufValid = RegInit(0.U(1.W))
		// //io.entry.ready := adder_core.io.entry.ready 
		// adder_core.io.A := bufA
		// adder_core.io.B := bufB
		// when(io.entry.ready & io.entry.valid){
		// 	bufA := io.A
		// 	bufB := io.B
		//     bufValid := 1.U
		// }  .otherwise {
		// 	bufValid := 0.U
		// }
		// io.Sum := adder_core.io.Sum
		// io.Cout := adder_core.io.Cout
		// io.exit.valid := bufValid & adder_core.io.exit.valid
		// adder_core.io.Cin := io.Cin
		// adder_core.io.entry <> io.entry
		// adder_core.io.exit.ready := io.exit.ready
		// io.entry.ready := adder_core.io.entry.ready
		// adder_core.io.entry.valid := io.entry.valid 
	 //  }

	 //  new GenericBufferedAdder2(HardwareConfig)
	  
  // }
  
  
  
  
  
}
*/
