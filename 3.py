class Person:
    def __init__(self,name, nationality):
        self.person_nationality = nationality
        self.person_name = name
    
    def printInfo(self):
        print(self.person_nationality, self.person_name)
    
    def setType(self, surname):
        self.person_surname = surname
    
    def getType(self):
        print (self.person_surname)

class student (Person):
    def __init__(self, name, nationality, id):
        self.person_id = id
        Person.__init__(self, name, nationality)
    
    def printInfo0 (self):
        print (self.person_name, self.person_nationality, self.person_id)

class teacher (Person):
    def __init__(self, name, nationality, id):
        self.teacher_id = id
        Person.__init__(self, name, nationality)
    
    def printInfo1(self):
        print (self.person_name, self.person_nationality, self.teacher_id)

obj = Person("Arystan", "kazakh")
obj.printInfo()
obj.setType("Assylbekov")
obj.getType()

obj1 = student ("Arystan", "kazakh", "22B030150")
obj1.printInfo0()

obj2 = teacher ("Arystan", "kazakh", "22B030150")
obj2.printInfo1()