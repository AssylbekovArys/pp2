def div(n):
    for x in range (0, n + 1):
        if x % 4 == 0 and x % 3 == 0:
            yield x

for x in div(int(input())):
    print (x)