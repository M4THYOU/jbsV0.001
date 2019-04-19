from django.urls import path

from dashboard import views

urlpatterns = [

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),

    path('', views.Home.as_view(), name='home'),

    # START ajax #
    path('ajax/schedule-timeoff/', views.schedule_timeoff, name='schedule-timeoff'),
    path('ajax/availability/', views.availability, name='availability'),

]
