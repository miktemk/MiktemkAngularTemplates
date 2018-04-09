import sublime, sublime_plugin

class LinefyCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			if not region.empty():
				text = self.view.substr(region)
				text = text.replace("\r\n", "")
				text = text.replace("\n\r", "")
				text = text.replace("\n", "")
				while "  " in text:
					text = text.replace("  ", " ")
				text = text.replace(" ,", ", ")
				self.view.replace(edit, region, text)
		# .... debug test to see if it even runs
		#allLength = self.view.size()
		#self.view.insert(edit, allLength, "test")
