import sublime, sublime_plugin
import re

#.... NOTE: text has to be selected. Only selected region will change

class ChewMyTextMdaRegexEscapeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                #.... escape round brackets for MDA regex
                text = text.replace("(", "\\(")
                text = text.replace(")", "\\)")
                #....
                self.view.replace(edit, region, text)