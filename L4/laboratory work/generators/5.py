def down(n):
    while n >= 0:
        yield n
        n -= 1

for x in down(int(input())):
    print (x)