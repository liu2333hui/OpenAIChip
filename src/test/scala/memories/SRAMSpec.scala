// See LICENSE.txt for license details.
package memories


import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import eda._
import tester.{Helper, TechNode, FullTester}
import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._

import scala.util.Random

import play.api.libs.json._
import scala.io.Source


//import scala.util.control.Breaks._
import scala.math._

class SRAMSSpec(c: SRAMBankedASAP7, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {
	var global_cycles = 1;

	val write_data: Array[Int] = TestVector("write_data")
	val write_addr = TestVector("write_addr")
	val read_addr = TestVector("read_addr")
	var flag = false

	var ram_map = Map[Int, Int]()
	for (i <- 0 until write_addr.length){
		ram_map = ram_map + (write_addr(i) -> write_data(i)) 
	}

	for (i <- 0 until N) {	
		
		//RAW
		for (j <- 0 until math.min(512, write_data.length)){
			//Change for other technologies
			
			poke(c.io.write_address, write_addr(j % write_addr.length)   )
			poke(c.io.rw_mode, 0)
			poke(c.io.banksel, 1)
			poke(c.io.write_data  , write_data(j))
			
			step(D)
		}

		for (j <- 0 until math.min(512,read_addr.length)){
			//Change for other technologies
			
			poke(c.io.read_address, read_addr(j % read_addr.length)   )
			poke(c.io.rw_mode, 1)
			poke(c.io.banksel, 1)
			step(D)
			global_cycles  = global_cycles + 1
			if(global_cycles >= 88888){
				flag = true
				
			}
			if(flag){
				//break()
				//return
				
			}
			expect(c.io.read_data  , ram_map(read_addr(j)))
			
			
		}
			if(flag){
				//return
				//break()
			}
	
		
	}

    // println("TESTING AddN Complete\t"+ a(1)+"\t"+ b(1)+"\t"+ c)


}

object SRAMSSpecFromFile extends App{ 

 		//readFileTo2DArrayWithPadding

 		//val jsonString = Source.fromFile(args(1)).mkString
		
	val jsonString = Source.fromFile(args(args.length - 1)).mkString


 		// 解析 JSON
 		val parsed = Json.parse(jsonString)
		
 		// Testing Params
 		val N = 10

 		val EDAVerification = parsed("EDAVerification").as[Boolean]
 		val ModuleName = "SRAMBanked"//Match class names
 		val SpecName = s"${ModuleName}Spec"//Match class names
 		val   TestName = "Train"
		
 		val SkipSimulation = false
 		val ForceSynthesis = false
		
 		// Hardware Params
 		val HardwareMap = Map(
 			("entry_bits", Array( parsed("entry_bits").as[Int] )),//, 32, 64) ),
 			("rows",       Array( parsed("rows").as[Int])),
 			("sram_type", Array(  parsed("type").as[String] )),
 			("tech",    Array(parsed("tech").as[String] ))
 		)

		val RAW_DATA = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0)))


                val TESTS = RAW_DATA.length

               
		val READ = 0
		val WRITE = 1


	                var LEN = RAW_DATA(0).length //256	
			var ADDR = Array.range(0, LEN)
			var DATA = RAW_DATA
	                var WRITE_ADDR = RAW_DATA.map(subArray => (0 until subArray.length).toArray)
 	                 var READ_ADDR = Array.fill(TESTS)(Array[Int]())
        

		if(parsed("mode").as[Int] == READ){	

	                 LEN = RAW_DATA(0).length //256	
			 ADDR = Array.range(0, LEN)
			 DATA = RAW_DATA

//                 //val DATA =  generateAlternateData(LEN , TESTS)
//                 val DATA =  generateAlternateDataFull(LEN , TESTS)
//                 //println(DATA.length)
//                 //sys.exit()
           //      val WRITE_ADDR = Array.fill(TESTS)(ADDR)
	                 WRITE_ADDR = RAW_DATA.map(subArray => (0 until subArray.length).toArray)
 	
                  READ_ADDR = Array.fill(TESTS)(Array[Int]())
                
			} else {	
				
	                //val LEN = RAW_DATA(0).length //256	
			//val ADDR = Array.range(0, LEN)
			val repeat = 100
			DATA = RAW_DATA
	                WRITE_ADDR = RAW_DATA.map(subArray => (0 until subArray.length).toArray) //Array.fill(TESTS)(ADDR)
	                READ_ADDR = RAW_DATA.map(subArray =>Array.fill(repeat)( (0 until subArray.length).toArray).flatten  )
 	                //val READ_ADDR = Array.fill(TESTS)(Array.fill(repeat)(ADDR).flatten) 


//                 /*
//                 //READING
//                 val LEN = 256 //256
//                 val ADDR = Array.range(0, 2)
//                 val TESTS = 256
//                 val DATA =  generateAlternateDataFull(2 , TESTS)
//                 val WRITE_ADDR = Array.fill(TESTS)(ADDR)
//                 val READ_ADDR = Array.fill(TESTS)( createAlternatingArray(LEN, 1 ) )
// 		*/
		}

		
 		val TestVectorMap = Map(


                         ("write_data", DATA), 
 			("read_addr", READ_ADDR),
 			("write_addr", WRITE_ADDR)
			
		)

		
		
		val RuntimeMap = Map(("CLOCK", Array(parsed("CLOCK").as[Int] )),
							 ("cap_load", Array(parsed("cap_load").as[Double] )),//1.0)),//,0.010, 0.10, 1.0) ),
							 ("fanout_load", Array(parsed("fanout_load").as[Double] ))
		)
	
 		val RuntimeMap2 = Map(("CLOCK", Array(1)),
 							 ("cap_load", Array(0.100)),
 							 ("fanout_load", Array(0.0))
 		)
		
		
 		class Tester extends FullTester{
 			override def driver() = {
 					Driver.execute(  Array("--generate-vcd-output" , "on",
 					  "--top-name", this.SpecName,
 					   "--target-dir", this.TargetDir), 
 					   () => {
 							// val m = new SimpleAdder2(this.HardwareConfig)
 							// val m = new BankedSRAM(this.HardwareConfig)
 							val m = new SRAMBankedASAP7(this.HardwareConfig)
 							( m  ) 
 					   })( c => {
 						    val mspec = new SRAMSSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
 					   	    ( mspec )    
 						} ) 
 			}
 		}
		
 		val m = new Tester()
 		m.run(HardwareMap,
 				RuntimeMap, 
 				TestVectorMap,
 				N,
 				ModuleName=ModuleName,
 				TestName=TestName,
 				SpecName=SpecName,
 				EDAVerification = EDAVerification,
 				SkipSimulation = SkipSimulation,
 				ForceSynthesis = ForceSynthesis,
				OutputPowerFile = parsed("OutputPowerFile").as[String],
	DontSaveInput = true

	)
	
