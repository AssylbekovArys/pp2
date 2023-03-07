import re

file = open ('C:/Users/acer/Desktop/git lessin/L5/lab work/row.txt', 'r', encoding='UTF8')
result = re.findall(r'[a-z]+|[A-Z][a-z]*', file.read())
print(result)