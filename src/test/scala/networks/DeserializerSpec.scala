package networks

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import sys.process._

import eda._
import tester.{Helper, TechNode, FullTester}

import scala.reflect.runtime.universe._


import play.api.libs.json._
import scala.io.Source

import play.api.libs.json._


class DeserializerSpec(cc: GenericDeserializer, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(cc) {
		
	val c = cc
		
    
	val a: Array[Int] = TestVector("in_0")
	

	for ( i <- 0 until N ) {

            for (s <- 0 until (a.length-c.out_terms) by c.out_terms) {

                //Trigger
                poke(c.io.entry.valid,1)
                poke(c.io.exit.ready,1)
            
                poke(c.io.en, 1)

                var no = 0
                while(peek(c.io.entry.ready) == 0){
                    step(D)            
                }
            
                // step(D)   
                do{
                    poke(c.io.in , TestVector(s"in_0")(s+no))  
                    step(D)
                    //poke(c.io.entry.valid,0)		
                    no = no + 1
                } while ( peek(c.io.exit.valid) == 0 )


                //validate
                for (no <- 0 until c.out_terms){
                for (f <- 0 until c.fanout){
                    val kk = no  
                    expect(c.io.out(kk)(f), TestVector(s"in_0")(s+no))
                }}


            }
	
	}


}



class DeserializerSpecTester extends FullTester{
	
	// HardwareConfig: Map[String,String],
		// TestVector : Map[String, Array[Int]], N : Int, CLOCK: Int, ModuleNameSpecName:String
	override def driver() = {
			
			Driver.execute(  Array("--generate-vcd-output" , "on",
			  "--top-name", this.SpecName,
			   "--target-dir", this.TargetDir), 
			   () => {
                //    val m = Multiplier2Factory.create(this.HardwareConfig)

				   val m = DeserializerFactory.create_general(this.HardwareConfig)
					// val m = new Parallel2Serial(this.HardwareConfig)
					( m  ) 
			   })( c => {
				    val mspec = new DeserializerSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
			   	    ( mspec )  
					  
				} ) 

	}
	
}



object DeserializerSpecFromFile extends App{ 
	
	//val jsonString = Source.fromFile(args(1)).mkString
	val jsonString = Source.fromFile(args(args.length - 1)).mkString


	
	// 解析 JSON
	val parsed = Json.parse(jsonString)
	
	
		// Testing Params
		val N = 100
		val EDAVerification = parsed("EDAVerification").as[Boolean]
		val ModuleName = "Deserializer"//Match class names
		val SpecName = "DeserializerSpec"//Match class names
		val   TestName = "Test"
		
				// Hardware Params
        // val prec = 8
        // val max_terms = 1
		val HardwareMap = Map(("out_terms",Array( parsed("out_terms").as[Int] )),
							  ("fanout",Array( parsed("fanout").as[Int] )),
							  ("prec",Array( parsed("prec").as[Int] )),
                              ("hardwareType", Array(   parsed("hardwareType").as[String]   )), 
                              //ShiftDeserializer
                              //MuxDeserializer
			 	("tech",Array( parsed("tech").as[String] ))//tsmc40"))
		)
		
 		var TestVectorMap = Map(
			("in_0", Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0))))	
		)

		//Hetereogenous Primitive Mapping, i.e. systolic casting
		val CustomMap = parsed("CustomMap").as[Map[String,String]]
		println("read map")
		for ((k, v) <- CustomMap){
			println(s"Key: $k, Value: $v")
			
		}
		var idx = 1
		for ((k, v) <- CustomMap) {
			// println(s"Key: $k, Value: $v")
			TestVectorMap = TestVectorMap + (k-> Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(idx))))	
			idx += 1
		}

		// for (v <- CustomMap){
		// 	TestVectorMap = TestVectorMap + (v, Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(idx))))	
		// 	idx += 1
		// }


		// for (i <- 1 until parsed("terms").as[Int] ){
		// 	val key = s"in_$i"
		// 	val value = Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(i)))
		// 	TestVectorMap = TestVectorMap + (key -> value)
		// }


		
		println("LOADED"+ TestVectorMap("in_0").length + "\t" + TestVectorMap("in_0")(0).length)
		
		val RuntimeMap = Map(("CLOCK", Array(parsed("CLOCK").as[Int] )),
							 ("cap_load", Array(parsed("cap_load").as[Double] )),//1.0)),//,0.010, 0.10, 1.0) ),
							 ("fanout_load", Array(parsed("fanout_load").as[Double] ))
		)
		
		val m = new DeserializerSpecTester()
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
DontSaveInput = true,
CustomMap = CustomMap
)
}



