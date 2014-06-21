from datetime import datetime
import Tkinter as tk
import ttk
import calendar
import threading
import AttachmentFetcher

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title("Attachment Fetcher")
        self.geometry("300x510")

        self.service = self.optionMenu("Select email service: ", self.services())
        self.username = self.input("Username: ")
        self.password = self.input("Password: ", hide = True)
        self.start_date = self.timeInput("Received after: ")
        self.end_date = self.timeInput("Received before: ")
        self.file_type= self.optionMenu("Select attachment type: ", self.fileTypes())
        self.button("Get files", self.getFiles)

    def services(self):
        return ["yahoo", "gmail", "aol", "live"]

    def fileTypes(self):
        return ["jpeg", "gif", "png", "txt", "html", "pdf"]

    def optionMenu(self, text, options):
        tk.Label(self.master, text = text).pack()
        val = tk.StringVar(self.master)
        tk.OptionMenu(self.master, val, *options).pack()
        return val

    def input(self, text, hide = False):
        tk.Label(self.master, text = text).pack()
        entry = tk.Entry(self.master, show = "*" if hide else None)
        entry.pack()
        return entry

    def timeInput(self, text):
        tk.Label(self.master, text = text).pack()
        return self.input("Month: "), self.input("Day: "), self.input("Year: ")

    def button(self, text, onclick = None):    
        button = tk.Button(self.master, text = text)
        button.pack()
        if onclick:
            button.bind("<Button-1>", onclick)

    def dateIsValid(self, date):
        month, day, year = self.dateValues(date)
        return self.matchMonth(month) and day.isdigit() and year.isdigit()
        
    def datesAreValid(self):
        return self.dateIsValid(self.start_date) and self.dateIsValid(self.end_date)

    def dateObject(self, date):
        month, day, year = self.dateValues(date)
        return datetime.strptime(self.matchMonth(month) + " " + day + " " + year, '%b %d %Y').timetuple()

    def matchMonth(self, attempt):
        for index, month in enumerate(calendar.month_name):
            if month.startswith(attempt) or attempt == str(index):
                return calendar.month_abbr[index]

    def dateValues(self, date):
        return [val.get() for val in date]

    def values(self):
        return self.service.get(), self.username.get(), self.password.get(), \
               self.dateObject(self.start_date), self.dateObject(self.end_date), \
               self.file_type.get()

    def startProgressBar(self):
        progress_bar = ttk.Progressbar(self.master, orient=tk.HORIZONTAL, mode='indeterminate')
        progress_bar.start()
        progress_bar.pack()
        return progress_bar

    def getAttachments(self, progress_bar = None):
        AttachmentFetcher.getAttachments(*self.values())
        if progress_bar:
            progress_bar.stop()
   
    def getFiles(self, event):
        if self.datesAreValid():
            progress_bar = self.startProgressBar()
            threading.Thread(target = self.getAttachments, args = (progress_bar, )).start()
        else:
            print "Invalid date entry! Correct example: April 12 1998"

def runGUI():
    GUI().mainloop()

