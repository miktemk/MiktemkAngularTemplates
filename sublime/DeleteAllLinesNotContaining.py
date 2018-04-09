import sublime
import sublime_plugin
import re

# view.run_command("delete_all_lines_not_containing")
class DeleteAllLinesNotContainingCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sel = self.view.sel()
		if len(sel) == 0:
			return
		# .... get all text past the cursor
		sel1 = sel[0]
		if sel1.a == sel1.b:
			return
		matchingRegions = self.view.find_all(self.view.substr(sel1), sublime.LITERAL)
		allLines = self.view.lines(sublime.Region(0, self.view.size()))
		for lineRegion in reversed(allLines):
			if self.findFirstRegionInLine(matchingRegions, lineRegion) == None:
				self.view.replace(edit, lineRegion, '')
		# .... remove empty lines
		emptyNewlines = self.view.find_all('^\\n') # NOTE: no param = regex
		for toErase in reversed(emptyNewlines):
			self.view.replace(edit, toErase, '')
	def findFirstRegionInLine(self, regions, line):
		for region in regions:
			if line.a <= region.a and region.b <= line.b:
				return region
		return None