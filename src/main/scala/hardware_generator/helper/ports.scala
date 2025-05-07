package helper

import chisel3._

class EntryIO extends Bundle {
	val valid = Input(Bool())
	val ready = Output(Bool())
}

class ExitIO extends Bundle {
	val valid = Output(Bool())
	val ready = Input(Bool())
}


class FloatingPoint(exp:Int, mant:Int) extends Bundle {
	val sign = Input(UInt(1.W))
	val exponent = Input(UInt(exp.W))
	val mantissa = Input(UInt(mant.W))
}

