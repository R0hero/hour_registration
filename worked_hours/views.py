from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.contrib.auth import logout

import calendar
from datetime import datetime, timedelta
from collections import defaultdict

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import urllib, base64
import json

from .models import Timecard, Project, Company
from .forms import TimecardForm, ProjectForm, CompanyForm
from .utils import CustomHTMLCalendar

# Create your views here.
@login_required
def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):

    # capitalize month
    month = month.title()

    # find month number from month name
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)
    
    # get previous month
    prev_month_date = datetime(year, month_number, 1) - timedelta(days=1)
    prev_month = prev_month_date.strftime('%B')
    # get previous year
    prev_year = prev_month_date.year
    # get next month
    next_month_date = datetime(year, month_number, 1) + timedelta(days=31)
    next_month = next_month_date.strftime('%B')
    # get next year
    next_year = prev_month_date.year

    # get which dates has timecards
    timecards = Timecard.objects.filter(user=request.user, date__year=year, date__month=month_number)
    dates_with_timecards = {tc.date for tc in timecards}

    # create HTML calendar
    cal = CustomHTMLCalendar(dates_with_timecards).formatmonth(
        year,
        month_number
    )

    # group timecards
    grouped_timecards = defaultdict(list)
    for timecard in timecards:
        grouped_timecards[timecard.date].append(timecard)

    grouped_timecards.default_factory = None

    form = TimecardForm()

    return render(request, 'home.html', {
        "year": year,
        "month": month,
        "month_number": month_number,
        "previous_month": prev_month,
        "previous_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "calendar": cal,
        'grouped_timecards': grouped_timecards,
        'form': form,
    })

@csrf_exempt
@login_required
def get_timecards(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        date = parse_date(data.get('date'))
        if date:
            timecards = Timecard.objects.filter(user=request.user, date=date)
            timecards_list = [
    {
        'id': tc.id,
        'duration': str(tc.duration),
        'start_time': tc.start_time.strftime('%H:%M') if tc.start_time else '',
        'end_time': tc.end_time.strftime('%H:%M') if tc.end_time else '',
        'project_number': tc.project.project_number,
        'project_name': tc.project.project_name,
        'company_name': tc.project.company.company_name,
        'company_number': tc.project.company.company_number,
    } for tc in timecards
]
            return JsonResponse({'timecards': timecards_list})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def monthly(request, year=datetime.now().year, month=datetime.now().strftime('%B')):

    # pull the logged in user
    user = request.user

    # capitalize month
    month = month.title()

    # find month number from month name
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)
    
    # get previous month
    prev_month_date = datetime(year, month_number, 1) - timedelta(days=1)
    prev_month = prev_month_date.strftime('%B')
    # get previous year
    prev_year = prev_month_date.year
    # get next month
    next_month_date = datetime(year, month_number, 1) + timedelta(days=31)
    next_month = next_month_date.strftime('%B')
    # get next year
    next_year = prev_month_date.year

    # pull timecards
    timecards = Timecard.objects.filter(user=user, date__year=year, date__month=month_number)
    # group timecards
    grouped_timecards = defaultdict(lambda: defaultdict(list))
    for timecard in timecards:
        grouped_timecards[timecard.date][timecard.project.company].append(timecard)

    # ensuring items are not overwritten by django
    grouped_timecards.default_factory = None
    for timecard in timecards:
        grouped_timecards[timecard.date].default_factory = None

    # calculate total hours for month
    total_hours = timedelta(0)
    for timecard in timecards:
        total_hours += timecard.duration

    # calculate total daily hours per company
    daily_hours_companies = defaultdict(lambda: defaultdict(lambda: timedelta()))
    for timecard in timecards:
        daily_hours_companies[timecard.date][timecard.project.company] += timecard.duration
    # ensuring items are not overwritten by django
    daily_hours_companies.default_factory = None
    for timecard in timecards:
        daily_hours_companies[timecard.date].default_factory = None

    return render(request, 'monthly.html', {
        "year": year,
        "month": month, 
        "month_number": month_number,
        "previous_month": prev_month,
        "previous_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        'grouped_timecards': grouped_timecards,
        'total_hours': total_hours,
        'daily_hours_companies': daily_hours_companies,
    })

