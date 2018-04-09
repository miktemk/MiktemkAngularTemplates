import sublime, sublime_plugin
import re

#.... will copy to clip board what is `between backquotes` on which the cursor is. `test 1`, `test---2222`

class CopyToClipboardWhatsBetweenBackquotes(sublime_plugin.TextCommand):
    def run(self, edit):
        for cursor in self.view.sel():
            thatLineRegion = self.view.full_line(cursor)
            thatLine = self.view.substr(thatLineRegion)
            (token, modRorX) = self.GetSpecialToken(thatLine, cursor.a-thatLineRegion.a)
            if token != None:
                #print (token)
                sublime.set_clipboard(token);
            break;
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