from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.upload, name='upload'),
    path('reduce', views.reduce, name='reduce'),
    path('csrf', views.csrf, name='test')
]
