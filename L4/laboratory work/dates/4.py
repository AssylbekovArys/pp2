import datetime

x = datetime.datetime.now()
y = datetime.datetime(2022, 10, 20, 10, 10, 10)
z = x - y
print (z.seconds)