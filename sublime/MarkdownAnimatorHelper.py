import sublime, sublime_plugin, re

class MarkdownAnimatorHelper(sublime_plugin.EventListener):
	def __init__(self):
		# .... https://regex101.com/r/rvS2hn/2
		self.regexRemoveBrackets = re.compile(r'([^\\]|^)(\(|\))')
		# .... https://regex101.com/r/rQC7Vr/1
		self.regexWhereBrackets = re.compile(r'(\(.*?\))')
		# .... https://regex101.com/r/fWQ35P/11
		self.regexFindAllInlineCode = re.compile(r'(r?|x?)`(.*?)`')
		# .... https://regex101.com/r/fWQ35P/4
		self.regexFindAllSquareBracketBackquoteBlocks = re.compile(r'\[(r?`.*?`)\]', flags=re.X) # NOTE: re.X = extended = ignore whitespace
	def on_selection_modified(self, view):
		if view.file_name() == None or not (view.file_name().lower().endswith(".md") or view.file_name().lower().endswith(".txt")):
			view.erase_regions('MarkdownAnimatorHelperBlock')
			return;
		self.func = MarkdownAnimatorCommonFunc()

		cursor = self.func.firstEmptyCursor(view.sel())
		if cursor == None:
			view.erase_regions('MarkdownAnimatorHelperBlock')
			return

		thatLineRegion = view.full_line(cursor);
		thatLine = view.substr(thatLineRegion)
		# ....  Step 1. Find if cursor is on a set of tokens in [] (i.e. [`token1`, `token2`])
		tokensInBrackets = self.GetSpecialTokenListInBrackets(thatLine, cursor.a-thatLineRegion.a)
		if tokensInBrackets != None:
			matchingRegionsAllTokens = []
			for (token, modRorX) in tokensInBrackets:
				matchingRegionsAllTokens += self.GetHighlightRegions_ByToken(token, modRorX, view, cursor)
			self.removeRegionsIntersectingWithCursorRange(matchingRegionsAllTokens, thatLineRegion.a, thatLineRegion.b) # NOTE: disable the whole line
			view.add_regions('MarkdownAnimatorHelperBlock', matchingRegionsAllTokens, 'blackness... ARRRG!')
			return # .... first cursor list of tokens in []
		# ....  Step 2. Find if cursor is on a token (i.e. `token`)
		(token, modRorX) = self.GetSpecialToken(thatLine, cursor.a-thatLineRegion.a)
		if token != None:
			matchingRegionsOneToken = self.GetHighlightRegions_ByToken(token, modRorX, view, cursor)
			self.removeRegionsIntersectingWithCursorRange(matchingRegionsOneToken, thatLineRegion.a, thatLineRegion.b) # NOTE: disable the whole line
			#self.removeRegionsIntersectingWithCursorRange(matchingRegionsOneToken, cursor.a, cursor.a) # Old code (just cursor). NOTE: a == b, see above
			view.add_regions('MarkdownAnimatorHelperBlock', matchingRegionsOneToken, 'blackness... ARRRG!')
			return # .... first cursor token
		# ....  Step 3. Find if cursor is on an HTML tag. E.g. <md-highlight lines="5,13" />
		htmlCodeText = self.GetHtmlTag(thatLine, cursor.a-thatLineRegion.a)
		mdHighlight = self.ParseHtmlCodeText_mdHighlight(htmlCodeText)
		if mdHighlight != None:
			# .... go through lines and find code blocks
			allLength = view.size()
			regionAll = sublime.Region(0, allLength)
			allLines = view.lines(regionAll)
			prevCodeBlock = None
			passedCursor = False
			inCode = False
			prevWasABlank = False
			linesToHighlight = []
			for lineRegion in allLines:
				line = view.substr(lineRegion)
				isBlank = lineRegion.a == lineRegion.b
				if line.startswith("    ") or line.startswith("\t") or isBlank:
					if not inCode and prevWasABlank:
						# .... code started
						prevCodeBlock = []
						inCode = True
						# print ("started code", line)
					if inCode:
						prevCodeBlock += [lineRegion]
				else:
					if inCode and passedCursor:
						# .... one code after cursor => last code block
						if prevCodeBlock != None:
							# print (".... one code after cursor => last code block")
							# print (prevCodeBlock)
							linesToHighlight += self.pickLines(prevCodeBlock, mdHighlight)
						break
					inCode = False
				if cursor.a >= lineRegion.a and cursor.a <= lineRegion.b:
					# print ("in cursor")
					passedCursor = True
					# .... highlight lines in prev code block
					if prevCodeBlock != None:
						# print (".... highlight lines in prev code block")
						# print (prevCodeBlock)
						linesToHighlight += self.pickLines(prevCodeBlock, mdHighlight)
				prevWasABlank = isBlank
			view.add_regions('MarkdownAnimatorHelperBlock', linesToHighlight, 'blackness... ARRRG!')
			return # .... first cursor mdHighlight
		# .... if return was not called by anyone above, it means cursor is not on any markers and we need to clear regions
		view.erase_regions('MarkdownAnimatorHelperBlock')

	def pickLines(self, codeRegions, indices):
		lines = []
		rangeCode = range(len(codeRegions))
		for index in indices:
			if index-1 in rangeCode:
				lines += [codeRegions[index-1]]
		return lines

	# .... modifies matchingRegions. Removes region(s), so we don't highlight where the cursor is
	def removeRegionsIntersectingWithCursorRange(self, matchingRegions, cursorStart, cursorEnd):
		toRemove = []
		for mmm in matchingRegions:
			# .... condition to remove
			if ((cursorStart <= mmm.a and mmm.a <= cursorEnd) or # region start (mmm.a) is within cursor
				(cursorStart <= mmm.b and mmm.b <= cursorEnd) or # region end (mmm.b) is within cursor
				(mmm.a <= cursorStart and cursorStart <= mmm.b)): # cursor start is within region
				toRemove += [mmm]
		for mmm in toRemove:
			matchingRegions.remove(mmm)

	# .... figure out where these brackets are (adjustment, incremented by 2, is subtracted as if we were removing the brackets)
	# .... so we can then select those inner regions inside our matchingRegions
	# .... e.g. (regex)/printf/(g)e ---> regex/printf/ge ---> [(0,4), (13,13)]
	# .... e.g. (regex)/printf\(...\)/(g)e ---> regex/printf(...)/ge ---> [(0,4), (18,18)]
	def findBraketPosition(self, token):
		token = token.replace('\\(', ' ')
		token = token.replace('\\)', ' ')
		groupPositions = []
		adjustment = 0
		for m in self.regexWhereBrackets.finditer(token):
			groupPositions += [(m.start(1)-adjustment, m.end(1)-3-adjustment)]
			adjustment += 2
		return groupPositions

	# .... returns the inline code text (between `back` quotes) on which the cursor currently  is
	#      NOTE: cursorPos is WRT start of line, not absolute
	def GetSpecialToken(self, line, cursorPos):
		count = 0
		index = 0
		prevWasRorX = ''
		RorXInfrontOfIt = ''
		for c in line:
			# .... before cursor
			if index < cursorPos and c == "`":
				count += 1
				firstIndex = index
				RorXInfrontOfIt = prevWasRorX
			# .... on cursor, if even, means not between the 2 quotes
			if index == cursorPos and count % 2 == 0:
				return (None, False)
			# .... after
			if index >= cursorPos and c == "`":
				return (line[firstIndex+1:index], RorXInfrontOfIt)
			prevWasRorX = c if (c == 'r' or c == 'x') else '' 
			index += 1
		return (None, False)

	# .... returns a list of all tokens (in tuple form, similar to GetSpecialToken) if cursor is [`b/w`, `square brackets`]
	#      NOTE: cursorPos is WRT start of line, not absolute
	#      NOTE: [`with inline code`]. Square brackets + no backquotes returns null
	def GetSpecialTokenListInBrackets(self, line, cursorPos):
		# .... see https://regex101.com/r/fWQ35P/4
		for m in self.regexFindAllSquareBracketBackquoteBlocks.finditer(line):
			# .... is cursor on this match?
			# print ("match:", m.start(1), m.end(1), m.group(1))
			if m.start(1) <= cursorPos and cursorPos <= m.end(1):
				# .... Find all the `...` and r`...` and x`...`, See: https://regex101.com/r/fWQ35P/1
				bwBracketsText = m.group(1)
				tokenList = []
				for m in self.regexFindAllInlineCode.finditer(bwBracketsText):
					token = m.group(2)
					modRorX = m.group(1)
					tokenList += [(token, modRorX)]
					# print (token, modRorX)
				return tokenList
		return None

	# .... returns HTML tag the cursor is currently on (<md-highlight lines="5,13" />)
	def GetHtmlTag(self, line, cursorPos):
		count = 0
		index = 0
		isInBetween = False
		for c in line:
			# .... before cursor
			if index < cursorPos and c == "<":
				count += 1
				firstIndex = index
				isInBetween = True
			if index < cursorPos and c == ">":
				isInBetween = False
			# .... on cursor
			if index == cursorPos and not isInBetween:
				return None
			# .... after
			if index > cursorPos and c == ">":
				return line[firstIndex:index+1]
			index += 1
		#return line.strip() + ": " + str(cursorPos)
		return None

	# .... parses the tag we extracted in GetHtmlTag
	def ParseHtmlCodeText_mdHighlight(self, htmlCodeText):
		if htmlCodeText == None:
			return None
		mo = re.match("<md-highlight\\slines=\"(.*?)\".*/>", htmlCodeText)
		if mo != None:
			arrCommaText = mo.group(1)
			arrSplit = arrCommaText.split(',')
			arrSplitInt = [int(x) for x in arrSplit if x] # .... convert all non-empty entries to ints
			return arrSplitInt
		return None

	# def GetFirstCodeBlock(text):
	# 	splitLines = text.split('\n')
	# 	curChar = 0 # `xello`
	# 	for line in splitLines:
	# 		if line.startswith('\t'):
	# 			if firstLine:
	# 				firstLineOfCode = curChar
	# 			lastLineOfCode = curChar
	# 		curChar += len(line)

	#---------------------------------- hightligtht functions -----------------------------

	def GetHighlightRegions_ByToken(self, token, modRorX, view, cursor):
		#print (token, isRegex)
		# .... need LITERAL, otherwise it uses regex
		if modRorX == 'x':
			decodedRegions = self.func.regionsDecode(token)
			print('TODO: highlight decodedRegions in code above anbd below', decodedRegions)
			return view.find_all('star', sublime.LITERAL)
		elif modRorX == 'r':
			# .... remove brackets, unless they are preceeded by back-slash
			escapedToken = self.regexRemoveBrackets.sub(r'\1', token)
			escapedToken = escapedToken.replace('\\(', '(')
			escapedToken = escapedToken.replace('\\)', ')')
			matchingRegions = view.find_all(escapedToken, sublime.LITERAL)
			groupPositions = self.findBraketPosition(token)
			# .... compute inner regions for each matchingRegions
			matchingRegions2 = []
			for mmm in matchingRegions:
				for ggg in groupPositions:
					matchingRegions2 += [sublime.Region(mmm.a + ggg[0], mmm.a + ggg[1]+1)]
			return matchingRegions2
		return view.find_all(token, sublime.LITERAL)