// 		println("done")

 }


object SRAMSSpec extends App{ 

def createAlternatingArray(length: Int, c: Int): Array[Int] = {
  Array.tabulate(length) { i =>
    if (i % 2 == 0) 0 else c
  }
}


def generateAlternateData(LEN: Int, N: Int): Array[Array[Int]] = {
  val range = 0 until N
  range.map { c =>
    createAlternatingArray(LEN, (1<<c)-1 )
  }.toArray
}

def generateAlternateDataFull(LEN: Int, N: Int): Array[Array[Int]] = {
  val range = 0 until N
  range.map { c =>
    createAlternatingArray(LEN, c )
  }.toArray
}




		// Testing Params
		val N = 200
		val EDAVerification = true
		val ModuleName = "SRAMBanked"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation = false
		val ForceSynthesis = false
		
		// Hardware Params
		val HardwareMap = Map(
			("entry_bits", Array( 16)),//, 32, 64) ),
			("rows",       Array( 256)),
			("sram_type", Array("typical")),
			("tech",    Array("tsmc40"))
		)

                //WRITING
              	/* 
                val LEN = 256 //256
                //val ADDR = Array.range(0, LEN)
                val ADDR = Array.range(0, LEN)
                val TESTS = 16//256//1<<16
                val DATA =  generateAlternateData(LEN , TESTS)
                //val DATA =  generateAlternateDataFull(LEN , TESTS)
                //println(DATA.length)
                //sys.exit()
                val WRITE_ADDR = Array.fill(TESTS)(ADDR)
                val READ_ADDR = Array.fill(TESTS)(Array[Int]())
                
		*/
                
                //READING
                val LEN = 256 //256
                val ADDR = Array.range(0, 2)
                val TESTS = 16//256
                //val DATA =  generateAlternateDataFull(2 , TESTS)
                val DATA =  generateAlternateData(2 , TESTS)
 
                val WRITE_ADDR = Array.fill(TESTS)(ADDR)
                val READ_ADDR = Array.fill(TESTS)( createAlternatingArray(LEN, 1 ) )
		


		
		val TestVectorMap = Map(


                        ("write_data", DATA), 
			("read_addr", READ_ADDR),
			("write_addr", WRITE_ADDR)
			


	//		("write_data",Array( Array.fill(LEN)(0) , Array.fill(LEN)(1)  ,  Array.fill(LEN)(3), Array.fill(LEN)(Random.nextInt(7)) , Array.fill(LEN)(15), Array.fill(LEN)(31)       )),
 
//Array(  createAlternatingArray(LEN, 0), createAlternatingArray(LEN, 1), createAlternatingArray(LEN, 3), createAlternatingArray(LEN, 7), createAlternatingArray(LEN,15), createAlternatingArray(LEN, 31)),  createAlternatingArray(LEN, 0), createAlternatingArray(LEN, 1), createAlternatingArray(LEN, 3), createAlternatingArray(LEN, 7), createAlternatingArray(LEN,15), createAlternatingArray(LEN, 31)))  ), 

		//	("write_addr", Array.fill(TESTS)(ADDR) ),

		//	("read_addr",Array( Array[Int](), Array[Int](), Array[Int](), Array[Int](), Array[Int](), Array[Int]() ))
		)
		
