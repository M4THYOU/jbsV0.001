from django.urls import path

from webapp import views

urlpatterns = [

    # path('', views.temp_home),
    path('', views.home, name='home'),
    path('works/', views.works, name='works'),
    path('works-grid/', views.works_grid, name='works_grid'),
    path('works-grid-no-text/', views.works_grid_no_text, name='works_grid_no_text'),
    path('services/', views.services, name='services'),
    path('blog/', views.blog, name='blog'),
    path('about/', views.about, name='about'),
    path('shop/', views.shop, name='shop'),
    path('contact/', views.contact, name='contact'),

]
