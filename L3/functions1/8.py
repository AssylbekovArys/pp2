def game(nums):
    res = []
    for iter in nums:
        if iter == 0 or iter == 7:
            res.append(iter)
    for i in range(len(res)-2):
        if res[i] == 0 and res[i+1] == 0 and res[i+2] == 7:
            return True
    return False

n=[int(i) for i in input().split()]
print(game(n))