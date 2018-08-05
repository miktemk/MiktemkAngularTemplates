import sys, os, shutil, random
from datetime import datetime  
from datetime import timedelta  

dateStr = '2018-07-30T12:40:21Z'

# are there other ways to parse date string?
dateObj = datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%SZ")
print(dateObj)

# how can i assign custom time? e.g. 13:45 ==> 2018-07-30T13:45:00Z
dateAlt = dateObj.date()
#dateAlt = datetime.combine(dateObj.date(), datetime.time(10, 30))

print(dateAlt)
