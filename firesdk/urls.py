from django.urls import path

from firesdk import views

urlpatterns = [

    path('', views.temp_home),
    path('users/', views.show_users),
    path('schedule/week<int:num>/', views.get_schedule)

]
