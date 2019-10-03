import sublime, sublime_plugin
import re, datetime


class GenerateMddateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #---------------- CONFIG ---------------
        doWeekendColor = True
        weekendColor = "#ffdd99"
        #---------------------------------------

        weekend = set([5, 6])
        daty = datetime.date.today()
        dateStr = "{:%a/%b %d/%Y}".format(daty)
        if doWeekendColor and daty.weekday() in weekend:
            dateStr = "<font color='{1}'>{0}</font>".format(dateStr, weekendColor)
        mdStr = "## =============== " + dateStr + " ==============="
        cursor = self.view.sel()[0]
        # self.view.insert(edit, cursor.a, "\n" + mdStr + "\n\n")
        self.view.insert(edit, cursor.a, mdStr + "\n\n")
