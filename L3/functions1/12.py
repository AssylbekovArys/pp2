def histogram(list):
        for x in range(0,len(list)):
                print('*' * list[x])
        return
a=[int(x) for x in input().split()]
histogram(a)
