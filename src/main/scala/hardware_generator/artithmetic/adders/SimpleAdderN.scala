package adders

import chisel3._

class SimpleAdderN(HardwareConfig: Map[String, String]
	) extends GenericAdderN(HardwareConfig) {
		
    var root = Wire(UInt(prec_sum.W))
	root := io.A(0)
	
    for(i <- 1 until terms){
		val psum = Wire(UInt(prec_sum.W))
		psum := root + io.A(i)
		root = psum
	}

    io.Sum := root
    //io.Sum := io.A.reduceLeft(_ + _)
  
    io.entry.ready := 1.U
	io.exit.valid := 1.U
}

