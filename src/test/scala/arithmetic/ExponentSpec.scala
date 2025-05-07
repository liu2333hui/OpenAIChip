/*
package exponent
=======
// package exponent

// import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

// import eda._
// import tester.{Helper, TechNode, FullTester}
// import chisel3._
// import chisel3.util._
// import scala.collection.mutable.Queue
// import helper._

// class ExponentSpec(c: MaxN, 
//     TestVector : Map[String, Array[Int]] ,
//     N: Int = 500,
// 	D: Int = 1 ) extends PeekPokeTester(c) {

//     val cc = c
// 	for (i <- 0 until N) {	
// 		for (s <- 0 until TestVector("in_0").length ){
		
// 			//Set Data
// 			for (k <- 0 until 1){
//                 val kk = k 
// 				poke(   c.io.in(k) , TestVector(s"in_$kk"  )(s  ) )
// 			}
// 			step(D)          
// 			// expect(c.io.out,    )	
//             println("In: " + c.io.in.peek() + "\tOut:"+c.io.out.peek())
// 		}
// 	}
// }

// object ExponentSpec extends App{ 
// 		// Testing Params
// 		val N = 500
// 		val EDAVerification = false//false//false // false //true// false
// 		val ModuleName = "Exponent"//Match class names
// 		val SpecName = s"${ModuleName}Spec"//Match class names
// 		val   TestName = "Train"
		
// 		val SkipSimulation = false //true// false
// 		val ForceSynthesis = false
		
// 		// Hardware Params
// 		val prec = 8
// 	    val HardwareMap = Map(
//             ("in_prec", Array(prec)),
//             ("out_prec", Array(prec)),
//         	("tech",Array( "tsmc40"))
// 		)
  
// 		val TestVectorMap:Map[String, Array[Array[Int]]] = Helper.GenSimpleTrainingVectors(mode="bits", p=prec, dim=terms, skip = 2)
		
// 		val RuntimeMap = Map(("CLOCK", Array(1 )),
// 							 ("cap_load", Array(0.100 )),
// 							 ("fanout_load", Array(0.100 ))
// 		)
		
		
// 		class Tester extends FullTester{
// 			override def driver() = {
// 					Driver.execute(  Array("--generate-vcd-output" , "on",
// 					  "--top-name", this.SpecName,
// 					   "--target-dir", this.TargetDir), 
// 					   () => {
// 							val m = new ExponentLUT(this.HardwareConfig)
// 							( m  ) 
// 					   })( c => {
// 						    val mspec = new ExponentSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
// 					   	    ( mspec )    
// 						} ) 
// 			}
// 		}
		
// 		val m = new Tester()
// 		m.run(HardwareMap,
// 				RuntimeMap, 
// 				TestVectorMap,
// 				N,
// 				ModuleName=ModuleName,
// 				TestName=TestName,
// 				SpecName=SpecName,
// 				EDAVerification = EDAVerification,
// 				SkipSimulation = SkipSimulation,
// 				ForceSynthesis = ForceSynthesis)
// 		println("done")

<<<<<<< HEAD
}
*/
