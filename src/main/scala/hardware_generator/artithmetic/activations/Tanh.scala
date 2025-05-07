package activations

import chisel3._
import chisel3.util._

import memories.LUT
import java.lang.Math


object Tanh {
  def tanh(x: Double): Double = {
    Math.tanh(x)
  }
}


//AI half generated
class TanhLUT( HardwareConfig:Map[String, String]) extends 
    LUT(HardwareConfig) {
	
  // 这里可以根据需要初始化 LUT 的内容
  // 示例：将 LUT 初始化为索引值乘以 2
  for (i <- 0 until (1 << prec_in) ) {
    val x = i.toDouble / (1<<prec_in)
    val Value = Tanh.tanh(x)
    lut(i) := (Value * (1 << prec_out)).toInt.U
    // lut(i) := (i * 2).U
  }

}

//(todos)
// SigmoidInterpolate