from django.urls import path

from firesdk import views

urlpatterns = [

    path('', views.temp_home),

]
