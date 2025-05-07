// // See LICENSE.txt for license details.
package maxmin

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import eda._
import tester.{Helper, TechNode, FullTester}
import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._

import play.api.libs.json._
import scala.io.Source

import play.api.libs.json._



class MaxNSpec(c: MaxN, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

    val cc = c

	for (i <- 0 until N) {	
		for (s <- 0 until TestVector("in_0").length ){
		
			//Set Data
			for (k <- 0 until cc.terms){
					val kk = k 
				poke(   c.io.in(k) , TestVector(s"in_$kk"  )(s  ) )
			}

		
			step(D)
                       
			var max_val = 0
            for (k <- 0 until cc.terms){
                val kk = k
                if(TestVector(s"in_$kk")(s) > max_val){
					max_val = TestVector(s"in_$kk")(s)
				}
            }
			expect(c.io.out,   max_val )	
			
		}
	}

}

//Todos, for verification purposes
object MaxNSpecFromFile extends App{	
		val jsonString = Source.fromFile(args(args.length - 1)).mkString
		//print(jsonString)
		val parsed = Json.parse(jsonString)
		// Testing Params
		val N = 10
		val EDAVerification = parsed("EDAVerification").as[Boolean]
	
		print("hardwaremap\n")
 	
		val ModuleName = "MaxN"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation =false //true// false
		val ForceSynthesis = false
		
		// Hardware Params
	    val HardwareMap = Map(
            ("prec", Array( parsed("prec").as[Int]  )),
            ("terms", Array(   parsed("terms").as[Int]    )),
        	("tech",Array( parsed("tech").as[String] ))
		)

		print("hardwaremap\n")
 		var TestVectorMap = Map(
			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0))))	
	)
		for (i <- 1 until parsed("terms").as[Int] ){
			val key = s"in_$i"
			val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(i)))
			TestVectorMap = TestVectorMap + (key -> value)
		}

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
							val m = new MaxN(this.HardwareConfig)
							//val m = AdderNFactory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new MaxNSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
				OutputPowerFile = parsed("OutputPowerFile").as[String]
)
		println("done")

}

object MaxNSpec extends App{ 
		// Testing Params
		val N = 500
		val EDAVerification = true//false//false // false //true// false
		val ModuleName = "MaxN"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation = false //true// false
		val ForceSynthesis = false
		
		// Hardware Params
		val prec = 16
		val terms = 4
	    val HardwareMap = Map(
            ("prec", Array(prec)),
            ("terms", Array(terms)),
        	("tech",Array( "tsmc40"))
		)
  
		val TestVectorMap:Map[String, Array[Array[Int]]] = Helper.GenSimpleTrainingVectors(mode="bits", p=prec, dim=terms, skip = 2)
		
		val RuntimeMap = Map(("CLOCK", Array(1 )),
							 ("cap_load", Array(0.100 )),
							 ("fanout_load", Array(0.100 ))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							val m = new MaxN(this.HardwareConfig)
							//val m = AdderNFactory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new MaxNSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
