import re

file = open ('C:/Users/acer/Desktop/git lessin/L5/lab work/row.txt', 'r', encoding='UTF8')
result = re.sub(r'[ ,.]',':', file.read())
print(result)