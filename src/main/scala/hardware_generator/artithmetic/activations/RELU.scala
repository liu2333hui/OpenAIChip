package activations

import chisel3._
import chisel3.util._

import memories.LUT



//AI half generated
class ReluLUT( HardwareConfig:Map[String, String]) extends 
    LUT(HardwareConfig) {
	
  // 这里可以根据需要初始化 LUT 的内容
  // 示例：将 LUT 初始化为索引值乘以 2
  for (i <- 0 until (1 << prec_in) ) {

    var num = i 
    if(i > (1<<prec_in-1) ){
      num = 0
    }
    lut(i) := num.U
  }

}


//Essentially a Mux2
class ReluSimple( HardwareConfig:Map[String, String]) extends 
     Module{


  val prec_in:Int = HardwareConfig("prec_in").toInt
  val prec_out:Int = HardwareConfig("prec_out").toInt

  val io = IO(new Bundle {
    val in = Input(UInt(prec_in.W))
    val out = Output(UInt(prec_out.W))
  })

    when(io.in(prec_in-1) === 1.U){
      io.out := 0.U
    }.otherwise{
      io.out := io.in
    }

}
