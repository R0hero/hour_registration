from django.db import models
from django.contrib.auth.models import User

from django_countries.fields import CountryField

from datetime import timedelta
from datetime import datetime

# Create your models here.

class Company(models.Model):
    # required
    company_name = models.CharField('Company name', max_length=128)
    company_number = models.IntegerField('Company number')
    # details
    address = models.CharField('Street name and number', max_length=128, blank=True, null=True)
    zip = models.IntegerField('Zip code', blank=True, null=True)
    country = CountryField(blank=True, null=True)

    class Meta:
        ordering = ['company_number']

    def __str__(self):
        return f'{self.company_number} {self.company_name}'

class Project(models.Model):
    project_name = models.CharField('Project name', max_length=128)
    project_number = models.IntegerField('Project number')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    description = models.TextField('Description of project', blank=True, null=True)

    class Meta:
        ordering = ['project_number']

    def __str__(self):
        return f'{self.project_number} {self.project_name} ({self.company.company_name})'

class Timecard(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField('Project date')
    duration = models.DurationField('Time spent',default=timedelta(hours=7,minutes=30))
    start_time = models.TimeField('Starting time',blank=True,null=True)
    end_time = models.TimeField('Ending time',blank=True, null=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.project.project_number} on {self.date}'
    
    def save(self, *args, **kwargs):
        if not self.duration:
            self.duration = timedelta(hours=7, minutes=30)

        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()

        if self.start_time and self.duration:
            clicked_date = self.date
            start_datetime = datetime.combine(clicked_date, self.start_time)
            end_datetime = start_datetime + self.duration
            self.end_time = end_datetime.time()
        super().save(*args, **kwargs)