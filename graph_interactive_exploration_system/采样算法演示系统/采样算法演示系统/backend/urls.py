from django.urls import path
from . import views
from django.views.generic.base import TemplateView

app_name = 'backend'
urlpatterns = [
    path('', views.index,name='index'),
    path('run_sampling/', views.run_sampling, name='run_sampling'),
    path('get_minotype/', views.get_minotype, name='get_minotype')
]
