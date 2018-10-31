from django.urls import path

from firesdk import views

urlpatterns = [

    path('', views.temp_home),

    # V1 - NO LONGER IN SERVICE
    # path('users/', views.show_users),
    # path('schedule/', views.GetSchedule.as_view()),
    # path('schedule/<int:weeks>/', views.GetSchedule.as_view()),

    # V2 - Authentication
    path('code/<str:company_code>', views.CompanyCode.as_view()),

    # V2 - POST
    path('company/', views.Company.as_view()),
    # path('add/department/'),
    path('users/', views.User.as_view()),
    path('avail/', views.Availability.as_view()),
    path('needs/', views.Needs.as_view()),

    # V2 - GET
    path('users/<str:company>/<str:department>/', views.Users.as_view()),
    path('users/<str:company>/<str:department>/<str:encoded_email>/', views.User.as_view()),
    path('avail/<str:company>/<str:department>/<str:encoded_email>/', views.Availability.as_view()),
    path('needs/<str:company>/<str:department>/', views.Needs.as_view()),

]
