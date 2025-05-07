package maxmin

import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import networks.{Mux2}

//Max2
class Max2( HardwareConfig:Map[String, String]) extends Module {
	
  val prec:Int = HardwareConfig("prec").toInt
	
  val io = IO(new Bundle {
    val in0    = Input(UInt(prec.W))
    val in1    = Input(UInt(prec.W))
	val out = Output(UInt(prec.W))
  })  
  
	val mux = Module(new Mux2(HardwareConfig))

	val compare = io.in0 < io.in1

	mux.io.in0 := io.in0
	mux.io.in1 := io.in1
	mux.io.sel := compare

	io.out := mux.io.out

}

//MaxTreeN
//(todos generic tree structure for any arithmetic unit)
class MaxN(HardwareConfig:Map[String, String]) extends Module {
	
 val prec:Int  = HardwareConfig("prec").toInt
 val terms:Int = HardwareConfig("terms").toInt
	
  val io = IO(new Bundle {
    val in    = Input(Vec(terms, UInt(prec.W)))
	val out = Output(UInt(prec.W))
  })  
  
  // tree
  val root :Max2= Module(new Max2(HardwareConfig))
  io.out := root.io.out
  
  val cur_layer = Queue[Max2](root)
  for(i <- 1 until log2Ceil(terms)){
	  val cur_layer_len = cur_layer.length
		  for (j <- 0 until cur_layer_len){
			val element = cur_layer.dequeue()
			val childA : Max2 =  Module(new Max2(HardwareConfig))
			val childB : Max2 = Module(new Max2(HardwareConfig))
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

