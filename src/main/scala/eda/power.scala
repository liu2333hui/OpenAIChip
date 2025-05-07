package eda

import scala.io._
import java.io._
import sys.process._
import scala.io.Source

object power{


        def main(args: Array[String]) {

             //val pwr : Double =  get_average_power("./generated/AddTreeN/AddTreeN_SimpleAdder2_8_false_8_tsmc40/AddTreeN_SimpleAdder2_8_false_8_tsmc40.127.ptpx_res.txt")
//      println("PWR = "+pwr)

      }


      def get_total_cycles( vcdFile:String): Int = {
  
            
       // ("total" -> total)
       // ("reset" -> reset) 
       val lines = Source.fromFile(vcdFile).getLines().toList

        var timestamps_latest = 0
        for (line <- lines) {
          if (line.startsWith("#")) {
            val timestamp = line.substring(1).toInt
              timestamps_latest = timestamp
      	  }     
	}


        timestamps_latest

       }


       def get_average_power(report:String) :Array[Double] = {


         val source : BufferedSource = Source.fromFile(report)
           val lines:Iterator[String] = source.getLines()
            val myread :List[String] = lines.toList
             var state = 0

             for(line <- myread){
                   if(state == 0){
                        if(line.contains("-----")){
                          state = 1
                            }
                         
                   }
                    else {
                   println(line)
                    val elements = line.split("\\s+")

                   val result = elements.slice(1, 5).map(_.toDouble )
                     return  result
                    state = state + 1

                  }

              }

    
               Array[Double]()
}

	def run(module_out_name:String="SimpleAdder2_1",module:String = "SimpleAdder2", root:String="generated", testbench:String="test_0"):Unit = {
	
	//val result:Int = "source ptpx.sh"!

val result:Int = 	s"vcd2saif -input ${root}/${module_out_name}/${testbench}.vcd -output ${root}/${module_out_name}/${testbench}.saif"!
val result2:Int = 	"pt_shell -f ptpx.tcl"!
	
		
		
	}
	
def ptpx_script(
	target_library : String = "/nfs/project/JayMok/power_experiments_xie/fab/t40lp/sc/tcbn40lpbwp/nldm/tcbn40lpbwptc.db",
	module : String = "SimpleAdder2",
	root : String = "generated",
   
         module_out_name : String = "SimpleAdder2",
       testbench : String = "test1",

	cap_load : Double = 10,
	fanout_load: Double = 0.1,

	input_transition: Double = 0.5,
	max_transition: Double = 0.6,
	max_clock_delay : Double= 1.2,
	min_clock_delay: Double = 1.2,
	min_data_delay : Double= 1.2,
	max_data_delay: Double = 1.2

	):String = {


	//write ptpx.sh
	
	val writer_ptpx = new PrintWriter(new File("ptpx.tcl" ))
	
	val ptpx_sh = s"""
	#dc_shell -f zonghe.tcl 
	vcd2saif -input ${root}/${module}/${module}.vcd -output ${root}/${module}/${module}.saif
	pt_shell -f ptpx.tcl
	"""
	
	writer_ptpx.write(ptpx_sh)
	
	writer_ptpx.close()
	
	// #dc_shell -f zonghe.tcl
	// vcd2saif -input SimpleAdd2.vcd -output SimpleAdd2.saif
	// pt_shell -f ptpx.tcl
	
	
	

	// write ptpx.tcl

	val writer = new PrintWriter(new File("ptpx.tcl" ))



	val tcl = s"""
    set power_enable_analysis TRUE
    set power_enable_clock_scaling TRUE
    set CUR_DESIGN ${module}
    set verilog_file ./${root}/${module_out_name}/${module}.syn.v
    set sdc_file ./${root}/${module_out_name}/${module}.syn.sdc
    
    set_app_var target_library [list ${target_library}]
    set_app_var link_library """+"\"* $target_library\"" + """
    set link_path [list ${target_library}]
    set link_path "* """+"$link_path"+"""  "
    read_verilog """+"$verilog_file"+"""
    current_design """+"$CUR_DESIGN"+s"""


    #link
    read_sdc """+"$sdc_file"+ s"""
    

    create_clock -period 1 -name CLK [get_ports clock] 

	set_fanout_load ${fanout_load} [all_outputs]
	set_input_transition ${input_transition} [all_inputs]
	set_load ${cap_load} [all_outputs]
	set_max_transition ${max_transition} [current_design]
	set max_clock_delay ${max_clock_delay}
	set min_clock_delay ${min_clock_delay}
	set max_data_delay ${max_data_delay}
	set min_data_delay ${min_data_delay}
	

    set_propagated_clock [all_clocks]
    read_saif -strip_path ${module} ${root}/${module_out_name}/${testbench}.saif
    report_switching_activity
    check_timing
    update_timing
    update_power
    report_power
    report_power -h > ${root}/${module_out_name}/${module}.${testbench}.ptpx_res.txt 
    exit
    """
	

	writer.write(tcl)

	writer.close()


        s"${root}/${module_out_name}/${module}.${testbench}.ptpx_res.txt"

}

}
