import sublime, sublime_plugin
import re
class CamelCaseToSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = re.sub("([a-z])([A-Z])","\g<1> \g<2>", text)
                self.view.replace(edit, region, text)