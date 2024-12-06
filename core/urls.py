from . import views
from django.urls import path


urlpatterns = [
    path('project/', views.gemcloud_view, name='index'),
    path('', views.about, name='about'),
]