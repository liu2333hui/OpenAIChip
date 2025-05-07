package tester
import scala.io.Source
import scala.util.Random

object Helper{
	def transpose(array: Array[Array[Int]]): Array[Array[Int]] = {
	  // 检查数组是否为空
	  if (array.isEmpty || array(0).isEmpty) {
	    return Array.empty[Array[Int]]
	  }
	
	  // 获取行数和列数
	  val rows = array.length
	  val cols = array(0).length
	
	  // 创建转置后的数组
	  val transposed = Array.ofDim[Int](cols, rows)
	
	  // 填充转置后的数组
	  for (i <- 0 until rows; j <- 0 until cols) {
	    transposed(j)(i) = array(i)(j)
	  }
	
	  transposed
	}
	
	//AI-generated helpers
	def readFileTo2DArrayWithPadding(filePath: String, padding: Int = 0): Array[Array[Int]] = {
	    val lines = Source.fromFile(filePath).getLines().toList
	    val maxLength = lines.map(_.split("\t").length).max

	lines.filter(_.nonEmpty).map { line =>
  val parts = line.split("\t").map(_.toInt)
  parts ++ Array.fill(maxLength - parts.length)(padding)
}.toArray	

	   // lines.map { line =>
	  //    val parts = line.split("\t").map(_.toInt)
	  //    parts ++ Array.fill(maxLength - parts.length)(padding)
	  //  }.toArray
		
	}
	
	def readFileTo2DArrayIgnoreShortLines(filePath: String): Array[Array[Int]] = {
	    val lines = Source.fromFile(filePath).getLines().toList
	    val maxLength = lines.map(_.split("\t").length).max
	
	    lines.filter(_.split("\t").length == maxLength)
	      .map(_.split("\t").map(_.toInt))
	      .toArray
	  }  
	def readFileTo2DArrayDynamic(filePath: String): Array[Array[Int]] = {
	    val lines = Source.fromFile(filePath).getLines()
	
	    lines.map(_.split("\t").map(_.toInt)).toArray
	  }
	  
	  
	  
	def processFileToMap(f:String, group:Int = 2):Map[String, Array[Array[Int]]] = {
		
		val lines = scala.io.Source.fromFile(f)
		  .getLines()
		  .map(_.trim.split("\t").map(_.toInt))
		  .toArray
		
		// 获取列数
		val numColumns = lines.head.length
		println(numColumns)
		// 2
		// 动态生成 Map[String, Array[Array[Int]]]
		var result = Map[String, Array[Array[Int]]]()
		if(group == 2){
			result = Map(
		  "in_0" -> (0 until numColumns / 2).map(col => lines.map(_(col))).toArray, // 前 3 列
		  "in_1" -> (numColumns / 2 until numColumns).map(col => lines.map(_(col))).toArray  // 后 3 列
		)
		} else if (group == 1){
			result = Map(
			  "in_0" -> (0 until numColumns).map(col => lines.map(_(col))).toArray
			)
		} else {
			//todos
		}

		
		// 结果验证
		result.foreach { case (k, v) =>
		  println(s"$k:" + v.length + ":" + v(0).length)
		  //v.foreach(arr => println(arr.mkString("Array(", ", ", ")")))
		}
		
		result
	}
	
	def PrintTest( Hardware:Array[String], Runtime: Array[String], Test: Int){
		
		for(h <- Hardware){
			print(h + ",")
		}
		print(" : ")
		for(h <- Runtime){
			print(h + ",")
		}
		print(" : ")
		println(Test +"")
		
	}
	