@login_required
def weekly(request, year=datetime.now().year, week=datetime.now().strftime('%W')):
    
    # constants
    weekend = ['Saturday', 'Sunday']
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    target_hours = timedelta(hours=37)

    # pull the logged in user
    user = request.user

    # get week number
    week = int(week)

    # find first monday
    first_day_of_year = datetime(year,1,1)
    first_monday = first_day_of_year + timedelta(days=(7 - first_day_of_year.weekday() % 7))

    # define dates for start and end of weeks
    start_of_week = first_monday + timedelta(weeks=week - 2)
    end_of_week = start_of_week + timedelta(days=6)

    # get previous week
    prev_week = start_of_week - timedelta(days=7)
    prev_year = prev_week.year

    # get next week
    next_week = start_of_week + timedelta(days=7)
    next_year = next_week.year

    # pull timecards
    timecards = Timecard.objects.filter(user=user, date__range=(start_of_week, end_of_week))
    # group timecards
    grouped_timecards = defaultdict(lambda: defaultdict(list))
    for timecard in timecards:
        grouped_timecards[timecard.date][timecard.project.company].append(timecard)

    # ensuring items are not overwritten by django
    grouped_timecards.default_factory = None
    for timecard in timecards:
        grouped_timecards[timecard.date].default_factory = None

    # calculate total hours for month
    total_hours = timedelta(0)
    for timecard in timecards:
        total_hours += timecard.duration

    # calculate total daily hours per company
    daily_hours_companies = defaultdict(lambda: defaultdict(lambda: timedelta()))
    daily_hours = defaultdict(lambda: timedelta())
    for timecard in timecards:
        daily_hours_companies[timecard.date][timecard.project.company] += timecard.duration
        daily_hours[timecard.date] += timecard.duration
    # ensuring items are not overwritten by django
    daily_hours_companies.default_factory = None
    for timecard in timecards:
        daily_hours_companies[timecard.date].default_factory = None

    # prepare data for plotting
    dates = [(start_of_week + timedelta(days=i)).date() for i in range(7)]
    hours = [(daily_hours[date].total_seconds() / 3600) if date in daily_hours.keys() and isinstance(daily_hours[date], timedelta) else 0 for date in dates]

    cumulative_hours = [sum(hours[0:x:1]) for x in range(0, len(hours)+1)] 
    cumulative_hours = cumulative_hours[1:]

    # generate the plot
    fig, ax1 = plt.subplots(figsize=(20, 3))
    ax1.bar(dates, hours, color='blue')
    ax1.axhline(y=target_hours.total_seconds() / 3600 / 5, linestyle='--', color='darkblue', alpha=0.75)
    ax1.set_xticklabels(weekdays)
    ax1.set_ylim(0,max(max(hours),target_hours.total_seconds() / 3600 / 5) * 1.1)
    ax1.set_ylabel('Hours worked per day')
    ax1.set_title('Weekly Worked Hours')

    # ax2 = fig.add_subplot()
    ax2 = ax1.twinx()
    ax2.plot(dates, cumulative_hours, color='red')
    ax2.axhline(y=target_hours.total_seconds() / 3600, linestyle='--', color='darkred', alpha=0.75)
    ax2.set_ylabel('Hours worked total')
    ax2.set_ylim(0, max(max(cumulative_hours),target_hours.total_seconds() / 3600) * 1.1)

    # save plot to a PNG image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    weeklyplot = 'data:image/png;base64,' + urllib.parse.quote(string)

    return render(request, 'weekly.html', {
        "year": year,
        "week_number": week,
        "previous_week": prev_week.isocalendar()[1],
        "previous_year": prev_year,
        "next_week": next_week.isocalendar()[1],
        "next_year": next_year,
        'grouped_timecards': grouped_timecards,
        'total_hours': total_hours,
        'target_hours': target_hours,
        'difference_hours': total_hours - target_hours,
        'daily_hours_companies': daily_hours_companies,
        'weekdays': weekdays,
        'weekend': weekend,
        'weekly_plot': weeklyplot,
    })

def parse_duration(duration_str):
    """Parse duration string into timedelta, supporting both HH:MM and HH:MM:SS formats."""
    parts = duration_str.split(':')
    if len(parts) == 2:  # HH:MM
        hours, minutes = map(int, parts)
        return timedelta(hours=hours, minutes=minutes)
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = map(int, parts)
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    else:
        raise ValueError("Invalid duration format")

@login_required
def add_timecard(request):
    if request.method == 'POST':
        form = TimecardForm(request.POST)
        if form.is_valid():
            timecard = form.save(commit=False)
            timecard.user = request.user
            timecard.date = request.POST.get('date')

            duration_str = request.POST.get('duration')
            if duration_str:
                timecard.duration = parse_duration(duration_str)

            timecard.save()

            return redirect(reverse('home'))  # Redirect to home after saving
    else:
        form = TimecardForm()
    return render(request, 'timecard_form.html', {'form': form})

@login_required
def edit_timecard(request, timecard_id):
    timecard = get_object_or_404(Timecard, id=timecard_id)

    if request.method == 'POST':
        form = TimecardForm(request.POST, instance=timecard)
        if form.is_valid():

            duration_str = request.POST.get('duration')
            if duration_str:
                timecard.duration = parse_duration(duration_str)
            timecard.save()

            form.save()
            return redirect('home')
    else:
        form = TimecardForm(instance=timecard)

    return render(request, 'timecard_edit.html', {
        'form': form,
        'timecard': timecard
    })

@login_required
def delete_timecard(request, timecard_id):
    timecard = get_object_or_404(Timecard, pk=timecard_id)

    if request.method == 'POST':
        timecard.delete()
        return redirect('home')

    return render(request, 'edit_timecard.html', {'timecard': timecard})

@login_required
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect(reverse('home'))
    else:
        form = CompanyForm()

    return render(request, 'company_form.html', {
        'form': form,
    })

@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect(reverse('home'))
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

