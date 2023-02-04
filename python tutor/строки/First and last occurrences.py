s = str(input())
if s.find('f') != s.rfind('f'):
    print(s.find('f'))
    print(s.rfind('f'))
elif 'f' in s:
    print(s.find('f'))
else:
    print()