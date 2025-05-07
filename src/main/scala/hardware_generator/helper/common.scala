package helper

import chisel3._



class EntryExitWire( val prec_in:Int, val prec_out:Int ) extends Module {
  val io = IO(new Bundle {
    val in    = Input(UInt(prec_in.W))
    val out  = Output(UInt(prec_out.W))
	
	
	val entry = new EntryIO()
	val exit = new ExitIO()
	
	
  })
  
  io.out := io.in
  io.exit <> io.entry
}
