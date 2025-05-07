package networks

import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue

//Mux2
class Mux2( HardwareConfig:Map[String, String]) extends Module {
	
  val prec:Int = HardwareConfig("prec").toInt
	
  val io = IO(new Bundle {
    val in0    = Input(UInt(prec.W))
    val in1    = Input(UInt(prec.W))
    val sel = Input(Bool())
	val out = Output(UInt(prec.W))
  })  
  
  when(io.sel){
	  io.out := io.in1
  } .otherwise{
	  io.out := io.in0
  }
  
}

//MuxN
class MuxN(HardwareConfig:Map[String, String]) extends Module {
	
 val prec:Int  = HardwareConfig("prec").toInt
 val terms:Int = HardwareConfig("terms").toInt
	
  val io = IO(new Bundle {
    val in    = Input(Vec(terms, UInt(prec.W)))
    val sel = Input(UInt(log2Ceil(terms).W))
	val out = Output(UInt(prec.W))
  })  

  
  val sel_reverse  = Wire(Vec(log2Ceil(terms), UInt(1.W)))
  for (i <- 0 until log2Ceil(terms)){
	  sel_reverse(i) := io.sel(log2Ceil(terms)-1-i)
  }
  
  //Multiplexer tree
  val root :Mux2= Module(new Mux2(HardwareConfig))
  root.io.sel := sel_reverse(0)
  io.out := root.io.out
  
  val cur_layer = Queue[Mux2](root)
  for(i <- 1 until log2Ceil(terms)){
	  val cur_layer_len = cur_layer.length
		  for (j <- 0 until cur_layer_len){
			val element = cur_layer.dequeue()
			val childA : Mux2 =  Module(new Mux2(HardwareConfig))
			val childB : Mux2 = Module(new Mux2(HardwareConfig))
			childA.io.sel := sel_reverse(i)
			childB.io.sel := sel_reverse(i)
			element.io.in0 := childA.io.out 
			element.io.in1 := childB.io.out 
			cur_layer.enqueue(childA)
			cur_layer.enqueue(childB)
		  }
   }
	
	var idx = 0
	val cur_layer_len = cur_layer.length
	for (j <- 0 until cur_layer_len){
	val element = cur_layer.dequeue()
	element.io.in0 := io.in(idx) 
	element.io.in1 := io.in(idx+1)
	idx = idx+ 2
	}	

	
}

