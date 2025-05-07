// // See LICENSE.txt for license details.
package components

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


class AdderTreeSpec(c: AdderTree, 
    TestVector : Map[String, Array[Int]] ,
    N: Int = 500,
	D: Int = 1 ) extends PeekPokeTester(c) {

	poke(c.io.entry.valid,0)
	poke(c.io.exit.ready,0)
        val cc = c	

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
				for (n <- 0 until cc.number){
       	                        	val kk = k //% 2
	         			poke(   c.io.in(k) , TestVector(s"in_$kk"  )(s  ) )
				}
                        }
			do{
				step(D)
				//poke(c.io.entry.valid,0)		
			} while ( peek(c.io.exit.valid) == 0 )
			
                        var sum = 0
                        for (k <- 0 until cc.terms){
                                val kk = k // % 2
 
                            sum = sum + TestVector(s"in_$kk")(s)
                        }

			for (n <- 0 until cc.number){
				expect(c.io.Out(n),   sum )	
			}
			
		}
	}

}


object AdderTreeSpec extends App{ 
		// Testing Params
		val N = 500
		val EDAVerification = false//false // false //true// false
		val ModuleName = "AdderTree"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		val   TestName = "Train"
		
		val SkipSimulation =false //true// false
		val ForceSynthesis = false
		
		// Hardware Params
		val prec = 8
		val terms = 4 //128 // 32

        val HardwareMap = Map(
         	   ("prec_in", Array(prec)),
	  	   ("prec_sum", Array( prec )),
	           ("adderNType", Array( "SimpleAdderN")),//,"AddTreeN" )), //AddTreeN
        	   ("adderType", Array( "SimpleAdder2") ),// ,"RCAAdder2")),
	           ("terms", Array( terms     )),
       		   ("signed", Array(false)),
	           ("same_prec", Array(true)),
       		   ("pipelined", Array(false)),
       		   ("buffered", Array(false)),
	       	   ("auto_prec_sum", Array(true)), 
		   ("tech",Array( "tsmc40")),

		   ("number", Array(1)  ),
		   ("ratio", Array( 2  )    ),
		   ("htype", Array( "AdderTree"  )),
		)
  
		
		var TestVectorMap = Helper.GenSimpleTrainingVectors(mode="bits", p=prec, dim=2)
		for (t <- 2 until terms){	
			TestVectorMap = TestVectorMap.updated(s"in_$t", TestVectorMap(s"in_${t % 2}"))
		}


		println(TestVectorMap("in_0").length)

	
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
							val m = new AdderTree(this.HardwareConfig)
						//AdderNFactory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new AdderTreeSpec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
