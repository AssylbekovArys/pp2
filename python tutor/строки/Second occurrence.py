s = str(input())
n = s.count('f')
if n >= 2:
    print (s.find('f', s.find('f') + 1))
elif n == 1:
    print(-1)
else:
    print(-2)