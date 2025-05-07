// // See LICENSE.txt for license details.
package training

import multipliers._

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import eda._
import tester.{Helper, TechNode, FullTester}
import chisel3._
import chisel3.util._
import scala.collection.mutable.Queue
import helper._

object Multiplier2Train extends App{ 
		// Testing Params
		val N = 500
		val EDAVerification = false
		val ModuleName = "Multiplier2"//Match class names
		val SpecName = s"${ModuleName}Spec"//Match class names
		
		val SkipSimulation = false
		val ForceSynthesis = false
		
		// Hardware Params
		val HardwareMap = Map(("prec2",Array(8,16)),
							  ("prec1",Array(8,16)),
							  ("prec_out", Array(16)),
							  ("auto_prec_out", Array(true)),
							  ("radix"   , Array(2,4,8)), //2,4,8
							  ("side", Array("A", "B", "dual")),//"A", "B", "dual"
							  ("multiplierType", Array("BitSerialMultiplier")),
							  ("buffered",Array(false)),
							  ("signed", Array(false)),  
							  ("adderType",Array("SimpleAdder2")),
							  ("tech",Array("tsmc40"))
		)
		val HardwareMap2 = Map(("prec2",Array(4,8,16)),
							  ("prec1",Array(4,8,16)),
							  ("prec_out", Array(16)),
							  ("auto_prec_out", Array(true)),
							  ("radix"   , Array(2,4,8)), //2,4,8
							  ("multiplierType", Array("SimpleMultiplier2",
								"HighRadixMultiplier2"
							  )),
							  ("buffered",Array(false)),
							  ("signed", Array(false)),  
							  ("adderType",Array("SimpleAdder2")),
							  ("tech",Array("tsmc40"))
		)
				
				
		val TestVectorMap = Map(("in_a",Array(  Array(0,1) , Array(0, 3) ,  Array(0, 127)   )),
							  ("in_b",Array(    Array(0,1) , Array(0, 3) , Array(0, 127)   ))
		)
		
		// val TestVectorMap = Map("in_a", GenSimpleTrainingVectors)
		
		val RuntimeMap = Map(("CLOCK", Array(1)),
							 ("cap_load", Array(0.010)),
							 ("fanout_load", Array(0.0))
		)
		
		
		class Tester extends FullTester{
			override def driver() = {
					Driver.execute(  Array("--generate-vcd-output" , "on",
					  "--top-name", this.SpecName,
					   "--target-dir", this.TargetDir), 
					   () => {
							val m = Multiplier2Factory.create(this.HardwareConfig)
							( m  ) 
					   })( c => {
						    val mspec = new Multiplier2Spec(c, TestVector=this.TestVector, N=this.N,D=this.CLOCK) 
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
				TestName="Train",
				SpecName=SpecName,
				EDAVerification = EDAVerification,
				SkipSimulation = SkipSimulation,
				ForceSynthesis = ForceSynthesis)


		m.run(HardwareMap2,
						RuntimeMap, 
						TestVectorMap,
						N,
						ModuleName=ModuleName,
						TestName="Train2",
						SpecName=SpecName,
						EDAVerification = EDAVerification,
						SkipSimulation = SkipSimulation,
						ForceSynthesis = ForceSynthesis)

}