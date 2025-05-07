// // See LICENSE.txt for license details.
// package adders

// import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

// class SimpleAddNSpec(c: GenericAdderN, a: Array[Int], b: Array[Int], N: Int = 500,
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
	 
// 	for (j <- 0 until a.length){
// 		// println(""+j+"\t"+ a(j)+"\t"+ b(j))
// 		if(i % 2 == 0){
// 			poke(c.io.A(j), a(j))
// 		} else {
// 			poke(c.io.A(j), b(j))
// 		}
		
// 	}
	
// 	do{
// 		step(D)
// 		poke(c.io.entry.valid,0)
		
// 	} while ( peek(c.io.exit.valid) == 0 )
	
// 	// println("TESTING AB " + c.io.Sum)
// 	// println("TESTING " + i + "\t"+peek(c.io.Sum) + "\tvalid: " + peek(c.io.exit.valid)  )
// 	if(i % 2 == 0){
// 		expect(c.io.Sum,a.reduce((x,y)=> x + y))
// 	} else{
// 		expect(c.io.Sum,b.reduce((x,y)=> x + y))
// 	}

//  }
//     println("TESTING AddN Complete\t"+ a(1)+"\t"+ b(1)+"\t"+ c)

// }

	
// 	class SimpleAddNTester extends ChiselFlatSpec {
		
		
// 		for (terms <- Array(2,4,8)){
// 		  for (zhi <- Array(8, 16)){
			  
			  
// 	  // TEST CASE - SimpleAddN
// 	  behavior of s"SimpleAddN_${terms}_$zhi"
// 	  backends foreach {backend =>
// 	    it should s"correctly add numbers in $backend" in {
		
// 		     //val terms = 4
// 		       val prec_in = 8
// 		       val prec_out = 12
// 			   val buffered = true
// 		       //val zhi = 8
			
// 	            Driver.execute(  Array("--generate-vcd-output" , "on", 
// 			          "--top-name", "SimpleAddNSpec",
// 			           "--target-dir", "generated/SimpleAddN"),  () => (new SimpleAdderN(terms,prec_in,prec_out, buffered=buffered)).asInstanceOf[GenericAdderN])(c => new SimpleAddNSpec(c.asInstanceOf[GenericAdderN], Array.fill(terms)(zhi), Array.fill(terms)(0) )) should be (true)
// 		      }
// 			}
// 		// END TESTCASE
		
		
		
// 		}
// 	  }
	  
	  
	  
	  
// 	}
	
	
