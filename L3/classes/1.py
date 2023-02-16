class string:
    def __init__(self, string):
        self.string = string

    def getString(self):
        return self.string

    def printString(self):
        self.string = self.string.upper()
        return self.string


s = string(input())
a = s.getString()
print(a)
b = s.printString()
print(b)