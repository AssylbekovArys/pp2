def check(s):
    up = 0
    low = 0
    for x in s:
        if x.islower():
            low += 1
        elif x.isupper():
            up += 1
    print ('lower:', low)
    print ('upper:', up)
s = 'Hello, world'
check(s)