import math

class Point:
    def __init__(self, x , y):
        self.x=x
        self.y=y
    def show(self):
        print(self.x, self.y)
    def move(self, x1, y2):
        self.x1=x1
        self.y2=y2
        return(self.x, self.y)
    def dis(self):
        return math.sqrt((self.x)**2+(self.y)**2)

a=Point(int(input()), int(input()))
print(Point.show(a))
b=Point.dis(a)
print(b)
a=Point.move(a,int(input()), int(input()))
Point.show(a)