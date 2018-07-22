from django.urls import path

from firesdk import views

urlpatterns = [

    path('', views.temp_home),
    path('users/', views.show_users),
    path('schedule/<int:weeks>/', views.GetSchedule.as_view())

]
