a = int(input())
sum = 0
f = 1
for x in range (1, a + 1):
    f *= x
    sum += f
print(sum)