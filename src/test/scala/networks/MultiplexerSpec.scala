package networks

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import sys.process._

import eda._
import tester.{Helper, TechNode, FullTester}

import scala.reflect.runtime.universe._





class MultiplexerCalibrationTester extends FullTester{
	override def driver() = {
		
		class MultiplexerNSelectSpec(cc: MuxN,
		    TestVector : Map[String, Array[Int]] ,
		    N: Int = 500,
			D: Int = 1 ) extends PeekPokeTester(cc) {
				
			val c = cc
				
			  val sel_incr = TestVector("sel")(0)
			  val a: Array[Int] = TestVector("in_a")
			  val b: Array[Int] = TestVector("in_b")
			  
			var sel = 0
			for (i <- 0 until N) {
		
		
				
		
				poke(c.io.sel, sel)
				
				for (t <- 0 until cc.terms){
					if(i % 2 == 0){
						poke(c.io.in(t) , a(t % a.length))
					}else{
						poke(c.io.in(t) , b(t % b.length))
					}
				}
				
				step(D)
				
				if(i % 2 == 0){
					expect(c.io.out, a(sel % a.length))
				} else{
					expect(c.io.out, b(sel % b.length))
				}
				
					
			
				sel = (sel + sel_incr) % c.terms
				
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


object MultiplexerNTester extends App{ 
		// Testing Params
		val N = 500
		val EDAVerification = false
		val ModuleName = "MultiplexerN"//Match class names
		
		// Hardware Params
		val HardwareMap = Map(("terms",Array(16)),
							  ("prec",Array(8)),
							  ("tech",Array("tsmc40"))
		)
		
		val TestVectorMap = Map(("sel",Array( Array(0), Array(0), Array(1)    )),
							     ("in_a",  Array( Array(0), Array(0), Array(0)   )),
								 ("in_b",  Array( Array(1), Array(3), Array.range(0, 16) ))
		)
		
		val RuntimeMap = Map(("CLOCK", Array(1)),
							 ("cap_load", Array(1.0)),
							 ("fanout_load", Array(0.0))
		)
		
		//Toggle select 0-->1-->2-->3-->..., Inputs 0,测试,0,测试
		
		//Toggle Inputs 0-->测试-->测试-->。。。, select = 0
		val m = new MultiplexerCalibrationTester()
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
