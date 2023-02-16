class Shape:
    def __init__(self, length):
            self.length = length
    class Square:
        def _init_(self, side):
            self.side=side
    def area(self):
        return self.length*self.length
    
a=Shape(int(input()))
b=Shape.area(a)
print(b)