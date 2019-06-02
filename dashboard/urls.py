from django.urls import path

from dashboard import views

urlpatterns = [

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),

    path('', views.Home.as_view(), name='home'),
    path('schedule/', views.Schedule.as_view(), name='schedule'),
    path('time-off/', views.TimeOff.as_view(), name='time-off'),
    path('settings/', views.Settings.as_view(), name='settings'),

    # Basic Only
    path('availability/', views.Availability.as_view(), name='availability-page'),

    # Manager Only
    path('needs/', views.Needs.as_view(), name='needs'),

    # START ajax #

    # Basic
    path('ajax/schedule-timeoff/', views.schedule_timeoff, name='schedule-timeoff'),
    path('ajax/availability/', views.availability, name='availability'),
    path('ajax/user-schedule/<str:start_date_string>/<str:end_date_string>/', views.user_schedule, name='user-schedule'),
    path('ajax/user-time-off/', views.update_user_time_off, name='user-time-off'),

    # Manager
    path('ajax/day-schedule/<str:date_string>/', views.day_schedule, name='day-schedule'),
    path('ajax/upcoming-time-off/<str:date_string>/', views.upcoming_time_off, name='upcoming-time-off'),
    path('ajax/upcoming-time-off/', views.update_time_off_request, name='update-time-off-request'),
    path('ajax/needs/', views.needs, name='needs-ajax'),
    path('ajax/full-schedule/<str:start_date_string>/<str:end_date_string>/', views.full_schedule, name='full-schedule'),
    path('ajax/full-schedule/', views.update_full_schedule, name='full-schedule'),
    path('ajax/saved-shifts/', views.get_saved_shifts, name='saved-shifts'),
    path('ajax/full-time-off/<str:date_string>/', views.full_time_off, name='full-time-off'),

    # END ajax #

]
