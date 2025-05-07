// // See LICENSE.txt for license details.
// package adders

// import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

// import sys.process._

// class Accumulator1Spec(c: GenericAdderN, 
//    a: Array[Int], N: Int = 500,
// 	D: Int = 1) extends PeekPokeTester(c) {
//   // println(""+b(1))
  
//   poke(c.io.entry.valid,0)
//   poke(c.io.exit.ready,0)
//  for (i <- 0 until N) {
	 
	 
	
// 	poke(c.io.entry.valid,1)
// 	poke(c.io.exit.ready,1)
// 	// println("ready"+peek(c.io.entry.ready))
// 	while(peek(c.io.entry.ready) == 0){

// 		step(D)
// 	}
	
	
// 	var j = 0
// 	do{
// 		poke(c.io.A(0), a(j))
		
// 		poke(c.io.entry.valid,1)
// 		step(D)
// 		j = j + 1
		
// 	} while ( peek(c.io.exit.valid) == 0 )
	
// 	// println("TESTING AB " + c.io.Sum)
// 	// println("TESTING " + i + "\t"+peek(c.io.Sum) + "\tvalid: " + peek(c.io.exit.valid)  )
// 		expect(c.io.Sum,a.reduce((x,y)=> x + y))

//  }
//     // println("TESTING AddN Complete\t"+ a(1)+"\t"+ b(1)+"\t"+ c)

// }

	
// class Accumulator1Tester extends ChiselFlatSpec {
		
// 	val name = "Accumulator1"
// 	val N = 10
// 	//val terms = 4
// 	val prec_in = 8
// 	val prec_out = 12
// 	val buffered = true
// 	//val zhi = 8
// 	val adder2Type= "RCAAdder2"//"SimpleAdder2"
	  
// 	for (terms <- Array(2, 4, 8)){
// 		for (zhi <- Array(8, 16, 127)){
			  
			  
// 	  // TEST CASE - SimpleAddN
// 	  behavior of s"${name}_${terms}_$zhi"
// 	  backends foreach {backend =>
// 	    it should s"correctly add numbers in $backend" in {
		
			
// 	            Driver.execute(  Array("--generate-vcd-output" , "on", 
// 			          "--top-name", s"${name}Spec",
// 			           "--target-dir", s"generated/${name}"),  () => (new 
// 					   Accumulator1( terms=terms,
// 					        prec_in =prec_in,
// 					   	 prec_out =prec_out,
// 					   	 adder2Type= adder2Type, 
// 					   	 pipelined = false,
// 					   	 buffered = false
// 					   	) 
// 					   ).asInstanceOf[GenericAdderN])(c => new Accumulator1Spec(c.asInstanceOf[GenericAdderN], Array.fill(terms)(zhi),N=N )) should be (true)
// 		      }
// 			}
// 		// END TESTCASE
	
		
		
// 		}
// 	  }
	  
	  
	  
	  
// 	}
	
	