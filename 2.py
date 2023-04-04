"""
a = '''Lorem Ipsum is simply dummy text of the printing and typesetting industry. 
Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, 
when an unknown printer took a galley of type and scrambled it to make a type specimen book. 
It has survived not only five centuries, but also the leap into electronic typesetting, remaining
essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing 
Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.'''
x = a.rsplit(" ")
x.reverse()
#print (x)
print(x[::3])
"""
import re

text = "hello my abbd hey ey ab"
pattern = r'[aA][bB]' # ab => bc
# r = removes all /

text = re.sub(pattern, 'bc', text) #it changes the pattern where 'a' and 'b' steps it an oreder

with open('data.txt', mode='w', encoding = 'UTF') as f:
    f.write(text)