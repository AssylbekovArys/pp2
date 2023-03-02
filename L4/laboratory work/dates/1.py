import datetime

now_date = datetime.date.today()
five_day = now_date - datetime.timedelta(days=5)

print(five_day)