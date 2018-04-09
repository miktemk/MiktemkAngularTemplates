import sublime, sublime_plugin
import re

#.... NOTE: text has to be selected. Only selected region will change

# view.run_command("chew_my_text_hgb_tokenize")
class ChewMyTextHgbTokenizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                #.... tokenize explanation. See https://regex101.com/r/PgCpOB/4
                text = re.sub(" - (.*)", " - [`\\1`, r`|(\\1)`] \\1", text)
                #.... get the words See https://regex101.com/r/cj0Vr8/3
                regexWherePart2 = re.compile(r'(r`\|\((.*)\)`)')
                for mo in regexWherePart2.finditer(text):
                    toSplit = mo.group(2)
                    allGroup = mo.group(1)
                    splits = toSplit.split(" ")
                    wrapped = ["r`|(" + x + ")`" for x in splits]
                    text = text.replace(allGroup, ", ".join(wrapped))
                    # print(text)
                self.view.replace(edit, region, text)
