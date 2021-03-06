import sublime, sublime_plugin
import re
from operator import itemgetter, attrgetter

#.... NOTE: if text is selected, applies only to selection. Otherwise applies to the entire text.

class ChewMyTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if len(self.view.sel()) == 1 and self.view.sel()[0].empty():
            print ('ChewMyText: no selection, affecting all text')
            allLength = self.view.size()
            regionAll = sublime.Region(0, allLength)
            text = self.view.substr(regionAll)
            text = self.ChewText(text)
            self.view.replace(edit, regionAll, text)
            return
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = self.ChewText(text)
                self.view.replace(edit, region, text)
    def RoundAllDecimalNumbers(self, text):
        # LINK: https://regex101.com/r/NI2IY3/3
        listy = []
        matches = re.finditer(re.compile(r'\d+\.\d\d\d+'), text)
        for m in matches:
            numStr = m.group(0)
            replacement = "{0:0.0f}".format(float(numStr))
            listy += [(numStr, replacement, m.start(0))]
        listy = sorted(listy, key=itemgetter(2), reverse=True)
        for (numStr, replacement, start) in listy:
            text = text[:start] + replacement + text[start + len(numStr):]
        return text

    def MultiplyAllNumbersInRegexGroups(self, text, regex, factor):
        listy = []
        matches = re.finditer(re.compile(regex), text)
        for m in matches:
            for iGroup in range(len(m.groups())):
                numStr = m.group(iGroup+1)
                num = float(numStr)
                num *= factor
                replacement = "{0:0.0f}".format(num)
                listy += [(numStr, replacement, m.start(iGroup+1))]
        listy = sorted(listy, key=itemgetter(2), reverse=True)
        for (numStr, replacement, start) in listy:
            text = text[:start] + replacement + text[start + len(numStr):]
        return text

    def ChewText(self, text):
        #.... Format PATH from Commnad Prompt
        # text = text.replace("\n", "")
        # text = text.replace(";", "\n")
        
        # .... Wiki clean 123.123123, 45.999
        #text = re.sub("\[.*?\]", "", text)

        #.... transform .phrasi into interleaved en-es
        # text = re.sub("^([^\s].*)$", "es: nueva palabra - \\1", text, 0, re.MULTILINE)
        # text = re.sub("^\s*#.*$", "", text, 0, re.MULTILINE)
        # text = re.sub("\t(.*?)\s*\#\s*(.*?)\n", "en: \\2\nes: \\1\n", text) #, re.MULTILINE)
        # self.view.replace(edit, region, text)

        #.... SVG: Reduce the file size of pngtosvg.com SVG by rounding off the decimal points
        # text = self.RoundAllDecimalNumbers(text)

        #.... SVG: LeshyLabs - apply coordinate reduction
        widthBefore = 2752
        widthAfter = 1376
        reductionFactor = float(widthAfter) / widthBefore
        # LINK: https://regex101.com/r/Yj99Mo/1
        text = self.MultiplyAllNumbersInRegexGroups(text, r'"x":(\d+),"y":(\d+),"w":(\d+),"h":(\d+)', reductionFactor)
        # LINK: https://regex101.com/r/Yj99Mo/3
        text = self.MultiplyAllNumbersInRegexGroups(text, r'{"w":(\d+),"h":(\d+)}', reductionFactor)

        #.... BASIC: do several string replacements
        # text = text.replace("CreateWorkspace", "AssignToWorkspace")
        # text = text.replace("create-workspace", "assign-to-workspace")
        # text = text.replace("Create workspace", "Assign to workspace")

        return text