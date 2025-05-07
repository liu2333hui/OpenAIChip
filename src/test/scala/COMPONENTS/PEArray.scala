
// // See LICENSE.txt for license details.
package components

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import eda._
import tester.{Helper, TechNode, FullTester}
import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._


import play.api.libs.json._
import scala.io.Source

class SimplePEArraySpec(c: SimplePEArray, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

	poke(c.io.entry.valid,0)
	poke(c.io.exit.ready,0)
	
	val a: Array[Int] = TestVector("in_0")
	val b: Array[Int] = TestVector("in_1")
	val a_len = a.length
	val b_len = b.length
	val gab = BigInt(a_len).gcd(BigInt(b.length)).toInt

	for (i <- 0 until N) {	
		
		for (s <- 0 until a.length * b.length / gab ){
			
			//Trigger
			poke(c.io.entry.valid,1)
			poke(c.io.exit.ready,1)
			while(peek(c.io.entry.ready) == 0){
				step(D)
			}
		
			//Set Data
			for (n <- 0 until c.number){
			poke(c.io.in0(n), a(s % a_len)   )
			poke(c.io.in1(n), b(s % b_len)   )
			}
		
			//step(D)
			do{
				step(D)
				//poke(c.io.entry.valid,0)		
			} while ( peek(c.io.exit.valid) == 0 )
			
			for( n <- 0 until c.number){
			expect(c.io.Out(n),a(s % a_len) * b(s % b_len ))
			}
			
			
		}
	}
    println("TESTING Multiplier Complete\t"+ a(a.length-1)+"\t"+ b(b.length-1)+"\t")

}

object SimplePEArraySpec extends App{ 
		// Testing Params

		val N = 200
		val EDAVerification = true

		val ModuleName = "SimplePEArray"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation =false //true// false
		val ForceSynthesis = false
		
		// Hardware Params
		val HardwareMap = Map(("prec2",Array(8)),
					("prec1",Array(8)),
					("prec_out", Array(16) ),
					 ("auto_prec_out", Array(true)),
					  ("radix"   , Array(256)), //2,4,8
				   //("multiplierType",Array("SimpleMultiplier2")),
					 ("multiplierType", Array("HighRadixMultiplier")),
					  ("side", Array("A", "B", "dual" )),//"A", "B", "dual"
					//  ("multiplierType", Array("BitSerialMultiplier")),
					  ("buffered",Array(false)),
						  ("signed", Array(false)),  
					  ("adderType",Array("SimpleAdder2")),
					  ("tech",Array( "tsmc40")),//asap7")),

					("number", Array( 1) )
		)
		
		var TestVectorMap = Map(("in_0",Array(   Array(123, 1, 41, 4 )   )),
		 		         ("in_1",Array(  Array(11, 22, 3,  123)   )) )

		TestVectorMap = Map(("in_0",Array(   Array(18 ), Array(158)   )),
		 		         ("in_1",Array(  Array(38), Array(27)   )) )

		//TestVectorMap = Map(("in_0",Array(       Array(233 )   )),
		//	 		         ("in_1",Array(  Array(1)   )) )
	
		TestVectorMap = Helper.GenSimpleTrainingVectors(mode="bits_no_zero", p=8, dim=2)
		//estVectorMap = Helper.GenSimpleTrainingVectors(mode="bits", p=8, dim=2)

		//TestVectorMap = Helper.GenSimpleTrainingVectors(mode="bits", p=8, dim=2, ZeroRepeat = 2)

		


		// 0, 123, 0, 1231
		// 0, 		
	
		
		 for (i <-TestVectorMap.keys){
		 	for (k <- TestVectorMap(i)){
		 		 print( i+",")
		 		for(v <- k){
		 			print(v+",")
		 		}
		 		println()
		 	}
		 }
		val RuntimeMap = Map(("CLOCK", Array(1 )),
							 ("cap_load", Array(1.00 )),//1.0)),//,0.010, 0.10, 1.0) ),
							 ("fanout_load", Array(0.100 ))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							val m = new SimplePEArray(this.HardwareConfig)
							//val m = Multiplier2Factory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new SimplePEArraySpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
