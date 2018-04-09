# Hекоторые cлова мужского

import sublime
import sublime_plugin
import re


# USAGE: { "keys": [ "ctrl+alt+l" ], "command": "find_latinica_errors" },
#        view.run_command("find_latinica_errors")
class FindLatinicaErrorsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sel = self.view.sel()
		if len(sel) == 0:
			return
		# .... get all text past the cursor
		cursorPos = sel[0].a
		regionAll = sublime.Region(0, self.view.size())
		text2 = self.view.substr(regionAll)
		# .... https://regex101.com/r/Du2Bav/1
		regexFindOddLetter = re.compile(u'([\u0430-\u044F\u0410-\u042F])')
		# sel.clear()
		if regexFindOddLetter.match(text2) == None:
			print("no match")
		for mo in regexFindOddLetter.finditer(text2):
			position = mo.start(1)
			# sel.add(sublime.Region(position, position+1))
			# print ('match!', position)
			if position > cursorPos:
				sel.clear()
				sel.add(sublime.Region(position, position+1))
				print ('cursor to', position)
				return
		
		ru = u"Владивостокq находится на одной широте с Сочи, однако имеет среднегодовую температуру почти на 10 градусов ниже."
		en = u"Vladivostok (Russian: Владивосток; IPA: [vlədʲɪvɐˈstok] ( listen); Chinese: 海參崴; pinyin: Hǎishēnwǎi) is a city and the administrative center of Primorsky Krai, Russia"

		cyril1 = re.findall(u"[\u0400-\u0500][a-zA-Z]", en)
		cyril2 = re.findall(u"[\u0400-\u0500]", ru)

		for x in cyril1:
		    print (x)

		for x in cyril2:
		    print (x)


