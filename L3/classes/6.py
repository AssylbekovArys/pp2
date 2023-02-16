def prime(num):
    if num == 1:
        return True
    for i in range(2, int(num**.05)+1):
        if num % i == 0:
            return False
    return True
my_list = [1,3, 6]

b = filter(lambda x: prime(x), my_list)
print(list(b))