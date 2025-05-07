package networks

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import sys.process._

import eda._
import tester.{Helper, TechNode, FullTester}

import scala.reflect.runtime.universe._


import play.api.libs.json._
import scala.io.Source

import play.api.libs.json._



class Parallel2SerialSpec(cc: GenericParallel2Serial, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(cc) {
		
	val c = cc
		
    
	val a: Array[Int] = TestVector("in_0")
	

	for ( i <- 0 until N ) {

            for (s <- 0 until a.length) {

            //Trigger
			poke(c.io.entry.valid,1)
			poke(c.io.exit.ready,1)
            
		    poke(c.io.en, 1)
            for (t <- 0 until cc.terms){
                val kk = t 
                poke(c.io.in(t) , TestVector(s"in_$kk")(s))
            }	

            var no = 0
			do{
				
				step(D)

				//validate
                for (f <- 0 until c.fanout){
                    val kk = no  
					// print(peek(c.io.out(f) + "\n"))
					// print(TestVector(s"in_$kk")(s).toString + "\n")
                    expect(c.io.out(f), TestVector(s"in_$kk")(s))
                }


                no = no + 1;
                
        
			}while(peek(c.io.entry.ready) == 0)
		
        

		
			// //step(D)   
			// // do{
			// step(D)
			// 	//poke(c.io.entry.valid,0)		
			// } while ( peek(c.io.exit.valid) == 0 )
			


            }
	
	}


}



class Parallel2SerialSpecTester extends FullTester{
	
	// HardwareConfig: Map[String,String],
		// TestVector : Map[String, Array[Int]], N : Int, CLOCK: Int, ModuleNameSpecName:String
	override def driver() = {
			
			Driver.execute(  Array("--generate-vcd-output" , "on",
			  "--top-name", this.SpecName,
			   "--target-dir", this.TargetDir), 
			   () => {
                //    val m = Multiplier2Factory.create(this.HardwareConfig)

				   val m = Parallel2SerialFactory.create_general(this.HardwareConfig)
					// val m = new Parallel2Serial(this.HardwareConfig)
					( m  ) 
			   })( c => {
				    val mspec = new Parallel2SerialSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
			   	    ( mspec )  
					  
				} ) 

	}
	
}



// object MulticastSpecFromFile extends App{ 
	
// 	//val jsonString = Source.fromFile(args(1)).mkString
// 	val jsonString = Source.fromFile(args(args.length - 1)).mkString


	
// 	// 解析 JSON
// 	val parsed = Json.parse(jsonString)
	
	
// 		// Testing Params
// 		val N = 100
// 		val EDAVerification = parsed("EDAVerification").as[Boolean]
// 		val ModuleName = "Multicast"//Match class names
// 		val SpecName = "MulticastSpec"//Match class names
// 		val   TestName = "Train"
		
// 		// Hardware Params
// 		val HardwareMap = Map(("terms",Array( parsed("terms").as[Int] )),
// 				("fanout",Array( parsed("fanout").as[Int] )),
// 				  ("prec",Array( parsed("prec").as[Int] )),
// 				  ("buffered",Array(true)),
// 			  ("tech",Array( parsed("tech").as[String] ))//tsmc40"))
// 		)
		
//  		var TestVectorMap = Map(
// 			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0))))	
// 	)
// 		for (i <- 1 until parsed("terms").as[Int] ){
// 			val key = s"in_$i"
// 			val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(i)))
// 			TestVectorMap = TestVectorMap + (key -> value)
// 		}


		
// 		println("LOADED"+ TestVectorMap("in_0").length + "\t" + TestVectorMap("in_0")(0).length)
		
// 		val RuntimeMap = Map(("CLOCK", Array(parsed("CLOCK").as[Int] )),
// 							 ("cap_load", Array(parsed("cap_load").as[Double] )),//1.0)),//,0.010, 0.10, 1.0) ),
// 							 ("fanout_load", Array(parsed("fanout_load").as[Double] ))
// 		)
		
// 		val m = new MulticastCalibrationTester()
// 		m.run(HardwareMap,
// 				RuntimeMap, 
// 				TestVectorMap,
// 				N,
// 				ModuleName=ModuleName,
// 				TestName=TestName,
// 				SpecName=SpecName,
// 				EDAVerification = EDAVerification,
// 				SkipSimulation = false,
// 				ForceSynthesis = false,
// 				OutputPowerFile = parsed("OutputPowerFile").as[String],
// DontSaveInput = true
// )
// }


object Parallel2SerialSpecFromFile extends App{ 

		val jsonString = Source.fromFile(args(args.length - 1)).mkString
	
		// 解析 JSON
		val parsed = Json.parse(jsonString)
		
		// Testing Params
		val N = 10
		val EDAVerification =parsed("EDAVerification").as[Boolean]
		val ModuleName = "Parallel2Serial"//Match class names
		val SpecName = "Parallel2SerialSpec"//Match class names
		val   TestName = "Train"
		
		// Hardware Params
        val prec = parsed("prec").as[Int]
        val max_terms = parsed("terms").as[Int]
		val HardwareMap = Map(("terms",Array(max_terms)),
							  ("fanout",Array( parsed("fanout").as[Int] )),
							  ("prec",Array( prec )),
                              ("hardwareType",   Array( parsed("hardwareType").as[String] )  ), 
                              //ShiftParallel2Serial
                              //MuxParallel2Serial
							  ("tech",Array(parsed("tech").as[String]))//tsmc40"))
		)
	
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
		
		val m = new Parallel2SerialSpecTester()
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



object Parallel2SerialSpec extends App{ 

	for (fanout <- Array(1, 2, 4, 8, 16)){
	for (prec <- Array(8, 16)){
	for (max_terms <- Array(2, 4, 8, 16, 32)){
		// Testing Params
		val N = 100
		val EDAVerification =true
		val ModuleName = "Parallel2Serial"//Match class names
		val SpecName = "Parallel2SerialSpec"//Match class names
		val   TestName = "Train"
		
		
		// Hardware Params
     //   val prec = 8
       // val max_terms = 1
       // val max_terms =1
		val HardwareMap = Map(("terms",Array(max_terms)),
							  ("fanout",Array( 1 )),
							  ("prec",Array( prec )),
                              ("hardwareType", Array("MuxParallel2Serial")), 
                              //ShiftParallel2Serial
                              //MuxParallel2Serial

							  ("tech",Array("tsmc40"))//tsmc40"))
		)


    // , 0, ...
    //  K,...   output: 0,K,0,K,...
        var TestVectorMap2:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()	
		var in_0 = Array[Array[Int]]()
		var in_1 = Array[Array[Int]]() 
		var in_rest = Array[Array[Int]]()		
        var repeat = 1
		for(k <- 0 until repeat){
			for (n <- 0 until prec){
				in_0 = Array.concat(in_0, Array( Array(  (1<<n)-1 ) ) )
				in_1 = Array.concat(in_1, Array( Array(  0) ) )
				// in_rest = Array.concat(in_rest, Array( Array((1<<n) - 1, (1<<n) - 1)  ) )
			}
		}
		TestVectorMap2 = TestVectorMap2.updated("in_0", in_0)
		TestVectorMap2 = TestVectorMap2.updated("in_1", in_1) 
		for (t <- 2 to max_terms){
            if(t %2 == 0){
			TestVectorMap2 = TestVectorMap2.updated(s"in_$t", in_0) 
            }
        
        if(t %2 == 1){
			TestVectorMap2 = TestVectorMap2.updated(s"in_$t", in_1) 
            }
        

        }




    // 0, K, 0, K...
    // 0, 0, 0, 0...   output: 0, K, 0, 0, 0 , K, 0, 0...
    var TestVectorMap1:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()	
		 in_0 = Array[Array[Int]]()
		 in_1 = Array[Array[Int]]() 
	     in_rest = Array[Array[Int]]()		
         repeat = 1
		for(k <- 0 until repeat){
			for (n <- 0 until prec){
				in_0 = Array.concat(in_0, Array( Array( 0, (1<<n)-1 ) ) )
				in_1 = Array.concat(in_1, Array( Array( 0, 0) ) )
				// in_rest = Array.concat(in_rest, Array( Array((1<<n) - 1, (1<<n) - 1)  ) )
			}
		}
		TestVectorMap1 = TestVectorMap1.updated("in_0", in_0)
		TestVectorMap1 = TestVectorMap1.updated("in_1", in_1) 
		for (t <- 2 to max_terms){
            if(t %2 == 0){
			TestVectorMap1 = TestVectorMap1.updated(s"in_$t", in_0) 
            }
        
        if(t %2 == 1){
			TestVectorMap1 = TestVectorMap1.updated(s"in_$t", in_1) 
            }
        

        }



    // 0, K, 0, K...
    // 0, K, 0, K...   output: 0...K,...
        var TestVectorMap3:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()	
		 in_0 = Array[Array[Int]]()
		 in_1 = Array[Array[Int]]() 
	     in_rest = Array[Array[Int]]()		
         repeat = 1
		for(k <- 0 until repeat){
			for (n <- 0 until prec){
				in_0 = Array.concat(in_0, Array( Array( 0, (1<<n)-1 ) ) )
				in_1 = Array.concat(in_1, Array( Array( 0, (1<<n)-1 )) )
				// in_rest = Array.concat(in_rest, Array( Array((1<<n) - 1, (1<<n) - 1)  ) )
			}
		}
		TestVectorMap3 = TestVectorMap3.updated("in_0", in_0)
		TestVectorMap3 = TestVectorMap3.updated("in_1", in_1) 
		for (t <- 2 to max_terms){
            if(t %2 == 0){
			TestVectorMap3 = TestVectorMap3.updated(s"in_$t", in_0) 
            }
        
        if(t %2 == 1){
			TestVectorMap3 = TestVectorMap3.updated(s"in_$t", in_1) 
            }
        

        }



		var TestVectorMap:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()		
		for (t <- 0 to max_terms){
			TestVectorMap = TestVectorMap.updated(s"in_$t", 
				Array.concat(
					TestVectorMap1(s"in_$t" ),
					TestVectorMap2(s"in_$t" ),
					TestVectorMap3(s"in_$t" )
				 ) )
		}

        // val TestVectorMap:Map[String, Array[Array[Int]]] = Helper.GenSimpleTrainingVectors(mode="bits", p=8, dim=1)
		
        // Helper.GenSimpleTrainingVectors(mode="bits", p=8, dim=1)

        //     for (i <- 1 until parsed("terms").as[Int] ){
		// 	    val key = s"in_$i"
		// 	    val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(i)))
		// 	TestVectorMap = TestVectorMap + (key -> value)
		// }


		val RuntimeMap = Map(("CLOCK", Array(1)),
							 ("cap_load", Array(0.10)),
							 ("fanout_load", Array(0.0))
		)
		
		val m = new Parallel2SerialSpecTester()
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
}
}
}
