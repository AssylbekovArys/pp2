def multi (ls):
    n = 1
    for x in ls:
        n *= x
    return n

lis = [2, 3, 4, 5]
print (multi(lis))