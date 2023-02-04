a = str(input())
n = 0
i = 0
while i < len(a):
    if a[i] == ' ':
        n += 1
    i += 1
print (n + 1)