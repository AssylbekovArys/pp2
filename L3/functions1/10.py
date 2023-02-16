def unique(nums):
    res = dict()
    for item in nums:
        res[item] = 0
    for item in nums:
        res[item] += 1
    output = []
    for key,value in res.items():
        if value == 1:
            output.append(key)
    return output

n=[int(i) for i in input().split()]
print(unique(n))