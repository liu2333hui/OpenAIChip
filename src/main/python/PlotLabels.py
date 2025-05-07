if __name__ == "__main__":
	xi =  "generated/Arch/SparseConv/analyzed_04_03"
	head = xi+".head.txt"
	tail = xi+".tail.txt"
	
	import pandas as pd

	header = pd.read_csv(head, header=None,delimiter="\t")
	#print(header)
	columns = header.iloc[0].tolist()

	data = pd.read_csv(tail, header=None,delimiter="\t")

	data.columns = columns

	#print(data.head())
	print(data)
	
	import matplotlib.pyplot as plt
	plt.scatter(data['golden_total'], data['golden_total'])
	plt.show()
