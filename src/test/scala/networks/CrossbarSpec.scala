package networks

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import sys.process._

import eda._
import tester.{Helper, TechNode, FullTester}

import scala.reflect.runtime.universe._

import play.api.libs.json._
import scala.io.Source

import play.api.libs.json._





class CrossbarCalibrationTester extends FullTester{
	override def driver() = {
		
		class CrossbarSelectSpec(cc: Crossbar,
		    TestVector : Map[String, Array[Int]] ,
		    N: Int = 500,
			D: Int = 1 ) extends PeekPokeTester(cc) {
				
			val c = cc
				
			  
			var sel = 0
			for (i <- 0 until N) {
		
				for (s <- 0 until TestVector("in_0").length ){	

				//Sel		
				for (t <- 0 until cc.out_terms) {
					sel = TestVector(s"sel_$t")(s)
					poke(c.io.sel(t) , TestVector(s"sel_$t")(s))
				}

				//Input Data	
				for (t <- 0 until cc.in_terms){
					val kk = t //+ 1
					poke(c.io.in(t) , TestVector(s"in_$kk")(s))
				}	
				step(D)	
				for (t <- 0 until cc.out_terms){
				val act_sel = TestVector(s"sel_$t")(s)
				//println(s + "\t"+ TestVector(s"in_$act_sel")+"\t"+ sel)
				expect(c.io.out(t), TestVector(s"in_$act_sel")( s ) )
				}
				
			}
		}//end test loop
				
	}//endclass
		
		
			Driver.execute(  Array("--generate-vcd-output" , "on",
			  "--top-name", this.SpecName,
			   "--target-dir", this.TargetDir), 
			   () => {
					val m = new Crossbar(this.HardwareConfig)
					( m  ) 
			   })( c => {
				    val mspec = new CrossbarSelectSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
			   	    ( mspec )  
				} ) 

	}
	
}

object CrossbarSpecFromFile extends App{ 

	val jsonString = Source.fromFile(args(args.length - 1)).mkString

	
	// 解析 JSON
	val parsed = Json.parse(jsonString)
	

		// Testing Params
		val N = 10
		//val EDAVerification = true
		val EDAVerification = parsed("EDAVerification").as[Boolean]

		val ModuleName = "Crossbar"//Match class names
		
		// Hardware Params
		//val prec = 16
		//val skip = 1

		//val terms = Array(8)

		val HardwareMap = Map(
		("in_terms",Array( parsed("in_terms").as[Int]  )   ),
		("out_terms", Array( parsed("out_terms").as[Int] ) ),//2
		("prec",Array( parsed("prec").as[Int] )   ),
		("type", Array( parsed("type").as[String]) ),

							  ("tech",Array( parsed("tech").as[String] ))
		)

		//val max_terms =  terms.max
		
 		var TestVectorMap = Map(
			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0))))	
	)
		for (i <- 1 until parsed("in_terms").as[Int] ){
			val key = s"in_$i"
			val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(i)))
			TestVectorMap = TestVectorMap + (key -> value)
		}

		for (i <- 0 until parsed("out_terms").as[Int] ){
			val key = s"sel_${i}"
			val idx = i + parsed("in_terms").as[Int]
			val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(idx)))
			TestVectorMap = TestVectorMap + (key -> value)
		}





		val RuntimeMap = Map(("CLOCK", Array(parsed("CLOCK").as[Int] )),
				     ("cap_load", Array(parsed("cap_load").as[Double] )),//1.0)),//,0.010, 0.10, 1.0) ),
				     ("fanout_load", Array(parsed("fanout_load").as[Double] ))
		)
	
	
		
		
		val m = new CrossbarCalibrationTester()
		m.run(HardwareMap,
				RuntimeMap, 
				TestVectorMap,
				N,
				ModuleName=ModuleName,
				TestName="TrainSelect",
				SpecName=s"${ModuleName}SelectSpec",
				EDAVerification = EDAVerification,
				SkipSimulation = false,
				ForceSynthesis = false,
				OutputPowerFile = parsed("OutputPowerFile").as[String],
	DontSaveInput = true
)
//inputs can be huge


}

object CrossbarSpec extends App{ 
		// Testing Params
		val N = 500
		val EDAVerification = true
		val ModuleName = "Crossbar"//Match class names
		
		// Hardware Params
		val prec = 16
		val skip = 1

		val terms = Array(8)
		val HardwareMap = Map(("in_terms",Array( 4 )   ),
					("out_terms", Array(2) ),//2
			         	("prec",Array(prec)),
					 ("tech",Array("tsmc40")),
		)
		val max_terms =  terms.max
		

		var TestVectorMap = Map(
					("sel_0", Array( Array(0,1,1)  ) ),//0,1,1 : 0,1,0
					("sel_1", Array(  Array(0,1,0)  ) ),

					 ("in_0",Array( Array(0,3,5)    )),
					 ("in_1",  Array( Array(0,32,0) )),
					 ("in_2",  Array( Array(0,1,127) )),
					 ("in_3",  Array( Array(0,32,99)  )),
					 ("in_4",  Array( Array(0,32,0) )),

					 ("in_5",  Array( Array(0,1,127)  )),
					 ("in_6",  Array( Array(0,32,0) )),
					 ("in_7",  Array( Array(0,32,0)   )),
					 ("in_8",  Array( Array(0,32,0) )),
		)
	

		val RuntimeMap = Map(("CLOCK", Array(1)),
				     ("cap_load", Array(1.00)),
			    	     ("fanout_load", Array(0.0))
		)
		
		
		val m = new CrossbarCalibrationTester()
		m.run(HardwareMap,
				RuntimeMap, 
				TestVectorMap,
				N,
				ModuleName=ModuleName,
				TestName="TrainSelect",
				SpecName=s"${ModuleName}SelectSpec",
				EDAVerification = EDAVerification,
				SkipSimulation = false,
				ForceSynthesis = false)

}
