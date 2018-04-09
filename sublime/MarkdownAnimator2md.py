import sublime, sublime_plugin
import re

# .... to run in console: view.run_command('markdown_animator2md')
class MarkdownAnimator2mdCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# .... removes the animated markup and tts russian swearing
		regexBlock = re.compile(r"\[r?`.*?`\] ?") # .... [`var`], [`var1`,`var2`], [r`regex`]
		regexTts = re.compile(r"<tts.*?<\/tts> ?") # .... <tts lang="ru">suka</tts>
		regexHL = re.compile(r"<md-highlight lines=\".*?\" \/> ?") # .... <md-highlight lines="2,3" />

		allLength = self.view.size()
		regionAll = sublime.Region(0, allLength)
		text = self.view.substr(regionAll)
		text = regexBlock.sub("", text)
		text = regexTts.sub("", text)
		text = regexHL.sub("", text)
		self.view.replace(edit, regionAll, text)