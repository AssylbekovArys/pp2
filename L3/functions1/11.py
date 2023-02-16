def pal(s):
    if s==s[::-1]:
        return True
    else:
        return False

s=str(input())
print(pal(s))