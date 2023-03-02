import math

n = 4
a = 25
s = ((n * math.pow(a, 2)) / 4) * (1/math.tan((180/n) * (math.pi/180)))
print ("Input number of sides:", n)
print ("Input the length of a side:", a)
print ("The area of the polygon is:", math.floor(s))