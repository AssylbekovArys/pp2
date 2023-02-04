z = int (input ())
y = int (input ())
if z < y:
    for x in range(z, y + 1):
        print (x)
else:
    for x in range(z, y - 1, -1):
        print (x)