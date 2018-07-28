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