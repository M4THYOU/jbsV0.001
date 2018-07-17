from django.urls import path

from serverauth import views

urlpatterns = [

    path('senduser/', views.post_user),

]
