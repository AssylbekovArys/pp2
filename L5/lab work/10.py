import re

file = open ('C:/Users/acer/Desktop/git lessin/L5/lab work/row.txt', 'r', encoding='UTF8')
result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', file.read()).lower()
print(result)