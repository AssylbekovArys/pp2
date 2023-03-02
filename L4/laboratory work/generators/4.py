def sqrt(a, b):
    for x in range (a, b + 1):
        yield x ** 2

for x in sqrt(int(input()), int(input())):
    print (x)