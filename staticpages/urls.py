from django.urls import path

from . import views

urlpatterns = [
    path('about/', views.about, name='about'), # adicione esta linha
    path('', views.index, name='index'),
]
