//Parallel2Serial, Serializer
package networks

import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._

//Used in systolic flows
class GenericParallel2Serial( HardwareConfig:Map[String, String]) extends Module {

   val prec:Int  = HardwareConfig("prec").toInt
   val terms:Int  = HardwareConfig("terms").toInt //Ratio, terms:1
   val fanout:Int  = HardwareConfig("fanout").toInt



	val io = IO(new Bundle{
		val in = Input(Vec(terms, UInt(prec.W)))
		val out = Output(Vec(fanout, UInt(prec.W)))
		val en = Input(Bool())

		val entry = new EntryIO()
		val exit = new ExitIO()
	})


}


object Parallel2SerialFactory {
  
  def create_general( HardwareConfig : Map[String, String] ): GenericParallel2Serial = {
		val hardwareType:String  = HardwareConfig("hardwareType").toString

		val out =  hardwareType match {
			case "MuxParallel2Serial" => new MuxParallel2Serial(HardwareConfig)
			case "ShiftParallel2Serial" => new ShiftParallel2Serial(HardwareConfig)
			case "Mux" => new MuxParallel2Serial(HardwareConfig)
			case "Shift" => new ShiftParallel2Serial(HardwareConfig)
	
			//Other types ...? SRAM or FIFO based?

			case _     => throw new IllegalArgumentException("Unknown Parallel2Serial type")
		}
	  out
	  
  }

  }
  

class MuxParallel2Serial( HardwareConfig:Map[String, String]) 
	extends GenericParallel2Serial(HardwareConfig){

		//special case = max_out terms ==1, then cannot use mux, must use the multicast
		if(terms == 1){
			io.entry.ready := 1.U
			io.exit.valid := 1.U		

			val multicast : Multicast = Module(new Multicast(HardwareConfig
				+  ("terms" -> 1.toString) 
				+ ("fanout" -> fanout.toString)
				+ ("buffered" -> true.toString)   
			))

			multicast.io.en := io.en
			for (j <- Array.range(0, terms)){

				multicast.io.in(j) := io.in(j)
	
			}

				/*
			for(i <- Array.range(0, fanout)){
				io.out(i) := multicast.io.out(0)(i)
			}
				*/	

			for (l <- Array.range(0, terms)){
				for(k <- Array.range(0, fanout)){
					io.out(k) := multicast.io.out(l)(k)
				}
			}

	
		} else {


		val mux :MuxN= Module(new MuxN(HardwareConfig 
			+ ("terms" -> terms.toString) ))
		val multicast : Multicast = Module(new Multicast(HardwareConfig
			+  ("terms" -> 1.toString) 
			+ ("fanout" -> fanout.toString)
			+ ("buffered" -> false.toString)   
		))
	
		val cnt = Reg(UInt(prec.W))
		val data = Reg(Vec(terms,UInt(prec.W)))

		// io.entry.ready := (cnt == 0) & io.entry.valid
		io.entry.ready := (cnt === 0.U) && io.entry.valid
		io.exit.valid := 1.U

		when(cnt === 0.U){
			data := io.in
		}


		when(io.en){
			when(cnt === (terms-1).U){
				cnt := 0.U
			}.otherwise{
				cnt := cnt + 1.U
			}
		}

		multicast.io.en := io.en
		multicast.io.in(0) := mux.io.out

		for(i <- Array.range(0, fanout)){
			io.out(i) := multicast.io.out(0)(i)
		}
		
		mux.io.in := data
		mux.io.sel := cnt
		
	}
}

class ShiftParallel2Serial( HardwareConfig:Map[String, String]) 
	extends GenericParallel2Serial(HardwareConfig){
	

			// val mux :MuxN= Module(new MuxN(HardwareConfig 
			// + ("terms" -> terms.toString) ))
		val multicast : Multicast = Module(new Multicast(HardwareConfig
			+  ("terms" -> 1.toString) 
			+ ("fanout" -> fanout.toString)
			+ ("buffered" -> false.toString)   
		))
	
		val cnt = Reg(UInt(prec.W))
		val data = Reg(Vec(terms,UInt(prec.W)))

		// io.entry.ready := (cnt == 0) & io.entry.valid
		io.entry.ready := (cnt === 0.U) && io.entry.valid
		io.exit.valid := 1.U

		when(cnt === 0.U){
			data := io.in
		}.otherwise{
			for (i <- Array.range(1, terms)){
				data(i-1) := data(i) 
			}
		}

		multicast.io.in(0) := data(0)

		when(io.en){
			when(cnt === (terms-1).U){
				cnt := 0.U
			}.otherwise{
				cnt := cnt + 1.U
			}
		}

		multicast.io.en := io.en
		// multicast.io.in(0) := mux.io.out

		for(i <- Array.range(0, fanout)){
			io.out(i) := multicast.io.out(0)(i)
		}
		
		// mux.io.in := data
		// mux.io.sel := cnt


	// loading
	// val data = Reg(UInt(prec.W))
	
	// io.out := data(out_prec-1, 0)		

	// when(io.en){
	// when(io.mode === 0.U){
	// 	data := io.in		
	// }.otherwise{
		
	// 	data := Cat(data(out_prec-1, 0)  , data(in_prec-1,out_prec ) ) 
	// }
	// }


}
