// //Use a booth encoding
// //To increase summations of 0 and thus decrease power
// //Similar to the HighRadixMultiplier

// package multipliers

// //Booth encoder
// // 0   0     0
// // 0   1     1
// // 1   0    -1
// // 1   1     0

// import chisel3._
// import chisel3.util._

// class BoothEncoder2 extends Module{
//   val io = IO(new Bundle {
//     val a    = Input(UInt(1.W))
//     val a_prev    = Input(UInt(1.W))
//     val Out  = Output(SInt(2.W))	
//   })
  
//   when(a == 0.U and a_prev == 0.U){
// 	  Out := 0.S	  
//   } .elsewhen(a == 1.U and a_prev == 0.U) {
// 	  Out := 1.S
//   } .elsewhen(a == 0.U and a_prev == 1.U) {
// 	  Out := -1.S
//   } .otherwise{
// 	  Out := 0.S
//   }
  
// }

// //3 --> radix = 4, 4 --> radix = 8
// class BoothEncoderN(radix:Int) extends Module {
// 	val terms = log2Ceil( radix ) + 1
	
// 	val io = IO(new Bundle {
// 		val a   = Input(  UInt(terms.W)     )
// 		val Out = Output( SInt(terms.W)     )
// 	})
	
// 	val bits : Array[Int] = Array.fill(terms)
// 	for (i <- 0 until math.pow(2, terms).toInt ){
// 	    for (j <- 0 until terms){
// 			bits(j) = (i >> j) % 2
// 		}	
// 		var booth_value = -radix*bits(0) 
// 		for (j <- 1 until terms){
// 			radix/2*bits(j)
// 			booth_value = booth_value + bits(j)
// 		}
		
// 		when( io.a == i.U    )  {
// 			Out := booth_value.toSint
// 		}	
// 	}
	
// }

// class SimpleBoothMultiplier2() extends Module {
	
// }