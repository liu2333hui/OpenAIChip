// // See LICENSE.txt for license details.
package adders

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


class AdderNSpec(c: GenericAdderN, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

	poke(c.io.entry.valid,0)
	poke(c.io.exit.ready,0)
        val cc = c	
	//val a: Array[Int] = TestVector("in_0")
	//val b: Array[Int] = TestVector("in_1")
	//val a_len = a.length
	//val b_len = b.length
	//val gab = BigInt(a_len).gcd(BigInt(b.length)).toInt

	for (i <- 0 until N) {	
		
		for (s <- 0 until TestVector("in_0").length ){
			
			//Trigger
			poke(c.io.entry.valid,1)
			poke(c.io.exit.ready,1)
			while(peek(c.io.entry.ready) == 0){
				step(D)
			}
		
			//Set Data
                        for (k <- 0 until cc.terms){
                                val kk = k //% 2
         			poke(   c.io.A(k) , TestVector(s"in_$kk"  )(s  ) )
                        }
			//poke(c.io.A, a(s % a_len)   )
			//poke(c.io.B, b(s % b_len)   )
		
			//step(D)
			do{
				step(D)
				//poke(c.io.entry.valid,0)		
			} while ( peek(c.io.exit.valid) == 0 )
			
                        var sum = 0
                        for (k <- 0 until cc.terms){
                                val kk = k // % 2
 
                            sum = sum + TestVector(s"in_$kk")(s)
                        }
			expect(c.io.Sum,   sum )	
			
		}
	}
    //println("TESTING Multiplier Complete\t"+ a(a.length-1)+"\t"+ b(b.length-1)+"\t")

}

object AdderNSpecFromFile extends App{ 

		print(args(args.length-1))

		val jsonString = Source.fromFile(args(args.length - 1)).mkString
		print(jsonString)		
		
		//sys.exit(0)	

		// 解析 JSON
		val parsed = Json.parse(jsonString)

		
		//sys.exit(0)	
		// Testing Params
		val N = 10
		val EDAVerification = parsed("EDAVerification").as[Boolean]
	
		val ModuleName = "AdderN"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation =false //true// false
		val ForceSynthesis = false
		
		// Hardware Params

                                   		val HardwareMap = Map(
          ("prec_in", Array( parsed("prec_in").as[Int] )),
	  ("prec_sum", Array(  parsed("prec_sum").as[Int]  )),
          ("adderNType", Array( parsed("adderNType").as[String] )), //AddTreeN
          ("adderType", Array( parsed("adderType").as[String]     )),
          ("terms", Array(  parsed("terms").as[Int]  )),
          ("signed", Array(false)),
          ("same_prec", Array(true)),
          ("pipelined", Array(false)),
          ("buffered", Array(false)),
          ("auto_prec_sum", Array(true)), 
	  ("tech",Array( parsed("tech").as[String]))
		)
		/* 
          val HardwareMap = Map(
         	 ("prec_in", Array( parsed("prec_in").as[Int]  )),
		  ("prec_sum", parsed("prec_sum").as[Int] ),
          ("adderNType", Array( parsed("adderType").as[String] )), //AddTreeN
          ("adderType", Array( "RCAAdder2"  )),//(todos)
          ("terms", Array(  parsed("terms").as[Int]  )),
          ("signed", Array(false)),
          ("same_prec", Array(true)),
          ("pipelined", Array(false)),
          ("buffered", Array(false)),
          ("auto_prec_sum", Array(true)), 
	("tech",Array(  parsed("tech").as[String] ))
		)
		*/
  
		var TestVectorMap = Map(
			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0))))	
	)


		for (i <- 1 until parsed("terms").as[Int] ){
			val key = s"in_$i"
			val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(i)))
			TestVectorMap = TestVectorMap + (key -> value)
		}


		/*
		val TestVectorMap  =  Map(
			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0)))),
			("in_1", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(1))))	
		) //Helper.processFileToMap(args(0), group=1 )
		*/	
	
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
							// val m = new SimpleAdder2(this.HardwareConfig)
							val m = AdderNFactory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new AdderNSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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


object AdderNSpec extends App{ 
		// Testing Params
		val N = 500
		val EDAVerification = false//false // false //true// false
		val ModuleName = "AdderN"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation =false //true// false
		val ForceSynthesis = false
		
