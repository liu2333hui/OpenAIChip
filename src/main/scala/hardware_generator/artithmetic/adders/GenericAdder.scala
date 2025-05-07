package adders

import chisel3._

import helper._

import chisel3.util._

//A 2-bit adder
class GenericAdder2(  HardwareConfig : Map[String, String]) extends Module {
	
	val prec1 = HardwareConfig("prec1").toInt
	
	var prec2 = 8
	if(HardwareConfig("same_prec").toBoolean){
		prec2 = prec1
	}else{
		prec2 = HardwareConfig("prec2").toInt
	}
	
	val prec_sum = HardwareConfig("prec_sum").toInt
	
	
  val io = IO(new Bundle {
    val A    = Input(UInt(prec1.W))
    val B    = Input(UInt(prec2.W))
    val Sum  = Output(UInt(prec_sum.W))
	
	val Cin = Input(UInt(1.W))
	val Cout = Output(UInt(1.W))
	
	val entry = new EntryIO()
	val exit = new ExitIO()
	
  })
  
  
}




object Adder2Factory {
	
  //Create Core Adder (i.e. combinational logic)
  def create( HardwareConfig : Map[String, String]): GenericAdder2 = {
	  val buffered = HardwareConfig("buffered").toBoolean
	  
	  if(buffered == false){
		  create_general(HardwareConfig)
	  }else{
		  create_buffered(HardwareConfig)
	  }
	  
	  
  }
  

  
  
  def create_general( HardwareConfig : Map[String, String] ): GenericAdder2 = {
	  
	  val signed = false//HardwareConfig("signed").toBoolean
	  val adderType = HardwareConfig("adderType")
	  
	  val out =   adderType match {
    case "SimpleAdder2" => new SimpleAdder2(HardwareConfig)
    case "RCAAdder2" => new RCAAdder2(HardwareConfig)
	//case "CLAAdder2"
	//case "Brunt-KungAdder2"
	//case "Stone-Adder2"
	//case "Adder2"
    case _     => throw new IllegalArgumentException("Unknown adder2 type")
  }
	  
	  if(signed == true){
		  
		  class GenericSignedAdder2(HardwareConfig:Map[String,String]) extends GenericAdder2(HardwareConfig) {
			  
			  val adder_core =  Module(create_general(HardwareConfig))
			  
			  adder_core.io.A := io.A
			  adder_core.io.B := io.B
			  adder_core.io.entry <> io.entry
			  adder_core.io.exit <> io.exit
			  
			  //Cat(  Fill( prec_sum-LEN-1, io.Cout) , io.Cout , io.A + io.B ).asUInt
			 var LEN = prec2
			 if(prec1 > prec2){
				 LEN = prec1
			 }
			  if(prec_sum <= LEN  ){
				  io.Sum := adder_core.io.Sum 
			  } else if (prec_sum == LEN + 1){
				  io.Sum := Cat(  io.Cout , io.A + io.B )
			  }else{
				 io.Sum := Cat(  Fill( prec_sum-LEN-1, io.Cout) , io.Cout , io.A + io.B )
			  }
			  
			  
		  }
		  
		  new GenericSignedAdder2(HardwareConfig)
		  
	  }else{
		  println("unsigned")
		  out
	  }
	  
	  
  }
  

  
  
  
  //Create Core Adder + input Buffer (i.e. 1-cycle adder)
  def create_buffered( HardwareConfig : Map[String, String]): GenericAdder2 = {
	  
	  class GenericBufferedAdder2(HardwareConfig : Map[String, String]) 
		extends GenericAdder2(HardwareConfig){
	    
		
	    val adder_core =  Module(create_general(HardwareConfig))
	    
		val bufA = RegInit(0.U(prec1.W))
		val bufB = RegInit(0.U(prec2.W))

		
		val bufValid = RegInit(0.U(1.W))
		//io.entry.ready := adder_core.io.entry.ready 
		
		
					adder_core.io.A := bufA
					adder_core.io.B := bufB
					
		when(io.entry.ready & io.entry.valid){
			bufA := io.A
			bufB := io.B
			
		    bufValid := 1.U
		}  .otherwise {
			bufValid := 0.U
		}
		
		io.Sum := adder_core.io.Sum
		io.Cout := adder_core.io.Cout
		io.exit.valid := bufValid & adder_core.io.exit.valid
		adder_core.io.Cin := io.Cin
		adder_core.io.entry <> io.entry
		adder_core.io.exit.ready := io.exit.ready
		io.entry.ready := adder_core.io.entry.ready
		adder_core.io.entry.valid := io.entry.valid 
		
	  }
	  
	  new GenericBufferedAdder2(HardwareConfig)
	  
  }
  
  
  
  
  
}

object AdderNFactory{
  def create( HardwareConfig : Map[String, String] ): GenericAdderN = {
	  
	  val adderNType = HardwareConfig("adderNType")
	  adderNType match {
	    case "SimpleAdderN" => new SimpleAdderN(HardwareConfig)
	    case "AddTreeN" => new AddTreeN(HardwareConfig)
	  	// case "Accumulator1" => new Accumulator1( HardwareConfig )
	  	//case "AdderCSA_Dadda" => None
	  	//case "AdderCSA_Wallace" => None
	  	//case "AdderCSA_4_2" => None
	    case _     => throw new IllegalArgumentException("Unknown adderN type " + adderNType)
	  }
  } 

	//create buffered version ... (this is for improvement of power purposes)
  	
  
}



class GenericAdderN(  HardwareConfig : Map[String, String] ) extends Module {
  
	val prec_in = HardwareConfig("prec_in").toInt
	val adderType = HardwareConfig("adderType")
	val terms = HardwareConfig("terms").toInt
	val pipelined  = HardwareConfig("pipelined").toBoolean
	val buffered = HardwareConfig("buffered").toBoolean

	val prec_sum = HardwareConfig("prec_sum").toInt // prec_in + log2Ceil(terms)

  val io = IO(new Bundle {
    val A = Input (Vec(terms, UInt (prec_in.W) ) )
    val Sum  = Output(UInt(prec_sum.W))
	
	val entry = new EntryIO()
	val exit = new ExitIO()

  })
  
}
