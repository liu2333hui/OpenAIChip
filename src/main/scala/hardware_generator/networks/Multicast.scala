package networks


import chisel3._


//1 --> fanout broadcasting network
class Broadcast( fanout : Int, prec : Int , buffered : Boolean = false) extends Module {
		val io = IO(new Bundle{
			val in = Input(UInt(prec.W))
			val out = Output(Vec(fanout, UInt(prec.W)))
			val en = Input(Bool())
		})
		
		if(buffered){
		    val buf_in = Reg(UInt(prec.W))
			when(io.en){
				buf_in := io.in
			}
			
		    for (i <- 0 until fanout){
				io.out(i) := buf_in
			}
		}else{
			for (i <- 0 until fanout){
				io.out(i) := io.in
			}
		}
		
		
}	

		
//terms --> terms * fanout multicasting network
class Multicast( HardwareConfig : Map[String, String] ) extends Module{
	
	
	
	val terms : Int = HardwareConfig("terms").toInt
	val fanout :Int = HardwareConfig("fanout").toInt
	val prec:Int = HardwareConfig("prec").toInt
	val buffered:Boolean = HardwareConfig("buffered").toBoolean
	
	
	
	val io = IO(new Bundle{
		val in = Input(Vec(terms, UInt(prec.W)) )
		val out = Output(Vec( terms , Vec(fanout, UInt(prec.W)))  )
		val en = Input(Bool())
	})
	
	for(i <- 0 until terms){
	
		val bcast = Module(new Broadcast(fanout=fanout, prec=prec,buffered=buffered))
		bcast.io.en := io.en
		bcast.io.in := io.in(i)
		for (j <- 0 until fanout){	
		    io.out(i)(j) := bcast.io.out(j) 
		}
		
	}
	
	
}
