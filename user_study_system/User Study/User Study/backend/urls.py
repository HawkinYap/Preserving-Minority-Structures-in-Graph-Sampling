from django.urls import path
from . import views
from django.views.generic.base import TemplateView

app_name = 'backend'

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html")),
    path('register/', views.register),
    path('saveRecord/', views.saveRecord),
    path('receiveSvg/', views.receiveSvg),
    path('getExpeSvgList/', views.getExpeSvgList),
    path('getSvgRecordList/', views.getSvgRecordList),
    path('getSvgUserImage/', views.getSvgUserImage),
    path('getAllImages/', views.getAllImages),
    path('getSvgOriImage/', views.getSvgOriImage),
    path('readRects/', views.readRects),
    path('getSourceData/', views.getSourceData),
    path('saveEvaluationRecord/', views.saveEvaluationRecord),
    path('saveHeatMap/', views.saveHeatMap),
]
