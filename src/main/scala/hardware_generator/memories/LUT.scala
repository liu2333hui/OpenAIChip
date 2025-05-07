//LUT can have many forms
//1. ROM or RAM
//2. SRAM base, REGISTER base, Multiplexer base

// SRAM used for:
// 1. Buffers (L1, L2)
// 2. ROMS, LUT-calculation
// 3. Accumulation (slow)
// 4. FIFO (slow)

// Register File used for:
// 1. Register Files / Scratchpads
// 2. LUT-calculation
// 3. Accumulation (fast)
// 4. FIFO (fast)

package memories

import chisel3._
import chisel3.util._

//AI half generated
class LUT( HardwareConfig:Map[String, String]) extends Module {
	
  val prec_in:Int = HardwareConfig("prec_in").toInt
  val prec_out:Int = HardwareConfig("prec_out").toInt

  val io = IO(new Bundle {
    // 输入索引，因为有 256 行，所以索引需要 8 位
    val in = Input(UInt(prec_in.W))
    // 输出数据，这里假设数据位宽为 32 位，可按需修改
    val out = Output(UInt(prec_out.W))
  })


  // 初始化一个 256 行、每行 32 位的 Mem 来作为 LUT
  val lut = Mem(1<<prec_in, UInt(prec_out.W))


  // 根据输入索引从 LUT 中读取数据
  io.out := lut(io.in)

}