		// Hardware Params
		val prec = 16
		val terms = 16//128 // 32

                                   		val HardwareMap = Map(
          ("prec_in", Array(prec)),
		  ("prec_sum", Array( prec )),
          ("adderNType", Array( "SimpleAdderN","AddTreeN" )), //AddTreeN
          ("adderType", Array( "SimpleAdder2" ,"RCAAdder2")),
          ("terms", Array( terms     )),
          ("signed", Array(false)),
          ("same_prec", Array(true)),
          ("pipelined", Array(false)),
          ("buffered", Array(false)),
          ("auto_prec_sum", Array(true)), 
							  ("tech",Array( "tsmc40"))
		)
  
		// seq = [ (0, 0, 0, 0), (127, 192, 22, 312), (12, 231 , 1, 32) ]
		/* 
		var TestVectorMap = Map( ("in_0",Array(  Array(0,127,12,33,99)     )),
					 ("in_1",Array(  Array(0,192,231,22,88)    )),
					 ("in_2",Array(  Array(0,22 ,1,33,77)       )),
					 ("in_3",Array(  Array(0,99,32,22,55)     )),
					 ("in_4",Array(  Array(0,9,8,3)      )),
					 ("in_5",Array(  Array(0,9,8,3)      )),
					 ("in_6",Array(  Array(0,9,8,3)      )),
					 ("in_7",Array(  Array(0,9,8,3)      )),		
		 )
		var TestVectorMap2 = Map( ("in_0",Array(  Array(0,127)     )),
					 ("in_1",Array(  Array(0,127)    )),
					 ("in_2",Array(  Array(0,127 )       )),
					 ("in_3",Array(  Array(0,127)     )),
		 )
        
                  
                 TestVectorMap = Map( ("in_0",Array(     Array(0,12,127)     )),
					 ("in_1",Array(  Array(0,231,192)    )),
					 ("in_2",Array(  Array(0,1,22)       )),
					 ("in_3",Array(  Array(0,32,99)     )),
					 ("in_4",Array(  Array(0,9,8,3)      )),
					 ("in_5",Array(  Array(0,9,8,3)      )),
					 ("in_6",Array(  Array(0,9,8,3)      )),
					 ("in_7",Array(  Array(0,9,8,3)      )),		
		 )
		*/
          	var TestVectorMap = Map( ("in_0",Array(     Array(0,0,22)     )),
					 ("in_1",Array(  Array(0,32,0)    )),
					 ("in_2",Array(  Array(0,1,127)       )),
					 ("in_3",Array(  Array(0,32,99)     )),
					 ("in_4",Array(  Array(0,9,8,3)      )),
					 ("in_5",Array(  Array(0,9,8,3)      )),
					 ("in_6",Array(  Array(0,9,8,3)      )),
					 ("in_7",Array(  Array(0,9,8,3)      )),		
		 )
          	
		/*
	          TestVectorMap = Map( ("in_0",Array(  Array(0,0, 1)     )),
					 ("in_1",Array(  Array(0,0,3)    )),
					 ("in_2",Array(  Array(0,0,8)       )),
					 ("in_3",Array(  Array(0,88, 0)     )),
					 ("in_4",Array(  Array(0,9,8,3)      )),
					 ("in_5",Array(  Array(0,9,8,3)      )),
					 ("in_6",Array(  Array(0,9,8,3)      )),
					 ("in_7",Array(  Array(0,9,8,3)      )),		
		 )
          	*/	


		TestVectorMap = Helper.GenSimpleTrainingVectors(mode="bits", p=prec, dim=2)
		for (t <- 2 until terms){	
			TestVectorMap = TestVectorMap.updated(s"in_$t", TestVectorMap(s"in_${t % 2}"))
		}


		println(TestVectorMap("in_0").length)
		//sys.exit()
		// seq = [ (0, 0, 0, 0), (127, 192, 22, 99), (12, 231 , 1, 32) ]

		//val TestVectorMap:Map[String, Array[Array[Int]]] = Helper.GenSimpleTrainingVectors(mode="full", p=8, dim=2)

                //print(TestVectorMap)
                //sys.exit(0)	
		
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
							// val m = new SimpleAdder2(this.HardwareConfig)
							val m = AdderNFactory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new AdderNSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
