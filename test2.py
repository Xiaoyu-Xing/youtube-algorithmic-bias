def square(i):
	return i*i 

def fib(i):
	if i == 0:
		return 0
	if i == 1:
		return 1
	else:
		return fib(i - 1) + fib(i - 2)
def main():
	for i in range(35):
		print(fib(i))


if __name__ == '__main__':
	main()