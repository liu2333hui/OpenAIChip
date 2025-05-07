
package memories

//Use blackbox for SRAM base
import chisel3.util.HasBlackBoxResource
import chisel3._
import chisel3.util._
import chisel3.util.experimental.loadMemoryFromFile
import chisel3.util.experimental._

/*
    How to test the SRAM Bank
	1. Reads 
	2. Writes
	3. Read + Writes
	4. Idle
*/
abstract class GenericSRAMBank(HardwareConfig: Map[String, String]  ) extends BlackBox with HasBlackBoxResource {
	// val folder = HardwareConfig("folder")
	val entry_bits = HardwareConfig("entry_bits").toInt
	val rows = HardwareConfig("rows").toInt
	val sram_name = HardwareConfig("sram_type")
	val addr_bits = log2Ceil(rows)
	
}



class BankedSRAM(HardwareConfig: Map[String, String]) extends Module {
	val entry_bits = HardwareConfig("entry_bits").toInt
	val rows = HardwareConfig("rows").toInt
	val sram_name = HardwareConfig("sram_type")
	
	val addr_bits = log2Ceil(rows)
	
	
	val io = IO(new Bundle{
		val ADDRESS = Input(UInt(addr_bits.W))
		val wd = Input(UInt(entry_bits.W)) //write data
		val banksel = Input(Bool())
        val read = Input(Bool())
		val dataout = Output(UInt(entry_bits.W)) //read data
		val write = Input(Bool())
	})	
	
	val m = Module(new srambank_64x4x16_6t122(HardwareConfig))
	
	m.io.ADDRESS:=io.ADDRESS
	m.io.wd:=io.wd 
	m.io.banksel:=io.banksel 
	m.io.read :=io.read 
	io.dataout := m.io.dataout
	m.io.write := io.write
	m.io.clk := clock
	// m.io.clk := clock
	
}


object MultibankSramFactory{
	
}

object BankSramFactory{
	def create(){
		
	}
}

// class SRAMBanked(HardwareConfig: Map[String, String]) extends Module {
// 	//...
// }

//统一API
class SRAMBankedASAP7(HardwareConfig: Map[String, String]) extends Module {
	
	val entry_bits = HardwareConfig("entry_bits").toInt
	val rows = HardwareConfig("rows").toInt
	val addr_bits = log2Ceil(rows)
	
	val io = IO(new Bundle{
		val read_address = Input(UInt(addr_bits.W))
		val write_address = Input(UInt(addr_bits.W))
		val banksel = Input(Bool())
		val rw_mode = Input(Bool()) //r == 0, w == 1
		val read_data = Output(UInt(entry_bits.W)) //read data
		val write_data= Input(UInt(entry_bits.W)) //write data
	})	

	

    val mi = (HardwareConfig("entry_bits"), HardwareConfig("rows")) match {
      case ("16", "256") => Module(new srambank_64x4x16_6t122(HardwareConfig) )
      case ("18", "256") => Module(new srambank_64x4x18_6t122(HardwareConfig) )
      case ("20", "256") => Module(new srambank_64x4x20_6t122(HardwareConfig) )
      case ("32", "256") => Module(new srambank_64x4x32_6t122(HardwareConfig) )
      case ("34", "256") => Module(new srambank_64x4x34_6t122(HardwareConfig) )
      case ("36", "256") => Module(new srambank_64x4x36_6t122(HardwareConfig) )
      case ("40", "256") => Module(new srambank_64x4x40_6t122(HardwareConfig) )
      case ("48", "256") => Module(new srambank_64x4x48_6t122(HardwareConfig) )
      case ("64", "256") => Module(new srambank_64x4x64_6t122(HardwareConfig) )
      case ("72", "256") => Module(new srambank_64x4x72_6t122(HardwareConfig) )
      case ("74", "256") => Module(new srambank_64x4x74_6t122(HardwareConfig) )
      case ("80", "256") => Module(new srambank_64x4x80_6t122(HardwareConfig) )
     case ("16", "512") =>  Module(new srambank_128x4x16_6t122(HardwareConfig))
     case ("18", "512") =>  Module(new srambank_128x4x18_6t122(HardwareConfig))
     case ("20", "512") =>  Module(new srambank_128x4x20_6t122(HardwareConfig))
     case ("32", "512") =>  Module(new srambank_128x4x32_6t122(HardwareConfig))
     case ("34", "512") =>  Module(new srambank_128x4x34_6t122(HardwareConfig))
     case ("36", "512") =>  Module(new srambank_128x4x36_6t122(HardwareConfig))
     case ("40", "512") =>  Module(new srambank_128x4x40_6t122(HardwareConfig))
     case ("48", "512") =>  Module(new srambank_128x4x48_6t122(HardwareConfig))
     case ("64", "512") =>  Module(new srambank_128x4x64_6t122(HardwareConfig))
     case ("72", "512") =>  Module(new srambank_128x4x72_6t122(HardwareConfig))
     case ("74", "512") =>  Module(new srambank_128x4x74_6t122(HardwareConfig))
     case ("80", "512") =>  Module(new srambank_128x4x80_6t122(HardwareConfig))
    case ("16", "1024") =>  Module(new srambank_256x4x16_6t122(HardwareConfig))
    case ("18", "1024") =>  Module(new srambank_256x4x18_6t122(HardwareConfig))
    case ("20", "1024") =>  Module(new srambank_256x4x20_6t122(HardwareConfig))
    case ("32", "1024") =>  Module(new srambank_256x4x32_6t122(HardwareConfig))
    case ("34", "1024") =>  Module(new srambank_256x4x34_6t122(HardwareConfig))
    case ("36", "1024") =>  Module(new srambank_256x4x36_6t122(HardwareConfig))
    case ("40", "1024") =>  Module(new srambank_256x4x40_6t122(HardwareConfig))
    case ("48", "1024") =>  Module(new srambank_256x4x48_6t122(HardwareConfig))
    case ("64", "1024") =>  Module(new srambank_256x4x64_6t122(HardwareConfig))
    case ("72", "1024") =>  Module(new srambank_256x4x72_6t122(HardwareConfig))
    case ("74", "1024") =>  Module(new srambank_256x4x74_6t122(HardwareConfig))
    case ("80", "1024") =>  Module(new srambank_256x4x80_6t122(HardwareConfig))
    case _ => throw new IllegalArgumentException("Unsupported cHardwareConfig, Choose from this list: (16-80, 256-1024) ")
  }
  
