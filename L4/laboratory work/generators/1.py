def square(n):
    for x in range (1, n + 1):
        yield x ** 2

for x in square(int(input())):
    print (x)