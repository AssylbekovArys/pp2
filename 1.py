"""
x = int(input())
for z in range(1, x + 1):
    for y in range (1, z + 1):
        print (y, sep='',end='')
    print()
"""
import math

num = int(input())
sqrt = math.sqrt(num)
print("The square root of", num, "is", sqrt)