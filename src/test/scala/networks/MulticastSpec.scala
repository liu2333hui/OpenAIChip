package networks

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import sys.process._

import eda._
import tester.{Helper, TechNode, FullTester}

import scala.reflect.runtime.universe._


import play.api.libs.json._
import scala.io.Source

import play.api.libs.json._



class MulticastSpec(cc: Multicast, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(cc) {
		
	val c = cc
		
	val a: Array[Int] = TestVector("in_0")
	
	for ( i <- 0 until N ) {

            for (s <- 0 until a.length) {


		//
		poke(c.io.en, 1)
		for (t <- 0 until c.terms){
			val kk = t
                      poke(c.io.in(t), TestVector(s"in_$kk")(s))
		}

		
		step(D)
		
		for (t <- 0 until c.terms){
			for (f <- 0 until c.fanout){
				val kk = t  
			    expect(c.io.out(t)(f), TestVector(s"in_$kk")(s))

			}
		}

            }
	
	}


}



class MulticastCalibrationTester extends FullTester{
	
	// HardwareConfig: Map[String,String],
		// TestVector : Map[String, Array[Int]], N : Int, CLOCK: Int, ModuleNameSpecName:String
	override def driver() = {
			

			// 	Driver.execute(  Array("--generate-vcd-output" , "on", 
			// 				  "--top-name", "SimpleAddNSpec",
			// 				   "--target-dir", s"generated/${module_out_name}"),  () 
			// 				   => (new AddTreeN(terms,prec_in,adderType,buffered=buffered)).asInstanceOf[GenericAdderN])(c => {
			
			
			// new SimpleAddNSpec(c.asInstanceOf[GenericAdderN], Array.fill(terms)(zhi1), Array.fill(terms)(zhi), 
			// N=N, D = CLOCK )})
			

			// println(this.N, this.CLOCK)
			// val m = new Multicast(this.HardwareConfig)
			
			
			
			Driver.execute(  Array("--generate-vcd-output" , "on",
			  "--top-name", this.SpecName,
			   "--target-dir", this.TargetDir), 
			   () => {
				   
				   // val mirror = runtimeMirror(getClass.getClassLoader)
				   // val classSymbol = mirror.staticClass("networks.Multicast")
				   // val classMirror = mirror.reflectClass(classSymbolsss)
				   
				   
					val m = new Multicast(this.HardwareConfig)
					( m  ) 
			   })( c => {
				    val mspec = new MulticastSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
			   	    ( mspec )  
					  
				} ) 

	}
	
}



object MulticastSpecFromFile extends App{ 
	
	//val jsonString = Source.fromFile(args(1)).mkString
	val jsonString = Source.fromFile(args(args.length - 1)).mkString


	
	// 解析 JSON
	val parsed = Json.parse(jsonString)
	
	
		// Testing Params
		val N = 100
		val EDAVerification = parsed("EDAVerification").as[Boolean]
		val ModuleName = "Multicast"//Match class names
		val SpecName = "MulticastSpec"//Match class names
		val   TestName = "Train"
		
		// Hardware Params
		val HardwareMap = Map(("terms",Array( parsed("terms").as[Int] )),
				("fanout",Array( parsed("fanout").as[Int] )),
				  ("prec",Array( parsed("prec").as[Int] )),
				  ("buffered",Array(true)),
			  ("tech",Array( parsed("tech").as[String] ))//tsmc40"))
		)
		
 		var TestVectorMap = Map(
			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0))))	
	)
		for (i <- 1 until parsed("terms").as[Int] ){
			val key = s"in_$i"
			val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(i)))
			TestVectorMap = TestVectorMap + (key -> value)
		}


		
		println("LOADED"+ TestVectorMap("in_0").length + "\t" + TestVectorMap("in_0")(0).length)
		
		val RuntimeMap = Map(("CLOCK", Array(parsed("CLOCK").as[Int] )),
							 ("cap_load", Array(parsed("cap_load").as[Double] )),//1.0)),//,0.010, 0.10, 1.0) ),
							 ("fanout_load", Array(parsed("fanout_load").as[Double] ))
		)
		
		val m = new MulticastCalibrationTester()
		m.run(HardwareMap,
				RuntimeMap, 
				TestVectorMap,
				N,
				ModuleName=ModuleName,
				TestName=TestName,
				SpecName=SpecName,
				EDAVerification = EDAVerification,
				SkipSimulation = false,
				ForceSynthesis = false,
				OutputPowerFile = parsed("OutputPowerFile").as[String],
DontSaveInput = true
)
}



object MulticastSpec extends App{ 
		// Testing Params
		val N = 50
		val EDAVerification =true
		val ModuleName = "Multicast"//Match class names
		val SpecName = "MulticastSpec"//Match class names
		val   TestName = "Train2"
		
		
		// Hardware Params
		val HardwareMap = Map(("terms",Array(1)),
							  ("fanout",Array( 16 )),
							  ("prec",Array( 8 )),
							  ("buffered",Array(true)),
							  ("tech",Array("tsmc40"))//tsmc40"))
		)
		
	//	val TestVectorMap = Map(("zhi1",Array(   Array(0), Array(0), Array(0) )),
//							  ("zhis",Array(   Array(0)  , Array(1), Array(3) ))
//		)

                val TestVectorMap:Map[String, Array[Array[Int]]] = Helper.GenSimpleTrainingVectors(mode="bits", p=8, dim=1)
 //               val TestVectorMap: Map[String, Array[Array[Int]]] = Map(("in_0", Array(
  //                 Array(0, 127, 192, 32, 39, 2, 2, 231  ))))
		
		
		val RuntimeMap = Map(("CLOCK", Array(1)),
							 ("cap_load", Array(1.0)),
							 ("fanout_load", Array(0.0))
		)
		
		val m = new MulticastCalibrationTester()
		m.run(HardwareMap,
				RuntimeMap, 
				TestVectorMap,
				N,
				ModuleName=ModuleName,
				TestName=TestName,
				SpecName=SpecName,
				EDAVerification = EDAVerification,
				SkipSimulation = false,
				ForceSynthesis = false)
		

}
