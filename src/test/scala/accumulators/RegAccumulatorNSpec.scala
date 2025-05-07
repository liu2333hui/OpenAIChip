// // See LICENSE.txt for license details.
package accumulators

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import eda._
import tester.{Helper, TechNode, FullTester}
import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._
import scala.io.Source

import play.api.libs.json._

import java.lang.Math

class RegAccumulatorNSpec_Testing(c: RegAccumulatorN, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

	poke(c.io.entry.valid,0)
	poke(c.io.exit.ready,0)
	
	val a: Array[Int] = TestVector("in_0")
	val clr:Array[Int] = TestVector("in_1")
	val a_len = a.length
	
	for (i <- 0 until N) {	
		
		poke(c.io.entry.valid,0)
		poke(c.io.exit.ready,1)
		poke(c.io.clear, 1)
		poke(c.io.en,   0)
		step(D)
		var accum:Int = 0
		//expect(c.io.Sum, accum)
		
		for (s <- 0 until a.length  ){
			
			//Trigger

			if(clr(s % clr.length) == 1){
				poke(c.io.entry.valid,0)
				poke(c.io.exit.ready,1)
				poke(c.io.clear, 1)
				poke(c.io.en,   0)	
			}else{
				poke(c.io.clear, 0)
				poke(c.io.en,   1)	
			

			//Set Data
			poke(c.io.entry.valid,1)
			for( t <- 0 until c.terms){
				poke(c.io.A(t), a(s % a_len)   )
			}
			
			do{
				step(D)
				
				poke(c.io.entry.valid,0)
				//poke(c.io.entry.valid,0)		
			} while ( peek(c.io.exit.valid) == 0 ) 
		        		
			accum = (accum + c.terms*a(s % a_len)) %(1<<c.prec_out)
			expect(c.io.Sum,accum)

		 	//poke(c.io.clear, 1)
			//poke(c.io.en   , 0)
	                //step(D)
			//expect(c.io.Sum, 0)
                        //step(D)	
			
		}
	}


	}
    // println("TESTING AddN Complete\t"+ a(1)+"\t"+ b(1)+"\t"+ c)

}



class RegAccumulatorNSpec(c: RegAccumulatorN, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

	poke(c.io.entry.valid,0)
	poke(c.io.exit.ready,0)
	
	val a: Array[Int] = TestVector("in_0")
	val a_len = a.length
	println("A_LEN"+ a_len)	
	for (i <- 0 until N) {	
		
		poke(c.io.entry.valid,0)
		poke(c.io.exit.ready,1)
		poke(c.io.clear, 1)
		poke(c.io.en,   0)
		step(D)
		var accum:Int = 0
		expect(c.io.Sum, accum)
		
		for (s <- 0 until a.length  ){
			
			//Trigger
			poke(c.io.clear, 0)
			poke(c.io.en   , 1)
			while( peek(c.io.entry.ready) == 0 ){
				step(D)
			}
		
			//Set Data
			
			poke(c.io.entry.valid,1)
			for( t <- 0 until c.terms){
				poke(c.io.A(t), a(s % a_len)   )
			}
			
			do{
				step(D)
				
				poke(c.io.entry.valid,0)
				//poke(c.io.entry.valid,0)		
			} while ( peek(c.io.exit.valid) == 0 )

		        		
			//accum = (accum + c.terms*a(s % a_len) )
			accum = accum + a(s % a_len)
			println(""+c.io.Sum +"\t"+accum)
			expect(c.io.Sum, a(s)  )//accum)
			
		}
	}
    // println("TESTING AddN Complete\t"+ a(1)+"\t"+ b(1)+"\t"+ c)

}


object RegAccumulatorNSpecFromFile extends App{

		val jsonString = Source.fromFile(args(args.length - 1)).mkString
		val parsed = Json.parse(jsonString)



		val N = 10
		val EDAVerification = parsed("EDAVerification").as[Boolean]
		val ModuleName = "Accumulator"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation = false
		val ForceSynthesis = false
		
		// Hardware Params
		val HardwareMap = Map(

          ("prec_in", Array( parsed("prec_in").as[Int] )),
	  ("prec_out", Array(  parsed("prec_sum").as[Int]  )), 
			("terms",Array( parsed("terms").as[Int]  )),
			("same_prec",Array(true)),
			("buffered",Array(false)), //buffered for terms > 1 has bug ..
			("adderType",Array("RCAAdder2")),
			("adderNType", Array("SimpleAdderN")),
			("signed", Array(false)),
			("pipelined", Array(false)),
	  ("tech",Array( parsed("tech").as[String])))
	
		
		var in_0 =  Helper.transpose(Helper.readFileTo2DArrayWithPadding(args(0)) )
		in_0  = in_0.map(subArray => subArray :+ 0)
		val in_1 = in_0.map(_.map(_ => 0))

