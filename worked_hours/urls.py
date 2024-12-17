# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:year>/<str:month>/', views.home, name='home'),
    path('monthly/', views.monthly, name='monthly'),
    path('monthly/<int:year>/<str:month>/', views.monthly, name='monthly'),
    path('weekly/', views.weekly, name='weekly'),
    path('weekly/<int:year>/<int:week>/', views.weekly, name='weekly'),
    path('get_timecards/', views.get_timecards, name='get_timecards'),
    path('add_timecard/', views.add_timecard, name='add_timecard'),
    path('edit_timecard/<int:timecard_id>/', views.edit_timecard, name='edit_timecard'),
    path('delete_timecard/<int:timecard_id>/', views.delete_timecard, name='delete_timecard'),
    path('add_project/', views.add_project, name='add_project'),
    path('add_company/', views.add_company, name='add_company'),
    path('logout/', views.user_logout, name='logout'),
] 
