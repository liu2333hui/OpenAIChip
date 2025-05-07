//Parallel Load, Parallel Out


// See LICENSE.txt for license details.
package memories

import chisel3._


//SInt
class RegisterN[T <: Data ](dt: T, terms:Int,
 precision :Int, has_enable: Boolean = true, 
	multicast_enable:Boolean =true, 
	) extends Module {
		
			val io = IO(new Bundle {
				val in = Input (  Vec(terms, dt ) )
				val out  = Output(Vec(terms, dt ) )
				})
	
	if(has_enable){
		if(multicast_enable){
			
				val en = Input (Bool())
		
			when(en){
				io.out := io.in
			}
					
		}else{
					val en = Input (  Vec(terms, Bool()))
				
				
			for (i <- 0 until terms){
				when(en(i)){
					io.out(i) := io.in(i)
				}
			}
				
		}
	} else{
		
		
		io.out := io.in
		
			
	}
  
  
  
}
