import sublime, sublime_plugin
import re

#.... NOTE: text has to be selected. Only selected region will change

class ChewMyTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                #.... Format PATH from Commnad Prompt
                # text = text.replace("\n", "")
                # text = text.replace(";", "\n")
                #.... Wiki clean
                #text = re.sub("\[.*?\]", "", text)

                #.... transform .phrasi into interleaved en-es
                text = re.sub("^([^\s].*)$", "es: nueva palabra - \\1", text, 0, re.MULTILINE)
                text = re.sub("^\s*#.*$", "", text, 0, re.MULTILINE)
                text = re.sub("\t(.*?)\s*\#\s*(.*?)\n", "en: \\2\nes: \\1\n", text) #, re.MULTILINE)
                self.view.replace(edit, region, text)