import base64
import struct

class MarkdownAnimatorCommonFunc:
	# .... FROM: http://stackoverflow.com/questions/34247166/python-convert-int-to-unsigned-short-then-back-to-int
	def int_to_signed_short(self, value):
		return -(value & 0x8000) | (value & 0x7fff)
	def regionsEncode(self, regions):
		regionsFlat = []
		for (start, length) in regions:
			regionsFlat += [self.int_to_signed_short(start), self.int_to_signed_short(length)]
		str64 = self.shortArr_encode64(regionsFlat)
		return str64
	def regionsDecode(self, str64):
		regionsFlat = self.shortArr_decode64(str64)
		# .... FROM: http://stackoverflow.com/questions/15266593/how-to-group-list-items-into-tuple
		regions = [tuple(regionsFlat[i:i+2]) for i in range(0, len(regionsFlat), 2)]
		return regions
	# .... NOTE: the following functions work only with arrays of shorts, hence the "H". (See struct documentation)
	def shortArr_encode64(self, shortArray):
		packedBytes = struct.pack("H" * len(shortArray), *shortArray)
		str64 = base64.b64encode(packedBytes).decode('utf-8')
		return str64
	def shortArr_decode64(self, str64):
		decodedBytes = base64.b64decode(str64.encode('utf-8'))
		decodedArray = struct.unpack("H" * int(len(decodedBytes)/2), decodedBytes)
		return list(decodedArray)
	def firstNonEmptyCursor(self, sel):
		for cursor in sel:
			if cursor.a != cursor.b:
				return cursor
		return None
	def firstEmptyCursor(self, sel):
		for cursor in sel:
			if cursor.a == cursor.b:
				return cursor
		return None
	def getCodeBlocks(self, view):
		allLength = view.size()
		regionAll = sublime.Region(0, allLength)
		allLines = view.lines(regionAll)
		prevCodeBlock = None
		inCode = False
		prevWasABlank = False
		codeBlocks = []
		for lineRegion in allLines:
			line = view.substr(lineRegion)
			isBlank = lineRegion.a == lineRegion.b
			if line.startswith("    ") or line.startswith("\t") or isBlank:
				if not inCode and prevWasABlank:
					# .... code started
					# print ("started code", line)
					if prevCodeBlock != None and len(prevCodeBlock) > 0:
						codeBlocks += [sublime.Region(prevCodeBlock[0].a, prevCodeBlock[-1].b)]
					prevCodeBlock = []
					inCode = True
				if inCode:
					prevCodeBlock += [lineRegion]
			else:
				inCode = False
			prevWasABlank = isBlank
		if prevCodeBlock != None and len(prevCodeBlock) > 0:
			codeBlocks += [sublime.Region(prevCodeBlock[0].a, prevCodeBlock[-1].b)]
		return codeBlocks
	def appendNoteBullet(self, view, edit):
		sel = view.sel()
		if len(sel) == 0:
			return False
		# .... cursor location
		cursor = sel[0]

		allLength = view.size()
		regionAll = sublime.Region(0, allLength)
		allLines = view.lines(regionAll)
		passedCursor = False
		inCode = False
		prevWasABlank = False

		for lineRegion in allLines:
			line = view.substr(lineRegion)
			isBlank = lineRegion.a == lineRegion.b
			if line.startswith("    ") or line.startswith("\t") or isBlank:
				if not inCode and prevWasABlank:
					# .... code started
					inCode = True
			else:
				inCode = False
			if cursor.a >= lineRegion.a and cursor.a <= lineRegion.b:
				# print ("in cursor")
				if not inCode:
					print ("not in code!")
					return
				passedCursor = True
			if passedCursor and not inCode:
				break
			prevWasABlank = isBlank
		# .... lineRegion is line after cursor code block. line is its content
		if inCode:
			# .... special case: we are at the end
			view.insert(edit, lineRegion.b, "\n\nNotes:\n\n - \n")
			self.cursorTo(view, lineRegion.b + 13)
			return True
		if line == "Note:" or line == "Notes:":
			# .... insert after the existing Notes:
			noteIndex = allLines.index(lineRegion)
			for i in range(noteIndex+2, len(allLines)):
				lineRegion = allLines[i]
				line = view.substr(lineRegion)
				if line.startswith(r'\s') or lineRegion.a == lineRegion.b:
					view.insert(edit, lineRegion.a, " - \n")
					self.cursorTo(view, lineRegion.b + 3)
					return True
		else:
			# .... insert new Notes above prev line:
			view.insert(edit, lineRegion.a, "Notes:\n\n - \n\n")
			self.cursorTo(view, lineRegion.a + 11)
			return True
		return False
	def cursorTo(self, view, pos):
		newCursorPos = sublime.Region(pos)
		view.sel().clear()
		view.sel().add(newCursorPos)
		view.show_at_center(newCursorPos)

