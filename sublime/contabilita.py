import sublime, sublime_plugin
import re


class ContabilitaCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		allLength = self.view.size()
		allText = self.view.substr(sublime.Region(0, allLength))
		lines = allText.split('\n')
		total = 0
		for line in lines:
			line = line.strip()
			if line.startswith('#'):
				continue
			mo = re.match(".*?(\d*\.\d+|\d+)$", line)
			if mo != None:
				num = mo.group(1)
				#print(num)
				num = float(num)
				total += num
		self.view.insert(edit, allLength, "# TOTAL: " + ("%.2f" % total) + "\n")