	val m = mi
    		
	when(io.rw_mode){
		m.io.read := 1.U
		m.io.write:= 0.U
		m.io.ADDRESS :=io.read_address
	
		
	}.otherwise{
	
		m.io.read := 0.U
		m.io.write:= 1.U
		m.io.ADDRESS := io.write_address
	
	}

	m.io.wd        := io.write_data 
	m.io.banksel   := io.banksel 
	io.read_data   := m.io.dataout
	m.io.clk       := clock
	
}



///////////////////////////////////////////////////////////////////////////////////////
//SRAM types
// 1. simultaneous read/write (i.e. Register File)
// 2. non-simultaneous read/write (i.e. SRAM)
// 3. only read (i.e. ROM)

class ASAP7Base(HardwareConfig: Map[String, String]) extends Module {
	//} with HasBlackBoxResource  {
	val entry_bits = HardwareConfig("entry_bits").toInt
	val rows = HardwareConfig("rows").toInt
	
	val addr_bits = log2Ceil(rows)
	
	val io = IO(new Bundle{
		val clk   = Input(Clock())
		val ADDRESS = Input(UInt(addr_bits.W))
		val wd      = Input(UInt(entry_bits.W)) //write data
		val banksel = Input(Bool())
	    val read = Input(Bool())
		val dataout = Output(UInt(entry_bits.W)) //read data
		val write = Input(Bool())
	})	
	
	val rows_div_4 :Int = rows / 4 
	//get it from the github repo (todos link)
	// addPath(s"./src/main/resources/asap7_sram_0p0/generated/verilog/srambank_${rows_div_4}x4x${entry_bits}_6t122.v")
	
	  // 定义 SRAM
	  val sram = SyncReadMem(entry_bits*rows, UInt(entry_bits.W))
	
	val dataout = Wire(UInt(entry_bits.W))
	
	withClock(io.clk) {
	  // 写操作
	  when(io.banksel & io.write) {
	    sram.write(io.ADDRESS, io.wd)
		dataout := 0.U
	  }.elsewhen(io.banksel & io.read){  
		dataout := sram.read(io.ADDRESS)
	  }.otherwise{
		  dataout := 0.U
	  }
	  
	  io.dataout := dataout
	
	  // 读操作
	  
	}
	
	
	// addResource(s"/asap7_sram_0p0/generated/verilog/srambank_${rows_div_4}x4x${entry_bits}_6t122.v")
	
	
}
//ASAP
class srambank_64x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "16"), ("rows", "256"))
)

class srambank_64x4x18_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "18"), ("rows", "256"))
)

class srambank_64x4x20_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "20"), ("rows", "256"))
)

class srambank_64x4x32_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "32"), ("rows", "256"))
)

class srambank_64x4x34_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "34"), ("rows", "256"))
)

class srambank_64x4x36_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "36"), ("rows", "256"))
)

class srambank_64x4x40_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "40"), ("rows", "256"))
)

class srambank_64x4x48_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "48"), ("rows", "256"))
)

class srambank_64x4x64_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "64"), ("rows", "256"))
)

class srambank_64x4x72_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "72"), ("rows", "256"))
)

class srambank_64x4x74_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "74"), ("rows", "256"))
)

class srambank_64x4x80_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "80"), ("rows", "256"))
)

class srambank_128x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "16"), ("rows", "512"))
)

class srambank_128x4x18_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "18"), ("rows", "512"))
)

class srambank_128x4x20_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "20"), ("rows", "512"))
)

class srambank_128x4x32_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "32"), ("rows", "512"))
)

class srambank_128x4x34_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "34"), ("rows", "512"))
)

