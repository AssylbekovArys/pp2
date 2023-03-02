def even(n):
    for x in range(0, n + 1, 2):
        yield x

num = even(int(input()))
print(",".join(str (x) for x in num ))