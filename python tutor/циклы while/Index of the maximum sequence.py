b = 1
max = 0
i = 0
maxi = 0
while b != 0:
    b = int(input())
    if b > max:
        max = b
        maxi = i
    i += 1
print (maxi)