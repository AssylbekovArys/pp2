s = str(input())
i = -1
for x in s:
    i += 1
    if s.find('h') <= i <= s.rfind('h'):
        continue
    print(x, sep='',end='')
    