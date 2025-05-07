// package adders

// import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

// import sys.process._

// import eda._


// object AddTreeNTester extends App{ 

// """ (ACCORDING TO DEEPSEEKV3) regarding 40nm technology FO4 capacitance
// Total load capacitance: For a typical fan-out of 4 (FO4) inverter chain, the load capacitance is often around 10 fF to 20 fF, including both gate and interconnect capacitances.
// """

// 		val N = 500
// 		val prec_in = 8	
// 		val zhi1= 1 
// 		val buffereds = Array(true, false)//true// false
// 		val cap_load = 0.010 //10//.0
// 		val fanout_load = 0.0
// 		val CLOCK = 1	


// 		val adderTypes = Array("SimpleAdder2")
// 		val termss = Array(8)//16)//8)
// 		//val zhis = Array(8,16,17,32,64,88,127)
// 		val zhis = Array(8,88,127)

// 		//val terms = 4
// 		// val adderType = "SimpleAdder2"
// 		//val zhi = 8

//       if(true){
//          for (buffered <- buffereds){
// 	for (adderType <-adderTypes){ //, "RCAAdder2")){
// 	for (terms <- termss){

//            val module = s"AddTreeN"//_${adderType}_${terms}_${buffered}_${prec_in}_tsmc40"


//            val module_out_name = s"AddTreeN_${adderType}_${terms}_${buffered}_${prec_in}_tsmc40"
// 	 for (zhi <- zhis ){
	
	
//            val testcase = module_out_name+"_"+zhi 
//            val testbench = s"$zhi"	


// 			Driver.execute(  Array("--generate-vcd-output" , "on", 
// 				  "--top-name", "SimpleAddNSpec",
// 				   "--target-dir", s"generated/${module_out_name}"),  () 
// 				   => (new AddTreeN(terms,prec_in,adderType,buffered=buffered)).asInstanceOf[GenericAdderN])(c => {


// new SimpleAddNSpec(c.asInstanceOf[GenericAdderN], Array.fill(terms)(zhi1), Array.fill(terms)(zhi), 
// N=N, D = CLOCK )})




//   //Run power post analysis
//            synthesis.dc_shell_synthesis_script(target_library="/nfs/project/JayMok/power_experiments_xie/fab/t40lp/sc/tcbn40lpbwp/nldm/tcbn40lpbwptc.db",module=module, cap_load=cap_load,fanout_load=fanout_load, module_out_name=module_out_name)
//            synthesis.run(module=module, module_out_name=module_out_name, force=false)


//   power.ptpx_script(target_library="/nfs/project/JayMok/power_experiments_xie/fab/t40lp/sc/tcbn40lpbwp/nldm/tcbn40lpbwptc.db",module=module, module_out_name=module_out_name, cap_load=cap_load, fanout_load=fanout_load, testbench=testbench)


//    power.run(module=module, module_out_name=module_out_name)//, module_out_name=module_out_name)

//    }}}
// }
//      }



//          for (buffered <- buffereds){
	
// 	for (adderType <-adderTypes){ //, "RCAAdder2")){
// 	for (terms <- termss){
//            val module = s"AddTreeN"//_${adderType}_${terms}_${buffered}_${prec_in}_tsmc40"
//            val module_out_name = s"AddTreeN_${adderType}_${terms}_${buffered}_${prec_in}_tsmc40"
// 	 for (zhi <- zhis ){	
//            val testcase = module_out_name+"_"+zhi 
//            val testbench = s"$zhi"	


//            val report:String = power.ptpx_script(target_library="/nfs/project/JayMok/power_experiments_xie/fab/t40lp/sc/tcbn40lpbwp/nldm/tcbn40lpbwptc.db",module=module, module_out_name=module_out_name, cap_load=cap_load, fanout_load=fanout_load, testbench=testbench)
//             println(testcase)//testbench)
//             power.get_average_power(report)

//    }}}  
// }  

  
// }
