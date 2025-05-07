// // See LICENSE.txt for license details.
package adders

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import eda._
import tester.{Helper, TechNode, FullTester}
import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._


class Adder2Spec(c: GenericAdder2, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

	poke(c.io.entry.valid,0)
	poke(c.io.exit.ready,0)
	poke(c.io.Cin, 0)
	
	val a: Array[Int] = TestVector("in_a")
	val b: Array[Int] = TestVector("in_b")
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
			poke(c.io.A, a(s % a_len)   )
			poke(c.io.B, b(s % b_len)   )
		
			do{
				step(D)
				//poke(c.io.entry.valid,0)		
			} while ( peek(c.io.exit.valid) == 0 )
			
			expect(c.io.Sum,a(s % a_len) + b(s % b_len ))
			
			
		}
	}
    // println("TESTING AddN Complete\t"+ a(1)+"\t"+ b(1)+"\t"+ c)

}

object Adder2Spec extends App{ 
		// Testing Params
		val N = 500
		val EDAVerification = false
		val ModuleName = "Adder2"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation = false
		val ForceSynthesis = false
		
		// Hardware Params
		val prec = 16
		val HardwareMap = Map(("prec_sum",Array(prec)),
							  ("prec1",Array(prec)),
							  ("same_prec",Array(true)),
							  ("buffered",Array(false)),
							  ("adderType",Array("RCAAdder2")),
							  ("signed", Array(false)),
							  ("tech",Array("tsmc40"))
		)
		
		val TestVectorMap = Map(("in_a",Array(  Array(0,8), Array(0,3), Array(0,5) )),
							  ("in_b",Array(    Array(0,8), Array(0,3), Array(0,5) ))
		)
		
		val RuntimeMap = Map(("CLOCK", Array(1)),
							 ("cap_load", Array(0.10)),
							 ("fanout_load", Array(0.0))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							// val m = new SimpleAdder2(this.HardwareConfig)
							val m = Adder2Factory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new Adder2Spec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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



// class SimpleAdd2Spec(c: SimpleAdd2, a: Int, b: Int ) extends PeekPokeTester(c) {
//   //for (i <- 0 until 10) {
//     //val in0 = rnd.nextInt(1 << c.w)
//    // val in1 = rnd.nextInt(1 << c.w)
//     poke(c.io.A, a)
//     poke(c.io.B, b)
//     step(1)
//     println("TESTING AB" + c.io.Sum)
//   //expect(c.io.Sum,a+b)
//   //}
//    for (i <- 0 until 100){
//    step(1)
//   }
// }
	
// class SimpleAdd2Tester extends ChiselFlatSpec {
//   behavior of "SimpleAdd2"
//   backends foreach {backend =>
//     it should s"correctly add numbers in $backend" in {
//       Driver.execute(  Array("--generate-vcd-output" , "on", 
// 		          "--top-name", "SimpleAdd2Spec",
// 		           "--target-dir", "generated/SimpleAdd2"),  () => new SimpleAdd2(16, 0))(c => new SimpleAdd2Spec(c, 8, 8)) should be (true)
//     }
//   }



   
// }
