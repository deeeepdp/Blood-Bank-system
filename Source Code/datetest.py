# import datetime
# fromdatetime = datetime.datetime.now()
# todatetime = datetime.datetime.now()
# date = todatetime-fromdatetime
# print(date)

import datetime
datee="2022-09-28T16:38"
datee = datee.replace('T', ' ')
datee = datetime.datetime.strptime(datee, "%Y-%m-%d %H:%M")
print(datee)
days = datetime.datetime.now() - datee

print(days.days)