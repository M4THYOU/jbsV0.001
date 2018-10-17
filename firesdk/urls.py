from django.urls import path

from firesdk import views

urlpatterns = [

    path('', views.temp_home),

    # V1
    path('users/', views.show_users),
    path('schedule/', views.GetSchedule.as_view()),
    path('schedule/<int:weeks>/', views.GetSchedule.as_view()),

    # V2
    path('avail/set/', views.PostAvailability.as_view()),

]
