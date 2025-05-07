// import chisel3._
// import chisel3.util._
// import networks.Mux2


// class SimpleFloatingAdd(  HardwareConfig : Map[String, String]) extends GenericFloatingPoint2Port(HardwareConfig) {
	
// 	// 对齐指数
// 	val maxExp = Wire(UInt(out_exponent.W))
// 	val max_exp = Mux(io.A.exponent >= io.B.exponent, 
// 		io.A.exponent, io.B.exponent)
// 	maxExp := max_exp

// 	val alignedMantissaA = Wire(UInt(out_mantissa.W))
// 	val alignedMantissaB = Wire(UInt(out_mantissa.W))
	
// 	val alignedMantissaA = a_mantissa << (maxExp - io.A.exponent)//Mux(a_exponent >= b_exponent, a_mantissa, a_mantissa >> expDiff)
// 	val alignedMantissaB = b_mantissa << (maxExp - io.B.exponent)//Mux(b_exponent >= a_exponent, b_mantissa, b_mantissa >> expDiff)

// 	// 加法
// 	val sumMantissa = Wire(UInt(out_mantissa.W))
// 	sumMantissa := alignedMantissaA + alignedMantissaB

// 	// 处理溢出
// 	// .. --> 1.123 + 1.312 --> carry 
// 	val overflow = sumMantissa(out_mantissa)
	
// 	val finalMantissa = Mux(overflow, sumMantissa >> 1, sumMantissa)
// 	val finalExp = Mux(overflow, maxExp + 1.U, maxExp)
// 	val finalSign = ?

// 	// 组合结果
// 	io.out.exponent := finalExp
// 	io.out.mantissa := finalMantissa
// 	io.out.sign := finalSign
// }

	