class srambank_128x4x36_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "36"), ("rows", "512"))
)

class srambank_128x4x40_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "40"), ("rows", "512"))
)

class srambank_128x4x48_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "48"), ("rows", "512"))
)

class srambank_128x4x64_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "64"), ("rows", "512"))
)

class srambank_128x4x72_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "72"), ("rows", "512"))
)

class srambank_128x4x74_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "74"), ("rows", "512"))
)

class srambank_128x4x80_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "80"), ("rows", "512"))
)


class srambank_256x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "16"), ("rows", "1024"))
)

class srambank_256x4x18_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "18"), ("rows", "1024"))
)

class srambank_256x4x20_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "20"), ("rows", "1024"))
)

class srambank_256x4x32_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "32"), ("rows", "1024"))
)

class srambank_256x4x34_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "34"), ("rows", "1024"))
)

class srambank_256x4x36_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "36"), ("rows", "1024"))
)

class srambank_256x4x40_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "40"), ("rows", "1024"))
)

class srambank_256x4x48_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "48"), ("rows", "1024"))
)

class srambank_256x4x64_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "64"), ("rows", "1024"))
)

class srambank_256x4x72_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "72"), ("rows", "1024"))
)

class srambank_256x4x74_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "74"), ("rows", "1024"))
)

class srambank_256x4x80_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
    Map(("entry_bits", "80"), ("rows", "1024"))
)

////////////////////////////////////////////////////////////////////////////

// class srambank_64x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
// 	Map(("entry_bits", "16"), ("rows", "256"))
// )
 
//  class srambank_64x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
//  	Map(("entry_bits", "16"), ("rows", "256"))
//  )
 
//  class srambank_64x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
//  	Map(("entry_bits", "16"), ("rows", "256"))
//  )
 
//  class srambank_64x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
//  	Map(("entry_bits", "16"), ("rows", "256"))
//  )
 
//  class srambank_64x4x16_6t122(HardwareConfig: Map[String, String]) extends ASAP7Base(
//  	Map(("entry_bits", "16"), ("rows", "256"))
//  )
 
//extends BlackBox with HasBlackBoxResource {
// 	val entry_bits = HardwareConfig("entry_bits").toInt
// 	val rows = HardwareConfig("rows").toInt
// 	val sram_name = HardwareConfig("sram_type")
	
// 	val addr_bits = log2Ceil(rows)
	
// 	val io = IO(new Bundle{
// 		val clk   = Input(Clock())
// 		val ADDRESS = Input(UInt(addr_bits.W))
// 		val wd = Input(UInt(entry_bits.W)) //write data
// 		val banksel = Input(Bool())
//         val read = Input(Bool())
// 		val dataout = Output(UInt(entry_bits.W)) //read data
// 		val write = Input(Bool())
// 	})	
	
// 	val rows_div_4 :Int = rows / 4 
// 	//get it from the github repo (todos link)
// 	// addPath(s"./src/main/resources/asap7_sram_0p0/generated/verilog/srambank_${rows_div_4}x4x${entry_bits}_6t122.v")
// 	addResource(s"/asap7_sram_0p0/generated/verilog/srambank_${rows_div_4}x4x${entry_bits}_6t122.v")
	

// }


class TSMC40SramBank(HardwareConfig: Map[String, String]) extends GenericSRAMBank(HardwareConfig){
	
	val io = IO(new Bundle{
		val read_addr = Input(UInt(addr_bits.W))
		val read_data = Output(UInt(entry_bits.W))
        val read_en = Input(Bool())
				
		val write_addr = Input(UInt(addr_bits.W))
		val write_data = Input(UInt(entry_bits.W))
		val write_en = Input(Bool())
		
	})
	
	// addResource(s"/${folder}/${sram_name}_${entry_bits}x${rows}.v")
}

// class NANGATE45SramBank(HardwareConfig: Map[String, String]) extends GenericSRAMBank(HardwareConfig){
	
// 	val io = IO(new Bundle{
// 		val read_addr = Input(UInt(addr_bits.W))
// 		val read_data = Output(UInt(entry_bits.W))
// 	    val read_en = Input(Bool())
				
// 		val write_addr = Input(UInt(addr_bits.W))
// 		val write_data = Input(UInt(entry_bits.W))
// 		val write_en = Input(Bool())
		
// 	})
	
// 	// addResource(s"/${folder}/${sram_name}_${entry_bits}_${rows}.v")
// }


class NANGATE45SramBank(HardwareConfig: Map[String, String]) extends GenericSRAMBank(HardwareConfig){
	
	val io = IO(new Bundle{
		val read_addr = Input(UInt(addr_bits.W))
		val read_data = Output(UInt(entry_bits.W))
	    val read_en = Input(Bool())
				
		val write_addr = Input(UInt(addr_bits.W))
		val write_data = Input(UInt(entry_bits.W))
		val write_en = Input(Bool())
		
	})
	
	// addResource(s"/${folder}/${sram_name}_${entry_bits}_${rows}.v")
}

class TSMC28SramBank(){
	
}

