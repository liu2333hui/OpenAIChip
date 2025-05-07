def toggle(dummy):
	prev1 = 0
	toggle1 = []
	for i in dummy:
		toggle1.append( bin( i ^  prev1  ).count('1'))
		prev1 = i
	return toggle1

def bitzero(A):
	bits = []
	for i in A:
		bits.append(bin(i).count("1"))
	return bits

def zeros(A):
	arr = A
	count = 0
	for num in arr:
		if num == 0:
		        count += 1	
	return count/len(A)
	return sum([a for a in A if a == 0])/len(A)

from toggle import gen_in	

if __name__ == "__main__":
	#A = [i for i in range(100)]
	set_bit_zero = 5
	set_sparse = 0.1
	A = gen_in(sparsity=set_sparse,bit_zero = set_bit_zero, prec=8, N = 100)

	B = [j for j in range(100)]

	sparse = zeros(A)

	bits1 = bitzero(A)
	print(A)
	print(set_bit_zero)
	print("meta",bits1, sparse)
	bits1 = int(sum(bits1)/len(bits1))+1
	print("meta",bits1, sparse)
	print((8-bits1))	
	bits1 = 8 - bits1*2
	bits2 = 0
	

	#like arch
	toggle1 = []
	toggle2 = []
	prev1 = 0
	prev2 = 0
	REUSE = 1
	K = 100000
	for n in range(K):
		for i in range(len(A)):
			for j in range(REUSE):
				data1 = A[i]
				data2 = B[j]			
				toggle1.append( bin( data1 ^  prev1  ).count('1'))
				prev1 = data1

	#like software
	s1 = []
	for n in range(10):
		dummy1 = gen_in(sparsity=sparse,bit_zero = bits1, prec=8, N = 1000, REUSE = REUSE)
		s1.append(sum(toggle(dummy1))/len(dummy1))
	
		#print(software1)
		#print(toggle1)
	print(s1)
	software1 = [sum(s1)/len(s1)]	
	print(sum(toggle1)/len(toggle1), 0.9*sum(software1)/len(software1))
