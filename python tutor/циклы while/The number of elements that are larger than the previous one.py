b = 1
i = 0
u = 1000000000000
while b != 0:
    b = int(input())
    if u < b:
        i+=1
    u = b
print (i)