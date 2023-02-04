s = input()  
print(s[:s.find('h')] + s[s.find('h'):s.rfind('h')+1][::-1] + s[s.rfind('h')+1:])
