My own plugins
==============

To write a plugin go `Tools` -> `New Plugin`.

#### contabilita

Wrote Sublime Text plugin `contabilita` to calculate total by adding double numbers at the end of each line. Find it here `C:\Users\Mikhail\AppData\Roaming\Sublime Text 3\Packages\contabilita`. If a line does not end in a number, it is skipped. If a line begins with # it is also skipped:

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

Invoke in console by `view.run_command('contabilita')`. Note that the class is called `ContabilitaCommand`, so the invokation name is without the `Command` suffix and lowercase first letter.

#### CamelCaseToSpaces

Wrote Sublime text plugin to convert CamelCase into space-separated words. The [API documentation](https://www.sublimetext.com/docs/3/api_reference.html) sux. Here is the code:

	import sublime, sublime_plugin
	import re
	class CamelCaseToSpacesCommand(sublime_plugin.TextCommand):
		def run(self, edit):
			for region in self.view.sel():
				if not region.empty():
					text = self.view.substr(region)
					text = re.sub("([a-z])([A-Z])","\g<1> \g<2>", text)
					self.view.replace(edit, region, text)

MMkay? In order to use it, you need to create a shortcut:

	{ "keys": [ "ctrl+alt+c", "ctrl+alt+c" ], "command": "camel_case_to_spaces" },

Ctrl + Alt + Sissy!

#### Chew my text

Modify this plugin as you wish. I used it to format the `%PATH%` environment variable from `cmd`. It is located here: `C:\Users\Mikhail\AppData\Roaming\Sublime Text 3\Packages\User`.

	import sublime, sublime_plugin
	import re
	class ChewMyTextCommand(sublime_plugin.TextCommand):
	    def run(self, edit):
	        for region in self.view.sel():
	            if not region.empty():
	                text = self.view.substr(region)
	                text = text.replace("\n", "") #.... Format PATH from Commnad Prompt
	                text = text.replace(";", "\n")
	                self.view.replace(edit, region, text)

shortcut is `Ctrl` + `Shift` + `C` + `V`:

	{ "keys": [ "ctrl+shift+c", "ctrl+shift+v" ], "command": "chew_my_text" },

### Other commands

 - `view.run_command('linefy')` - puts everything in 1 line, separated by 1 space