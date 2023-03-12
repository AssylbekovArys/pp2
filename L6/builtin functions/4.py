import time
import math

def square(mil, n):
    time.sleep(mil/1000)
    return math.sqrt(n)

n = 25100
mil = 2123
print(square(mil,n))