		val RuntimeMap = Map(("CLOCK", Array(1)),
							 ("cap_load", Array(0.100)),
							 ("fanout_load", Array(0.0))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							// val m = new SimpleAdder2(this.HardwareConfig)
							// val m = new BankedSRAM(this.HardwareConfig)
							val m = new SRAMBankedASAP7(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new SRAMSSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
					   	    ( mspec )    
						} ) 
			}
		}
		
		val m = new Tester()
		m.run(HardwareMap,
				RuntimeMap, 
				TestVectorMap,
				N,
				ModuleName=ModuleName,
				TestName=TestName,
				SpecName=SpecName,
				EDAVerification = EDAVerification,
				SkipSimulation = SkipSimulation,
				ForceSynthesis = ForceSynthesis)

		println("done")

}

// import sys.process._

// import eda._
// import tester.{Helper, TechNode, FullTester}

// import scala.reflect.runtime.universe._

// class ASAP7SramBankSpec(cc: Multicast, 
//     TestVector : Map[String, Array[Int]] ,
//     N: Int = 500,
// 	D: Int = 1 ) extends PeekPokeTester(cc) {
		
// 	val c = cc
		
// 	// for (z <- TestVector.keys){
// 	// 	print(z)
// 	// }
		
// 	  val a: Array[Int] = Array.fill(cc.terms)(TestVector("zhi1")(0))
// 	  val b: Array[Int] = Array.fill(cc.terms)(TestVector("zhis")(0))
// 	for (i <- 0 until N) {

// 		poke(c.io.en, 1)
// 		for (t <- 0 until c.terms){
// 			if(i % 2 == 0){
// 				poke(c.io.in(t) , a(t))
// 			}else{
// 				poke(c.io.in(t) , b(t))
// 			}
// 		}
		
// 		step(D)
		
// 		for (t <- 0 until c.terms){
// 			for (f <- 0 until c.fanout){
// 				if(i % 2 == 0)
// 					expect(c.io.out(t)(f), a(t))
// 				else
// 					expect(c.io.out(t)(f), b(t))
// 			}
// 		}
// 		// expect(c.io.Sum,a.reduce((x,y)=> x + y))
	
// 	}


// }



// class ASAP7SramBankTester extends FullTester{
	
// 	// HardwareConfig: Map[String,String],
// 		// TestVector : Map[String, Array[Int]], N : Int, CLOCK: Int, ModuleNameSpecName:String
// 	override def driver() = {

// 			Driver.execute(  Array("--generate-vcd-output" , "on",
// 			  "--top-name", this.SpecName,
// 			   "--target-dir", this.TargetDir), 
// 			   () => {
// 					val m = new Multicast(this.HardwareConfig)
// 					( m  ) 
// 			   })( c => {
// 				    val mspec = new MulticastSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
// 			   	    ( mspec )  
					  
// 				} ) 

// 	}
	
// }


// object MulticastTester extends App{ 
// 		// Testing Params
// 		val N = 500
// 		val EDAVerification = false
// 		val ModuleName = "Multicast"//Match class names
// 		val SpecName = "MulticastSpec"//Match class names
// 		val   TestName = "Train"
		
		
// 		// Hardware Params
// 		val HardwareMap = Map(("terms",Array(2,16)),
// 							  ("fanout",Array(2,32)),
// 							  ("prec",Array(8)),
// 							  ("buffered",Array(true)),
// 							  ("tech",Array("tsmc40"))
// 		)
		
// 		val TestVectorMap = Map(("address",Array( Array(0), Array(0), Array(0) )),
// 							  ("data",Array(   Array(0)  , Array(1), Array(3) )),
							  
// 		)
		
// 		val RuntimeMap = Map(("CLOCK", Array(1)),
// 							 ("cap_load", Array(0.010)),
// 							 ("fanout_load", Array(0.0))
// 		)
		
// 		val m = new ASAP7SramBankTester()
// 		m.run(HardwareMap,
// 				RuntimeMap, 
// 				TestVectorMap,
// 				N,
// 				ModuleName=ModuleName,
// 				TestName=TestName,
// 				SpecName=SpecName,
// 				EDAVerification = EDAVerification,
// 				SkipSimulation = false,
// 				ForceSynthesis = false)
		

// }
