# **MODE OF USE**: just execute

############ config ############

################################

import sys, os, shutil, random, re
import __main__
import getopt
from datetime import datetime  
from datetime import timedelta  
import subprocess

# command line options: note the first line parameter and the if statements below
# optlist, args = getopt.getopt(sys.argv[1:], "")
# if len(args) <= 0:
# 	print("Usage: must supply last commit date as first arg")
# 	exit(1)
# lastDate = args[0]


def parse_iso8601(sss):
	# LINK: https://regex101.com/r/Xz0oia/1
	sss = re.sub(r"(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d-\d\d):(\d\d)", "\\1\\2", sss)
	parsed = datetime.strptime(sss, '%Y-%m-%dT%H:%M:%S%z')
	return parsed

def getLastGitCommitDateIso8601Str():
	#test = subprocess.Popen('git log -1 --format="%at" | xargs -I{} date -d @{} "+%Y-%m-%dT%H:%M:%SZ"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	gitlogLastDate = subprocess.Popen('git log -1 --format="%aI"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	gitlogLastDate_out, gitlogLastDate_err = gitlogLastDate.communicate()
	# print(gitlogLastDate_out.strip())
	# print(gitlogLastDate_err)
	if len(gitlogLastDate_err) > 0:
		print('Error getting last commit date:')
		print(gitlogLastDate_err.decode("utf-8").strip())
		sys.exit(1)
	return gitlogLastDate_out.decode("utf-8").strip()

random.seed()

lastDateStr = getLastGitCommitDateIso8601Str()
if lastDateStr == '':
	lastDateStr = '2018-07-29T14:16:13-04:00'
lastDateObj = parse_iso8601(lastDateStr)
print('Last date:', lastDateObj)

newDateObj = lastDateObj + timedelta(minutes=random.randrange(30) + 20, seconds=random.randrange(59) + 1)
print('New date: ', newDateObj)

# lastSaturday1030am = lastDateObj.replace(hour=10, minute=30) - timedelta(days=lastDateObj.weekday()) - timedelta(days=2)
# print('lastSaturday1030am', lastSaturday1030am)

# OPTION 1: commit message will be "wip"
#cmdStr = "git commit --date \"" + newDateObj.isoformat() + "\" -m \"wip\"" 
# OPTION 2: commit message will be from Git Extensions
cmdStr = "git commit --date \"" + newDateObj.isoformat() + "\" -F \".git\\COMMITMESSAGE\"" 
print('Command:  ', cmdStr)

#cmdStr = "git status"
subprocess.Popen(cmdStr)
