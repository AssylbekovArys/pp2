def check(s):
    s = s.replace(' ','').lower()
    r = s[::-1]
    if s == r:
        print('It is palindrome')
    else:
        print('It is not palindrome')
s = 'Babab'
check(s)