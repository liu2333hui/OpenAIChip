package tester

import java.time.LocalTime

import java.io.IOException

import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import sys.process._

import eda._
import java.nio.file.{Files, Paths, StandardCopyOption}
import java.io.File

import java.nio.charset.StandardCharsets
import java.nio.file.StandardOpenOption
 
import scala.collection.mutable.ArrayBuffer


abstract class TraceTester{
	
}

/*
   Perform a test based on given hardware map, runtime map, and test vector map
   Where the test vector map is an array of Array[Int] of the testing vectors, 
      i.e.
	      Map(("input1", Array(   Array(0, 1, 2),   Array(0, 3, 5) ...   )),
			  ("input2", Array(   Array(5, 6, 6),   Array(1, 7, 9) ...   ))
	      )
	Use this to generate the training data
*/
abstract class FullTester{
	
	//Override with the test to run
	def driver()
	// HardwareConfig: Map[String,String], 
			// TestVector : Map[String, Array[Int]], N : Int, CLOCK: Int,SpecName:String) 
	
	
	var TargetDir:String = ""
    var SpecName : String = ""
	var HardwareConfig : Map[String, String] = Map()
	var TestVector: Map[String, Array[Int]] = Map()
	var N : Int = 500
	var CLOCK : Int = 1
	var currentTime = System.currentTimeMillis() //LocalTime.now()
	
			
	def run(HardwareMap:Map[String,Array[_ >: String with Boolean with Int with Double]], 
			RuntimeMap:Map[String,Array[_ >: String with Boolean with Int with Double]], 
			TestVectorMap:Map[String,Array[Array[Int]]],
			N :Int,
			ModuleName: String,
			TestName: String,
			SpecName: String,
			EDAVerification: Boolean,
			SkipSimulation:Boolean = false,
			ForceSynthesis:Boolean = false,
			RenameVcd:Boolean = true,
			OutputPowerFile:String = "",
			DontSaveInput:Boolean = false,
			CustomMap:Map[String,String] = Map()
			) = {
				


				
	        val root:String = "generated/"+ModuleName	
				
			var outputFile = root+"/"+ s"${currentTime}.txt"
			if(OutputPowerFile == ""){
				
			}else{
				outputFile = OutputPowerFile
			}
								
							
		var TestNum = 1
		for(k <- TestVectorMap.keys){
			TestNum = TestVectorMap(k).length
		}
				
		var idx :Int= 0
		var RuntimeKeyIndex:Map[String, Int] = Map()
		for (k <- RuntimeMap.keys){
			// RuntimeKeyIndex(k) = idx
			RuntimeKeyIndex = RuntimeKeyIndex + (k -> idx)
			idx  = idx + 1
		}
				
               val HardwareKeys = ArrayBuffer[String]()
               for( k <- HardwareMap.keys){
                   HardwareKeys += k 
               }
               val RuntimeKeys = ArrayBuffer[String]()
               for( k <- RuntimeMap.keys){
                   RuntimeKeys += k 
               }
               val TestingKeys = ArrayBuffer[String]()
                for( k <- TestVectorMap.keys){
                   TestingKeys += k 
               }
  


               var head =  HardwareKeys.reduce(_+"\t"+_) + "\t" + RuntimeKeys.reduce(_+"\t"+_)+"\t"+ TestingKeys.reduce(_+"\t"+_) + "\t"+ Array("Internal_Pwr", "Switch_Pwr", "Leak_Pwr", "Total_Pwr").reduce(_+"\t"+_)+"\t"+ "cycles" +"\t"+ "N" + "\n"

		if(DontSaveInput){
			head =  HardwareKeys.reduce(_+"\t"+_) + "\t" + RuntimeKeys.reduce(_+"\t"+_)+"\t"+ Array("Internal_Pwr", "Switch_Pwr", "Leak_Pwr", "Total_Pwr").reduce(_+"\t"+_)+"\t"+ "cycles" +"\t"+ "N" + "\n"
		}	
 
 
		//try {
		    val filePath = Paths.get(outputFile);
		    Files.createDirectories(filePath.getParent()); // 确保父目录存在
		//} catch (e) {
		  //  e.printStackTrace();
		//}

               Files.write(Paths.get(outputFile ), head.getBytes(StandardCharsets.UTF_8), StandardOpenOption.CREATE)
	
		if(! SkipSimulation){
		for (combo <- Helper.GenCombo(HardwareMap) ){
			for ( soft <- Helper.GenCombo(RuntimeMap) ){
				for (test <- 0 until TestNum)  {
					//Helper.PrintTest(combo, soft, test)
					
					val hardware = ModuleName + "_" + combo.reduce(_+"_"+_)
					val runtime = soft.reduce(_+"_"+_)
					
					val module_out_name = hardware + "__" + runtime
					
					val testbench = TestName + "_" + test
					println(module_out_name +"\t"+ testbench)
			
					var hardware_config:Map[String, String] = Map()
					var index = 0
					for (k <- HardwareMap.keys)  {
						hardware_config = hardware_config + (k -> combo(index))
						index = index + 1
					}
					
					val spec = s"${ModuleName}Spec"
					var test_vector : Map[String, Array[Int]] = Map()
					for (k <- TestVectorMap.keys){
						// TestVector(k) = 
						test_vector = test_vector + (k -> TestVectorMap(k)(test))
					}
					
					var runtime_config:Map[String, String] = Map()
					index = 0
					for (k <- RuntimeMap.keys)  {
						runtime_config = runtime_config + (k -> soft(index))
						index = index + 1
					}
			
					//Final minute changes
					//Useful for hetereogenous units
					//Where in_1 --> constant, for example
					for (mmm <- CustomMap.keys){
						//println(mmm)
						hardware_config = hardware_config + (CustomMap(mmm) -> (test_vector(mmm))(0).toString )
					}
			
					// val D = runtime(RuntimeKeyIndex("CLOCK"))
					val D = runtime_config("CLOCK").toInt
					val tech = hardware_config("tech")
					val cap_load =    runtime_config("cap_load").toDouble
					val fanout_load = runtime_config("fanout_load").toDouble
					val target_library = 	TechNode.get(tech)	
		
		
				   	
				   	this.TargetDir = s"generated/${ModuleName}/${module_out_name}"
				    this.SpecName = SpecName
				   	this.HardwareConfig = hardware_config
				   	this.TestVector = test_vector
				    this.N = N
				   	this.CLOCK = D
					this.driver()//hardware_config, TestVector, N, D,SpecName)
					
					
					//rename the .vcd into another name, related with testbench

						
						val files = (new File(s"${TargetDir}")).listFiles()
						// 查找当前目录中的 .v 文件
						val found = files.filter(_.getName.endsWith(".v"))
						// println(s"找到文件: ${file.getAbsolutePath}")
						// println(found(0))
						// val TopName = 
						
						val TopName = (found(0)+"").split("/").last.split("\\.").head
					if(RenameVcd){
						//Code from AI DeepSeekV3
						
						//val files = (new File(s"${TargetDir}")).listFiles()
						// 查找当前目录中的 .v 文件
						//val found = files.filter(_.getName.endsWith(".v"))
						// println(s"找到文件: ${file.getAbsolutePath}")
						// println(found(0))
						// val TopName = 
						
						val oldfile =found(0)+"cd" //s"${TargetDir}/${ModuleName}.vcd"
						val newfile = s"${TargetDir}/${testbench}.vcd"
						val sourcePath = Paths.get(oldfile)
						val targetPath = Paths.get(newfile)
						// 重命名文件（如果目标文件已存在，则覆盖）
						Files.move(sourcePath, targetPath, StandardCopyOption.REPLACE_EXISTING)
						println(s"$sourcePath -> $targetPath")
					}
					
   				   if(EDAVerification){
						//Run power post analysis
						//(todos) need to re-test
					   synthesis.dc_shell_synthesis_script(target_library=target_library,root=root,
					   module=TopName, cap_load=cap_load,fanout_load=fanout_load, module_out_name=module_out_name)
					   synthesis.run(root=root,module=TopName, module_out_name=module_out_name, force=ForceSynthesis)
						power.ptpx_script(root=root,target_library=target_library,
							module=TopName, module_out_name=module_out_name, cap_load=cap_load, 
							fanout_load=fanout_load, testbench=testbench)
						power.run(module=TopName, root=root, module_out_name=module_out_name,
							testbench=testbench)//, module_out_name=module_out_name)
					val report:String = power.ptpx_script(root=root,target_library=TechNode.get(tech),module=TopName, module_out_name=module_out_name, cap_load=cap_load, fanout_load=fanout_load, testbench=testbench)
	
                                                
			         	val avg_power = power.get_average_power(report)
                                        val cycles = power.get_total_cycles( root+"/"+module_out_name+"/"+ testbench+".vcd" )

                                      val vectors = TestingKeys.map(k => test_vector(k).mkString(",")).reduce(_+"\t"+_) 



		  	               var body =  HardwareKeys.map(k => hardware_config(k)).reduce(_+"\t"+_) + "\t" + RuntimeKeys.map(k => runtime_config(k) ).reduce(_+"\t"+_)+"\t"+vectors + "\t"+ avg_power.mkString("\t")+"\t"  + cycles +"\t"+ N+  "\n"
					if(DontSaveInput){
		  	               		 body =  HardwareKeys.map(k => hardware_config(k)).reduce(_+"\t"+_) + "\t" + RuntimeKeys.map(k => runtime_config(k) ).reduce(_+"\t"+_)+ "\t"+ avg_power.mkString("\t")+"\t"  + cycles +"\t"+ N+  "\n"
	
					}
 
	
                                        Files.write(Paths.get(outputFile) , body.getBytes(StandardCharsets.UTF_8), StandardOpenOption.APPEND)
	

					}
					
				}	
			}
		}
		}
		
		
		if(EDAVerification){
			
		for (combo <- Helper.GenCombo(HardwareMap) ){
			for ( soft <- Helper.GenCombo(RuntimeMap) ){
				for (test <- 0 until TestNum)  {
					//Helper.PrintTest(combo, soft, test)
					
					val hardware = ModuleName + "_" + combo.reduce(_+"_"+_)
					val runtime = soft.reduce(_+"_"+_)
					
					val module_out_name = hardware + "__" + runtime
					
					val testbench = TestName + "_" + test
					println(module_out_name +"\t"+ testbench)
			
					val D = runtime(RuntimeKeyIndex("CLOCK"))
					
					var hardware_config:Map[String, String] = Map()
					var index = 0
					for (k <- HardwareMap.keys)  {
						hardware_config = hardware_config + (k -> combo(index))
						index = index + 1
					}
					
					var runtime_config:Map[String, String] = Map()
					index = 0
					for (k <- RuntimeMap.keys)  {
						runtime_config = runtime_config + (k -> soft(index))
						index = index + 1
					}
					
					
					val spec = s"${ModuleName}Spec"

					val tech = hardware_config("tech")
					val cap_load =    runtime_config("cap_load").toDouble
					val fanout_load = runtime_config("fanout_load").toDouble
					val target_library = 	TechNode.get(tech)	
		
		
	//rename the .vcd into another name, related with testbench
				   	this.TargetDir = s"generated/${ModuleName}/${module_out_name}"
	

						
						val files = (new File(s"${TargetDir}")).listFiles()
						// 查找当前目录中的 .v 文件
						val found = files.filter(_.getName.endsWith(".v"))
						val TopName = (found(0)+"").split("/").last.split("\\.").head
					


					val report:String = power.ptpx_script(root=root,target_library=TechNode.get(tech),module=TopName, module_out_name=module_out_name, cap_load=cap_load, fanout_load=fanout_load, testbench=testbench)
					println(module_out_name+"->" +testbench)//testbench)
					power.get_average_power(report)
					
					
				}	
			}
		}
		}
		
		
	} //end run
	
}
