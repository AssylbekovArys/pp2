import re

file = open ('C:/Users/acer/Desktop/git lessin/L5/lab work/row.txt', 'r', encoding='UTF8')
result = re.findall(r".*a.*b.*b.*|.*a.*b.*b.*b.*", file.read())
#result = re.findall(".*a.{2}b.*", file.read())
print(result)