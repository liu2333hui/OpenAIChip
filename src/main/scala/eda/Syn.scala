package eda
import scala.io._
import java.io._
import sys.process._
import java.nio.file.{Paths, Files}

object synthesis{

	def run(module:String = "SimpleAdder2", root:String="generated", module_out_name:String="SimpleAdder2", force:Boolean=false):Unit = {

      
      //println(s"./${root}/${module_out_name}/${module}.syn.v") 
     // println(Files.exists(Paths.get( s"./${root}/${module_out_name}/${module}.syn.v")))
      //sys.exit(0)	
      if(! Files.exists(Paths.get(s"./${root}/${module_out_name}/${module}.syn.v")) || force){

val result:Int = "dc_shell -f zonghe.tcl"!
	
		
		
	}
}	

def run():Unit = {
	

 

	
}


def dc_shell_synthesis_script(
	target_library : String = "/nfs/project/JayMok/power_experiments_xie/fab/t40lp/sc/tcbn40lpbwp/nldm/tcbn40lpbwptc.db",
	module : String = "SimpleAdder2",
	root : String = "generated",

        module_out_name : String = "SimpleAdder2",

	cap_load : Double = 10,
	fanout_load: Double = 0.1,

	input_transition: Double = 0.5,
	max_transition: Double = 0.6,
	max_clock_delay : Double= 1.2,
	min_clock_delay: Double = 1.2,
	min_data_delay : Double= 1.2,
	max_data_delay: Double = 1.2

	):Unit = {


	val writer = new PrintWriter(new File("zonghe.tcl" ))

	val tcl = s"""define_design_lib work -path ./work
	set_host_options -max_cores 8
	set verilogout_no_tri true
	set OUTPUTS_DIR ./syn
	analyze -format verilog [list ${root}/${module_out_name}/${module}.v ]
	set_app_var target_library [list ${target_library}]
	set_app_var link_library [list ${target_library}]
	elaborate ${module}
	link
	check_design
	set_wire_load_mode top
	set_fix_multiple_port_nets -all -buffer_constants -feedthroughs
	set_fanout_load ${fanout_load} [all_outputs]
	set_input_transition ${input_transition} [all_inputs]
	set_load ${cap_load} [all_outputs]
	set_max_transition ${max_transition} [current_design]
	set max_clock_delay ${max_clock_delay}
	set min_clock_delay ${min_clock_delay}
	set max_data_delay ${max_data_delay}
	set min_data_delay ${min_data_delay}

	set_app_var compile_clock_gating_through_hierarchy true
	set_app_var power_cg_balance_stages true
	set_clock_gating_style -sequential_cell latch\\
	                   -positive_edge_logic integrated\\
	                   -control_point before\\
	                   -num_stages 2
	uniquify
	compile_ultra -no_autoungroup -gate_clock
	change_name -rule verilog -hier
	check_timing
	report_area -hier -nosplit > ./${root}/${module_out_name}/${module}.area
	report_qor 
	report_constraint -all_violators 
	report_reference -hier -nosplit 
	report_timing -delay max -max_paths 5 > ./${root}/${module_out_name}/${module}.max.timing 
	report_timing -delay min -max_paths 5 > ./${root}/${module_out_name}/${module}.min.timing 

	report_power -hier > ./${root}/${module_out_name}/${module}.hier.pwr 
	report_power > ./${root}/${module_out_name}/${module}.avg.pwr 
	report_clock
	report_clock_gating
	write_file -f verilog -hier -o ./${root}/${module_out_name}/${module}.syn.v
	write_sdc ./${root}/${module_out_name}/${module}.syn.sdc
	exit"""
	

	writer.write(tcl)

	writer.close()

}

}
