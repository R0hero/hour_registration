# forms.py
from django import forms
from .models import Timecard, Company, Project

class TimecardForm(forms.ModelForm):
    class Meta:
        model = Timecard
        fields = ['project', 'start_time', 'duration']

        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_number', 'company_name', 'address', 'zip', 'country']

        labels = {
            'address': 'Address'
        }

        widgets = {
            'company_number': forms.NumberInput(attrs={
                'type': 'text',
            }),
            'zip': forms.NumberInput(attrs={
                'type': 'text'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:  # Only set the default for new instances
            last_company = Company.objects.order_by('-company_number').first()
            next_number = (last_company.company_number + 1) if last_company else 1
            self.fields['company_number'].initial = next_number

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'project_number', 'company', 'description']

        widgets = {
            'project_number': forms.NumberInput(attrs={'type': 'text'}),
        }


