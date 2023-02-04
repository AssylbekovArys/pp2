s = str(input())
n = 0
for x in s:
    if n % 3 != 0:
        print(x, sep='',end='')
    n += 1