# USAGE: { "keys": [ "ctrl+alt+m", "ctrl+alt+b" ], "command": "markdown_animator_highlight" },
class MarkdownAnimatorHighlightCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# if self.view.file_name() == None or not self.view.file_name().lower().endswith(".md"):
		# 	return;
		self.func = MarkdownAnimatorCommonFunc()

		firstNonEmptyCursor = self.func.firstNonEmptyCursor(self.view.sel())
		if firstNonEmptyCursor == None:
			return

		codeBlocks = self.func.getCodeBlocks(self.view)
		for codeBlock in codeBlocks:
			if codeBlock.a <= firstNonEmptyCursor.a and firstNonEmptyCursor.a <= codeBlock.b:
				# .... work with this block
				highlightRegions = []
				for region in self.view.sel():
					if not region.empty():
						highlightRegions.append((region.a - codeBlock.a, region.b - region.a))
				str64 = self.func.regionsEncode(highlightRegions)
				# TODO: strip leading whitespace

				bulletAppendSuccessful = self.func.appendNoteBullet(self.view, edit)
				if bulletAppendSuccessful:
					self.view.run_command("insert_snippet", { "contents": "[x`" + str64 + "`] " })

				# print(highlightRegions);
				# print(str64);
				# decodedJunk = self.func.regionsDecode(str64)
				# print(decodedJunk);

# USAGE: { "keys": [ "ctrl+alt+m", "ctrl+alt+n" ], "command": "markdown_animator_insert_token_note" },
#        view.run_command("markdown_animator_insert_token_note")
class MarkdownAnimatorInsertTokenNoteCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		func = MarkdownAnimatorCommonFunc()
		bulletAppendSuccessful = func.appendNoteBullet(self.view, edit)
		if bulletAppendSuccessful:
			self.view.run_command("insert_snippet", { "contents": "[`${1:}`] " })
		