object DeserializerSpec extends App{ 

def createPatternArray2(N: Int, K: Int): List[Int] = {
  val zeros = List.fill(K)(0)    // 创建 K 个 0
  val ns = List.fill(K)(N)       // 创建 K 个 N
  val pattern = zeros ++ ns      // 组合成 [0,0,..., N,N,...]
  pattern ++ pattern             // 重复两次
}

def createPatternArray(N: Int, K: Int): Array[Int] = {
  val zeros = Array.fill(K)(0)    // 创建包含 K 个 0 的数组‌:ml-citation{ref="1,5" data="citationList"}
  val ns = Array.fill(K)(N)      // 创建包含 K 个 N 的数组‌:ml-citation{ref="1,5" data="citationList"}
  val pattern = zeros ++ ns      // 拼接为 [0,0,...,N,N,...]‌:ml-citation{ref="4,6" data="citationList"}
  (pattern ++ pattern).toArray   // 重复两次并转为 Array‌:ml-citation{ref="4,6" data="citationList"}
}

	for (prec <- Array(8, 16)){
	for (fanout <- Array(1)){//1 ok 
	for (max_terms <- Array(32,1,2,4,8,16)) { //1, 2, 4, 8, 16, 32, 64)){


		// Testing Params
		val N = 32
		val EDAVerification =true//false
		val ModuleName = "Deserializer"//Match class names
		val SpecName = "DeserializerSpec"//Match class names
		val   TestName = "Train"
		
		
		// Hardware Params
       // val prec = 8
        //val max_terms = 1
		val HardwareMap = Map(("out_terms",Array(max_terms)),
							  ("fanout",Array( fanout )),
							  ("prec",Array( prec )),
                              ("hardwareType", Array("MuxDeserializer")), 
                              //ShiftDeserializer
                              //MuxDeserializer
							  ("tech",Array("tsmc40"))//tsmc40"))
		)


	// output 00,0.0.0. ....., K, K, K, K, K, K, K, K, K, K


        // , 0, ...
        //  K,...   output: 0,K,0,K,...
        var TestVectorMap2:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()	
		var in_0 = Array[Array[Int]]()	
        var repeat = 1
		for(k <- 0 until repeat){
			for (n <- 0 until prec){
                val K =  (1<<n)-1
		val Z = 0
                val list = List.fill(max_terms)(List( Z,   K)).flatten//.take(max_terms)
                var array = list.toArray // 结果：Array(0, 5, 0, 5)
                //array = Array(0,1,2,3,4,5,6,7)
				in_0 = Array.concat(in_0, Array( array ) )
			}
		}
		TestVectorMap2 = TestVectorMap2.updated("in_0", in_0)
        



        // , 0, ...
        //  K,...   output: 0,K,0,K,...
// TestVectorMap3.updated("in_0", in_0)
 




		var TestVectorMap:Map[String, Array[Array[Int]]] = Map[String, Array[Array[Int]]]()		
		//for (t <- 0 until 1){



			//TestVectorMap = TestVectorMap.updated(s"in_$t", 
		//		Array.concat(
		//			TestVectorMap2(s"in_$t" ),
		//		 ) )


		val nestedArray = new Array[Array[Int]](prec)

		for (i <-0 until prec) {
		     nestedArray(i) = createPatternArray((1<<i) - 1 , max_terms )
		}
		TestVectorMap = TestVectorMap.updated(s"in_0", nestedArray)
		//	for (k <- 0 until prec){

		//		TestVectorMap = TestVectorMap.updated(s"in_$t", 
		//		Array.concat(
		//			Array( createPatternArray((1<<k) - 1 , max_terms ))
		//		 ) )


		//	}

		//}
		print("LENGTH\t" + TestVectorMap("in_0").length)
		
		//sys.exit()
		//TestVectorMap = Map(
		//	("in_0", Array( Array(1, 23, 123, 0, 0, 0, 0, 0, 0, 0, 0)))
		//)

		val RuntimeMap = Map(("CLOCK", Array(1)),
							 ("cap_load", Array(1.0)),
							 ("fanout_load", Array(0.0))
		)
		
		val m = new DeserializerSpecTester()
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
		
		//sys.exit()
		

}
}
}

}
