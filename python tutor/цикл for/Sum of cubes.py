a = int(input())
sum = 0
for x in range(a + 1):
    b = 1
    for y in range(3):
        b *= x
    sum += b
print (sum)