from calendar import HTMLCalendar
import calendar
from datetime import datetime

class CustomHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, dates_with_timecards):
        super().__init__()
        self.dates_with_timecards = dates_with_timecards

    def formatday(self, day, weekday, year, month):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        date = datetime(year, month, day).date()
        cssclass = self.cssclasses[weekday]
        if datetime.now().date() == datetime(year, month, day).date():
            cssclass += ' today'
        if date in self.dates_with_timecards:
            return f'<td class="{cssclass}"><a href="#" data-date="{year}-{month:02d}-{day:02d}">{day}</a><span class="dot"></span></td>'
        return f'<td class="{cssclass}"><a href="#" data-date="{year}-{month:02d}-{day:02d}">{day}</a></td>'

    def formatmonth(self, year, month, withyear=True):
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(year, month, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(year, month):
            a(self.formatweek(week, year, month))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def formatweek(self, theweek, year, month):
        s = ''.join(self.formatday(d, wd, year, month) for (d, wd) in theweek)
        return f'<tr>{s}</tr>'
