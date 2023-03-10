def reverse(str, start, end):
	temp = ''
	str1 = ""

	while (start <= end):
		temp = str[start]
		str[start] = str[end]
		str[end] = temp
		start+=1
		end-=1
	return str1.join(str)

def reverseWords(s):
	
	word_begin = -1

	i = 0

	while (i < len(s)):

		''' This condition is to make sure that the
				string start with valid character (not
				space) only '''
		if ((word_begin == -1) and (s[i] != ' ')):
			word_begin = i
		if (word_begin != -1 and ((i + 1 == len(s)) or (s[i + 1] == ' '))):
			s = reverse(list(s), word_begin, i)
			word_begin = -1
		i+=1
	''' End of while '''

	s = reverse(list(s), 0, (len(s) - 1))
	return s

s = "i like this program very much"

p = reverseWords(list(s))
print(p)