		var TestVectorMap = Map(
			("in_0", in_0),	
			("in_1", in_1)	
	
		)
		//need to pad a zero at the end of in_0 (can we fix this eventually?)	
				


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
							// val m = new SimpleAdder2(this.HardwareConfig)
							val m = new RegAccumulatorN(this.HardwareConfig)
							//Adder2Factory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new RegAccumulatorNSpec_Testing(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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

object RegAccumulatorNSpec extends App{ 

//for (repeat <- Array(1, 5, 10, 20, 50, 100, 200, 1000)){
val out_prec = 16
for (prec <- Array( 8)){
for (repeat <- Array(1,5,10,20,50,100,200, 500, 1000)){

	for( zero <- Array(0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2048-1, 
		4096-1, 8192-1, 8192*2-1, 8192*4-1, 8192*8-1, 1<<16 - 1)){

		// Testing Params
		val N = 10
		val EDAVerification = true //false
		val ModuleName = "Accumulator"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation = false
		val ForceSynthesis = false
		
		// Hardware Params
		val HardwareMap = Map(
			("prec_out",Array(out_prec)),
			("prec_in",Array(prec)),
			("terms",Array(1)),
			("same_prec",Array(false)),
			("buffered",Array(false)), //buffered for terms > 1 has bug ..
			("adderType",Array("RCAAdder2")),
		//	("multioperandAdderType", Array("RCAAdder2")),
			("adderNType", Array("SimpleAdderN")),
			("signed", Array(false)),
			("pipelined", Array(false)),
			("tech",Array("tsmc40"))
		)
		
		val A = 121424
		var TestVectorMap = Map( ("in_0",Array( Array.fill(repeat)(Array(  A, (1<<16) - A   )).flatten  ) ))
		TestVectorMap = Helper.GenSimpleTrainingVectors(mode="complements_full", p=1<<16, dim=1,
			repeat = 100,
			prec = 16)

		TestVectorMap = Helper.GenSimpleTrainingVectors(mode="bits", p=16, dim=1, zero = zero,
			repeat = repeat,
			prec = 32)




 var in_0 =  (0 to (1<<16)).map { i =>
//    Array(Math.pow(2, i).toInt - 1, 0 )
    Array(i.toInt , 0 )
 
  }.toArray

		var in_1 = Array.fill((1<<16))( Array(0,1)  )	

		/*	
		TestVectorMap = Map(
			 ("in_0",Array( Array( 0,0  ) ,
					 Array (1,1 ) ,
					 Array (3,3 ) ,
					 Array (7,7 ) ,
					 Array (15,15 ) ,
					 Array (31,31 ) ,
					 Array (63,63 ) ,
					 Array (127,127 ) ,
					 Array (255,255 ) ,
					 Array (511,511 ) ,
					 Array (1023,1023 ) ,
					 Array (2047,2047 ) ,
					 Array (4095,4095 ) ,
					 Array (4096*2-1,4096*2-1 ) ,
					 Array (4096*4-1,4096*4-1 ) ,
					 Array (4096*8-1,4096*8-1 ) 

) ),
			 ("in_1",Array( Array(  0, 1  ),
				Array(  0, 1  ),
				Array(  0, 1  ),
				Array(  0, 1  ),
				Array(  0, 1  ),
				Array(  0, 1  ),
				Array(  0, 1  ),
				Array(  0, 1  ),
				Array(  0, 1  ),
Array(  0, 1  ),
Array(  0, 1  ),
Array(  0, 1  ),
Array(  0, 1  ),
Array(  0, 1  ),
Array(  0, 1  ),Array(  0, 1  )

  ) )
	
		
		)	
		*/
		
		in_0 = Array (Array (8888,9999, 666,666, 912839, 1, 1, 1, 1, 1, 1, 1 ,0 ))
		in_1 = Array ( Array.fill(in_0(0).length-1) ( Array(0)  ).flatten  :+ 0 )




		TestVectorMap = Map(
			("in_0", in_0),
			("in_1", in_1)	
		)	
		val RuntimeMap = Map(("CLOCK", Array(1)),
					 ("cap_load", Array(1.0)),
					 ("fanout_load", Array(0.0))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							// val m = new SimpleAdder2(this.HardwareConfig)
							val m = new RegAccumulatorN(this.HardwareConfig)
							//Adder2Factory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new RegAccumulatorNSpec_Testing(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
		}}
}
