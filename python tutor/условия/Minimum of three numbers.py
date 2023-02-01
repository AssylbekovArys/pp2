x = int(input())
y = int(input())
z = int(input())
if x > y:
    if y > z:
        print(z)
    else:
        print(y)
else:
    if x > z:
        print(z)
    else:
        print(x)