package exponent

import chisel3._
import chisel3.util._

import memories.LUT
import java.lang.Math


//AI half generated
//Should support signed numbers
class ExponentLUT( HardwareConfig:Map[String, String]) extends 
    LUT(HardwareConfig) {
	
  // 这里可以根据需要初始化 LUT 的内容
  // 示例：将 LUT 初始化为索引值乘以 2
  for (i <- 0 until (1 << prec_in) ) {
    var expValue = 1.0
    val sign = (i > (1<<(prec_in-1)))
    var x = (i % (1<<(prec_in-1))).toDouble / (1<<(prec_in-1))
    if(sign){
        expValue = Math.exp(-x)
    }else{
        expValue = Math.exp(-x)
    }
    lut(i) := (expValue * (1 << prec_out)).toInt.U
    // lut(i) := (i * 2).U
  }

}
