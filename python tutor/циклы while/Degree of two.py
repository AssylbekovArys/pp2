n = int(input())
d = 0
while 2 ** d <= n:
    d += 1
print (d - 1, 2 ** (d - 1))