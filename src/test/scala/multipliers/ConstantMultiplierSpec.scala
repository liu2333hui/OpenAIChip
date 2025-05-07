// // See LICENSE.txt for license details.
package multipliers

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import eda._
import tester.{Helper, TechNode, FullTester}
import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._


import play.api.libs.json._
import scala.io.Source

class ConstantMultiplierSpec(c: ConstantMultiplier, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

	poke(c.io.entry.valid,0)
	poke(c.io.exit.ready,0)
	
	val a: Array[Int] = TestVector("in_0")
	val a_len = a.length

	for (i <- 0 until N) {	
		
		for (s <- 0 until a.length ){
			
			//Trigger
			poke(c.io.entry.valid,1)
			poke(c.io.exit.ready,1)
			while(peek(c.io.entry.ready) == 0){
				step(D)
			}
		
			//Set Data
			poke(c.io.A, a(s % a_len)   )
		
			//step(D)
			do{
				step(D)
				//poke(c.io.entry.valid,0)		
			} while ( peek(c.io.exit.valid) == 0 )
			
			expect(c.io.Out,a(s % a_len) * c.constant)
			
			
		}
	}
    // println("TESTING Multiplier Complete\t"+ a(a.length-1)+"\t"+ b(b.length-1)+"\t")

}

object ConstantMultiplier2SpecFromFile extends App{ 


		val jsonString = Source.fromFile(args(2)).mkString
		
		// 解析 JSON
		val parsed = Json.parse(jsonString)
		
		

		// Testing Params
		val N = 10
		val EDAVerification = parsed("EDAVerification").as[Boolean]
		val ModuleName = "ConstantMultiplier"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation = false //true// false
		val ForceSynthesis = false
		
		// Hardware Params
		val HardwareMap = Map(
							  ("prec1",Array(parsed("prec1").as[Int] )),
							  ("auto_prec_out", Array(true)),
							  ("signed", Array(false)),  
                              
                              ("constant", Array(1)),//Array(parsed("constant").as[Int])),
							  ("tech",Array( parsed("tech").as[String] ))//asap7"))
		)
		
		// val TestVectorMap = Map(("in_0",Array(  Array(127) ,   Array(0, 127)   )),
		//  		         ("in_1",Array(  Array(127) ,   Array(0, 127)   ))
		//  )
		
		 // val TestVectorMap  = Helper.processFileToMap(args(0) , group=2)
		val TestVectorMap  =  Map(
			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0)))),
			("in_1", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(1)))),

		) 

		//Helper.processFileToMap(args(0), group=1 )
		
		
		// for(i <- TestVectorMap("in_0")){
		// 	print(i+",")
		// }
		// println()
		// for(i <- TestVectorMap("in_1")){
		// 	print(i+",")
		// }
		// println()
		
		val RuntimeMap = Map(("CLOCK", Array(parsed("CLOCK").as[Int] )),
							 ("cap_load", Array(parsed("cap_load").as[Double] )),//1.0)),//,0.010, 0.10, 1.0) ),
							 ("fanout_load", Array(parsed("fanout_load").as[Double] ))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							val m = new ConstantMultiplier(this.HardwareConfig)
							// val m = Multiplier2Factory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new ConstantMultiplierSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
					   	    ( mspec )    
						} ) 
			}
		}
		
		val m = new Tester()
		val CustomMap = parsed("DynamicHardwareMap").as[Map[String, String]]
		//#Map[String,String]()
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
			DontSaveInput = true,
			CustomMap = CustomMap + ("in_1"  -> "constant"  )	
)
		println("done")

}


object ConstantMultiplierSpec extends App{ 
		// Testing Params
        for (prec <- Array(8, 16)){
        for (constant <- 256 until 1 by -4){
		val N = 200
		val EDAVerification = true

		val ModuleName = "ConstantMultiplier"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation =false //true// false
		val ForceSynthesis = false
		
		// Hardware Params
		val HardwareMap = Map(
							  ("prec1",Array(prec)),
							  ("auto_prec_out", Array(true)),
							  ("signed", Array(false)),  
                              ("constant", Array(constant)),
							  ("tech",Array( "tsmc40"))//asap7"))
		)
		
		var TestVectorMap = Map(("in_0",Array(   Array(123, 1, 41, 4 )   )),
		 		         ("in_1",Array(  Array(11, 22, 3,  123)   )) )

		//TestVectorMap = Map(("in_0",Array(       Array(233 )   )),
		//	 		         ("in_1",Array(  Array(1)   )) )
	
		TestVectorMap = Helper.GenSimpleTrainingVectors(mode="full", p=prec, dim=1)
		
		// for (i <-TestVectorMap.keys){
		// 	for (k <- TestVectorMap(i)){
		// 		 print( i+",")
		// 		for(v <- k){
		// 			print(v+",")
		// 		}
		// 		println()
		// 	}
		// }
		
		val RuntimeMap = Map(("CLOCK", Array(1 )),
							 ("cap_load", Array(0.100 )),//1.0)),//,0.010, 0.10, 1.0) ),
							 ("fanout_load", Array(0.100 ))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							val m = new ConstantMultiplier(this.HardwareConfig)
							// val m = Multiplier2Factory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new ConstantMultiplierSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
        }}
}