	def GenSimpleTrainingVectors(mode:String, p:Int, dim:Int, skip:Int = 1,
		prec:Int = 8, repeat:Int = 1, random_num:Int = 256, zero:Int = 0,
	ZeroRepeat:Int = 1,
): Map[String, Array[Array[Int]]] = {
		
		var training_map = Map[String, Array[Array[Int]]]()

		val random = new Random()
	
		for (d <- 0 until dim){	
			def gen_vectors():Array[Array[Int]] = {
				if(mode == "full"){
					(0 until math.pow(2, p).toInt by skip ).map( num => {
						//val arr = Array.fill(ZeroRepeat)(zero) :+ num

val arr = Array.tabulate(ZeroRepeat + 1) { i =>
  if (i < ZeroRepeat) 0 else num
}
						//Array.fill(repeat)(Array(zero, num)).flatten
						Array.fill(repeat)(arr).flatten

					}).toArray
				}else if(mode == "full_no_zero"){
					(0 until math.pow(2, p).toInt by skip ).map( num => {
						Array.fill(repeat)(Array( num)).flatten
					}).toArray
				}
				else if (mode == "random"){
					(0 until random_num ).map( num => {
						val randomIntInRange: Int = random.nextInt( 1<<(p)  )						
	Array.fill(repeat)(Array(zero,  randomIntInRange  )).flatten
	
					}).toArray
	
				}	
				else if (mode == "bits"){
					(0 until p by skip ).map( num => {
						//val arr = Array.fill(ZeroRepeat)(zero) :+ (1<<(num))-1

val arr = Array.tabulate(ZeroRepeat + 1) { i =>
  if (i < ZeroRepeat) 0 else (1<<(num))-1
}

						if( num==0){
						Array.fill(repeat)(Array(0, 0 )).flatten
						} else{
						Array.fill(repeat)(arr).flatten
						}
					}).toArray
				}else if (mode == "bits_no_zero"){
					(0 until p by skip ).map( num => {

						if( num==0)
						Array.fill(repeat)(Array( 0 )).flatten
						else
						Array.fill(repeat)(Array( (1<<(num)) -1)).flatten
					}).toArray
				}
				 else if (mode == "complements_full"){
				 	(0 until p by skip ).map( num => {
				 		if( num==0)
				 		Array.fill(repeat)(Array(0, 0 )).flatten
				 		else
				 		Array.fill(repeat)(Array(num, (1<<(prec)) -num)).flatten
				 	}).toArray
				 }
				 else if (mode == "complements_bits"){
				 	(0 until p by skip ).map( num => {
				 		if( num==0)
				 		Array.fill(repeat)(Array(0, 0 )).flatten
				 		else
				 		Array.fill(repeat)(Array((1<<(num)) -1, (1<<(prec)) -((1<<(num)) -1))).flatten
				 	}).toArray
				 }
				 
				 else{
                                       println("mode $mode does not exist")
                                        sys.exit(0)
					(0 to p ).map( num => {
						if( num==0)
							Array(0, 0 )
						else
							Array(0, 1<<(num-1) )
					}).toArray
				}
			}
			
			training_map = training_map + (s"in_$d" -> gen_vectors())
		}
		
		// for (i <- training_map.keys){
		// 	for (k <- training_map(i)){
		// 		 print( i+",")
		// 		for(v <- k){
		// 			print(v+",")
		// 		}
		// 		println()
		// 	}
		// }
		
		GenComboTestingVectors(training_map)
		
		
		
	}
	
	def GenComboTestingVectors(M : Map[String,Array[Array[Int]]]):
Map[String,Array[Array[Int]]] = {
		val s = M.size
		val keys = new Array[String](s)
		var i = 0
		for (k <- M.keys){
			keys(i) = k
			i = i + 1
		}
		
		val idx = new Array[Int](s)
		
		var TotalCombo = 1
		val Mu = new Array[Int](s)
		for(i <- 0 until M.size){
			Mu(i) = TotalCombo
			TotalCombo = TotalCombo*M(keys(i)).length
		}
		
		// for(i <- 0 until M.size){
		// 	println( Mu(i) )
		// }
		
		var out = Map[String, Array[Array[Int]]]()
		
		val CurIdx = new Array[Int](s)

		//((0,8), (0,16), (0,18))
		//((0,8), (0,16), (0,18))
		//-->
		//((0,8), (0,8), (0,8), (0,16), (0,16), (0,16), (0,18), (0,18), (0,18))
		//((0,8), (0,16),(0,18),...

		for(i <- 0 until s){
			var combos = Array.ofDim[ Int ](TotalCombo,  M(keys(0))(0).length )
			
			
			for(j <- 0 until TotalCombo){
				CurIdx(i) = j / Mu(i) % M(keys(i)).length
			// println(CurIdx(i) )
			
				for (k <- 0 until M(keys(0))(0).length){
					combos(j)(k) = M(keys(i))(CurIdx(i))(k)
				}
			
			}
			out = out + (keys(i) -> combos)
		}
		
		out
		
	}
	
	
	def GenCombo[A]( M : Map[String,Array[_ >: String with Boolean with Int with Double]] ) = {
		
		val s = M.size
		val keys = new Array[String](s)
		var i = 0
		for (k <- M.keys){
			keys(i) = k
			i = i + 1
		}
		
		val idx = new Array[Int](s)
		
		var TotalCombo = 1
		val Mu = new Array[Int](s)
		for(i <- 0 until M.size){
			Mu(i) = TotalCombo
			TotalCombo = TotalCombo*M(keys(i)).length
		}
		
		//println("TotalCombos", TotalCombo)
		// val combo = new Array[String with Boolean with Int](s)
		val combos = Array.ofDim[ String ](TotalCombo, s)
		val CurIdx = new Array[Int](s)
		for(j <- 0 until TotalCombo){
			for (i <- 0 until CurIdx.length){
				CurIdx(i) = j / Mu(i) % M(keys(i)).length
			}
			
			for (i <- 0 until CurIdx.length){
				for (k <- M(keys(i))){
					// print(M(keys(i))(CurIdx(i))+ "")
				}
				//combo(i) = M(keys(i))(CurIdx(i))+""
				combos(j)(i) = M(keys(i))(CurIdx(i))+""
			}
			
			// combos(j) =  combo
			
			// yield combo
			// yield CurIdx
			//println()
			
			
			//println(CurIdx.map(i => M.keys(i) ))
			//yield CurIdx.map(i => M(i))
		}
		
		combos
		
	}
}
