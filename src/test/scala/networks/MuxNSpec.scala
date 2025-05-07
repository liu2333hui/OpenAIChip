package networks

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import sys.process._

import eda._
import tester.{Helper, TechNode, FullTester}

import scala.reflect.runtime.universe._





class MuxNCalibrationTester extends FullTester{
	override def driver() = {
		
		class MultiplexerNSelectSpec(cc: MuxN,
		    TestVector : Map[String, Array[Int]] ,
		    N: Int = 500,
			D: Int = 1 ) extends PeekPokeTester(cc) {
				
			val c = cc
				
			  
			var sel = 0
			for (i <- 0 until N) {
		
				for (s <- 0 until TestVector("in_0").length ){	

				//Sel	
				val sel = TestVector(s"in_0")(s)
				poke(c.io.sel, sel  )

				//Input Data	
				for (t <- 0 until cc.terms){
					val kk = t + 1
					poke(c.io.in(t) , TestVector(s"in_$kk")(s))
				}	
				step(D)	
				val act_sel = sel + 1
				//println(s + "\t"+ TestVector(s"in_$act_sel")+"\t"+ sel)
				expect(c.io.out, TestVector(s"in_$act_sel")( s ) )
				
			}
		}//end test loop
				
	}//endclass
		
		
			Driver.execute(  Array("--generate-vcd-output" , "on",
			  "--top-name", this.SpecName,
			   "--target-dir", this.TargetDir), 
			   () => {
					val m = new MuxN(this.HardwareConfig)
					( m  ) 
			   })( c => {
				    val mspec = new MultiplexerNSelectSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
			   	    ( mspec )  
				} ) 

	}
	
}


object MuxNSpec extends App{ 

	for (term <-Array(4, 8, 16, 32, 64, 128, 256, 512)){
		// Testing Params
		val N = 100
		val EDAVerification = true
		val ModuleName = "MuxN"//Match class names
		
		// Hardware Params
		val prec = 8
		val skip = 1

		val terms = Array(term)
		val HardwareMap = Map(("terms",terms),
			         	("prec",Array(prec)),
					 ("tech",Array("tsmc40")),
		)
		val max_terms =  terms.max
		

		/*
		var TestVectorMap = Map(("in_0",Array( Array(0), Array(1), Array(1)    )),
					 ("in_1",  Array( Array(0), Array(0), Array(0)   )),
					 ("in_2",  Array( Array(1), Array(3), Array.range(0, 16) ))
		)
		*/


		//Test 1
		//Sel: 00000
		//In_1: 0  N 0 N 0 N 0 N
		//Sel stationary		
		var TestVectorMap1:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()	
		TestVectorMap1 = Helper.GenSimpleTrainingVectors(mode="bits", p=prec, dim=1, skip = skip)
		for(t <- 1 to max_terms){
			TestVectorMap1 = TestVectorMap1.updated(s"in_$t", TestVectorMap1("in_0"))		
		}	
		TestVectorMap1 = TestVectorMap1.updated("in_0", Array.fill(prec)(Array(0, 0)))
	
		//Test 2
		//Sel: 0 K 0 K 0 K
		//In_1: 0 0 0 0 0 0 0 0 0 0
		//In_2: N N N N N N N N N N
		//Data stationary
		var TestVectorMap2:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()	
		var in_0 = Array[Array[Int]]()
		var in_1 = Array[Array[Int]]() 
		var in_rest = Array[Array[Int]]()		
		for(k <- 0 until term){
			for (n <- 0 until prec){
				in_0 = Array.concat(in_0, Array( Array( 0, k) ) )
				in_1 = Array.concat(in_1, Array( Array( 0, 0) ) )
				in_rest = Array.concat(in_rest, Array( Array((1<<n) - 1, (1<<n) - 1)  ) )
			}
		}
		TestVectorMap2 = TestVectorMap2.updated("in_0", in_0)
		TestVectorMap2 = TestVectorMap2.updated("in_1", in_1) 
		for (t <- 2 to max_terms){
			TestVectorMap2 = TestVectorMap2.updated(s"in_$t", in_rest) 
		}

		//Test 3
		//Both changing
		//Sel: 
		//In_1:
		//In_2: 
		var TestVectorMap3:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()	
		in_0 = Array[Array[Int]]()
		in_rest = Array[Array[Int]]()		
		for(k <- 0 until term){
			for (n <- 0 until prec){
				in_0 = Array.concat(in_0, Array( Array( 0, k) ) )	
				in_rest = Array.concat(in_rest, Array(Array( 0, (1<<n) - 1)  )	)
			}
		}
		TestVectorMap3 = TestVectorMap3.updated("in_0", in_0)
		for (t <- 1 to max_terms){
			TestVectorMap3 = TestVectorMap3.updated(s"in_$t", in_rest) 
		}

	

		//Combine all three tests into one TestVectorMap

		
		var TestVectorMap:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()		
		for (t <- 0 to max_terms){
			TestVectorMap = TestVectorMap.updated(s"in_$t", 
				Array.concat(
					TestVectorMap1(s"in_$t" ),
					TestVectorMap2(s"in_$t" ),
					TestVectorMap3(s"in_$t" )
				 ) )
		}


		/*
		TestVectorMap = Map(("in_0",Array( Array(0,3,5)    )),
					 ("in_1",  Array( Array(0,32,0) )),
					 ("in_2",  Array( Array(0,1,127) )),
					 ("in_3",  Array( Array(0,32,99)  )),
					 ("in_4",  Array( Array(0,32,0) )),

					 ("in_5",  Array( Array(0,1,127)  )),
					 ("in_6",  Array( Array(0,32,0) )),
					 ("in_7",  Array( Array(0,32,0)   )),
					 ("in_8",  Array( Array(0,32,0) )),




		)
		*/	

		val RuntimeMap = Map(("CLOCK", Array(1)),
				     ("cap_load", Array(1.00)),
			    	     ("fanout_load", Array(0.0))
		)
		
		
		val m = new MuxNCalibrationTester()
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
}
