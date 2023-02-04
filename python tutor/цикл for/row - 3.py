z = int (input ())
y = int (input ())
for x in range(z, y - 1, -1):
    if x % 2 != 0:
        print (x)