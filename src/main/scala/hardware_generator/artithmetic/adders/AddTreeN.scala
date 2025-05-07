/*
Adder tree
输入, N个
1。用
2。

*/
// See LICENSE.txt for license details.
package adders

import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._

//加terms个值一起
class AddTreeN( HardwareConfig: Map[String, String]
	) extends GenericAdderN(HardwareConfig){



	//root
    val root : GenericAdder2 = Module(Adder2Factory.create(
		HardwareConfig + (("adderType",adderType), ("prec1", (prec_in+log2Ceil(terms)-1).toString),
		    ("prec2", (prec_in+log2Ceil(terms)-1).toString),
			("prec_sum", (prec_in+log2Ceil(terms)).toString),
			("buffered", buffered.toString)
		 )))
	val cur_layer = Queue[Module](root)
	
	
	//build children
	val N = terms - 1
	
	//layer
	for (i <- log2Ceil(terms)-2 to 0 by -1){
		val b = (N >> i) & 1
		val cur_layer_len = cur_layer.length
		println("cur_layer_len" + cur_layer_len)
		//每个元素
		for (j <- 0 until cur_layer_len){
			val element = cur_layer.dequeue()
				
			//是加法还是空的
			if(element.isInstanceOf[GenericAdder2])	{
				val elt : GenericAdder2 = element.asInstanceOf[GenericAdder2]
				
				val childA :GenericAdder2 = Module(Adder2Factory.create(
					HardwareConfig + (("adderType",adderType), ("prec1", (prec_in+i).toString),
						("prec2", (prec_in + i).toString),
						("prec_sum", (prec_in + i+1).toString),
						("buffered", buffered.toString)
					 )))
		 
				elt.io.A := childA.io.Sum
				if(b == 0){
					val childB :EntryExitWire = Module(new EntryExitWire(prec_in + i , prec_in + i+1) )
					println(elt.io.B+"\t"+ childB.io.out)
					elt.io.B := childB.io.out
					
					elt.io.entry <> childA.io.exit
					elt.io.entry <> childB.io.exit
					cur_layer.enqueue(childA)
					cur_layer.enqueue(childB)
					
				} else{
					val childB :GenericAdder2 = Module(Adder2Factory.create(
						HardwareConfig + (("adderType",adderType), ("prec1", (prec_in+i).toString),
							("prec2", (prec_in + i).toString),
							("prec_sum", (prec_in + i+1).toString),
							("buffered", buffered.toString)
						 )))
					elt.io.B := childB.io.Sum
					
									elt.io.entry <> childA.io.exit
									elt.io.entry <> childB.io.exit
									cur_layer.enqueue(childA)
									cur_layer.enqueue(childB)
				}
				
				elt.io.Cin := 0.U
				
				
			} else{
				val elt : EntryExitWire = element.asInstanceOf[EntryExitWire]
				if(b == 0){
					val childB :EntryExitWire = Module(new EntryExitWire(prec_in + i , prec_in + i+1) )
					elt.io.in := childB.io.out
					
					elt.io.entry <> childB.io.exit
					cur_layer.enqueue(childB)
					
				} else{
					val childB :GenericAdder2 = Module(Adder2Factory.create(
						HardwareConfig + (("adderType",adderType), ("prec1", (prec_in+i).toString),
							("prec2", (prec_in + i).toString),
							("prec_sum", (prec_in + i+1).toString),
							("buffered", buffered.toString)
						 )))
					elt.io.in := childB.io.Sum
					
					elt.io.entry <> childB.io.exit
					cur_layer.enqueue(childB)
				}
				
				
			}
		}
	}
	
	//connect io
	var idx : Int = 0
	//val in_rdy = Wire(UInt(terms.W))
	
	println(cur_layer.length + "\t"+terms)
	for (element <- cur_layer){
			println("elt\t" + element)
	}
	for (element <- cur_layer){
		if(element.isInstanceOf[GenericAdder2])	{
			val elt : GenericAdder2 = element.asInstanceOf[GenericAdder2]
			elt.io.A := io.A(idx)
			elt.io.B := io.A(idx+1)
			
			//in_rdy(idx) := elt.io.entry.ready
			//in_rdy(idx + 1) := elt.io.entry.ready
			
			idx = idx+ 2
			
			elt.io.Cin := 0.U
			elt.io.entry.valid := io.entry.valid
			
		} else {
			val elt : EntryExitWire = element.asInstanceOf[EntryExitWire]
			elt.io.in := io.A(idx)
			
			//in_rdy(idx) := elt.io.entry.ready
			idx = idx + 1
			
			elt.io.entry.valid := io.entry.valid
			
		}
	
		
		
	}
	
	io.Sum := root.io.Sum
	root.io.Cin := 0.U
	//io.exit.valid :=  1.U //root.io.exit.valid
	io.entry.ready :=  1.U //in_rdy.reduceLeft(_ & _)
	root.io.exit <> io.exit
    
	
}
