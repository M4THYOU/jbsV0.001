from django.urls import path

from firesdk import views
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [

    path('', views.temp_home),

    # V1 - NO LONGER IN SERVICE
    # path('users/', views.show_users),
    # path('schedule/', views.GetSchedule.as_view()),
    # path('schedule/<int:weeks>/', views.GetSchedule.as_view()),

    # Check Server
    path('check-server/', views.CheckServer.as_view()),

    # V2 - Authentication
    path('upload/user-list/', views.UserList.as_view()),
    path('code/<str:company_code>/', views.CompanyCode.as_view()),
    path('login-bool/', views.UserLoginBools.as_view()),  # post
    path('login-bool/<str:company>/<str:encoded_email>/', views.UserLoginBools.as_view()),  # get
    path('account-type/<str:company>/<str:encoded_email>/', views.AccountType.as_view()),  # not in use???

    # V2 - POST
    path('company/', views.Company.as_view()),
    path('users/', views.User.as_view()),
    path('avail/', views.Availability.as_view()),
    path('needs/', views.Needs.as_view()),
    path('schedule/', views.FullSchedule.as_view()),
    path('time-off/', views.TimeOff.as_view()),  # not used?
    path('time-off/single/', views.SingleTimeOff.as_view()),

    # V2 - GET
    path('users/<str:company>/<str:department>/', views.Users.as_view()),
    path('users/single/<str:company>/<str:encoded_email>/', views.User.as_view()),
    path('avail/<str:company>/<str:encoded_email>/', views.Availability.as_view()),
    path('avail/<str:company>/all/<str:department>/', views.FullAvailability.as_view()),
    path('needs/<str:company>/<str:department>/', views.Needs.as_view()),
    path('open-hours/<str:company>/<str:department>/', views.DepartmentOpenHours.as_view()),
    path('schedule/<str:company>/<str:department>/', views.FullSchedule.as_view()),
    path('schedule/<str:company>/user/<str:encoded_email>/', views.UserSchedule.as_view()),
    path('time-off/<str:company>/<str:department>/', views.TimeOff.as_view()),
    path('time-off/<str:company>/user/<str:encoded_email>/', views.SingleTimeOff.as_view()),

    # Metrics
    path('metrics/', views.Metrics.as_view()),

    # Token
    path('token/', TokenObtainPairView.as_view()),

]
