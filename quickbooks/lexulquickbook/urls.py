from django.urls import path , include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework import renderers
from quickbooks.lexulquickbook import views

urlpatterns = [
    path('docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema-yaml'}
    ), name='swagger-ui'),
    path('openapi.yaml', get_schema_view(
            title="API test for Lexul service",
            renderer_classes=[renderers.OpenAPIRenderer]
        ), name='openapi-schema-yaml'),
    path('openapi.json', get_schema_view(
            title="API test for Lexul service",
            renderer_classes = [renderers.JSONOpenAPIRenderer], 
        ), name='openapi-schema-json'),
    path('' , include('django_quickbooks.urls')),
    path('customer/' , views.CustomerList.as_view()),
    path('customer/<int:pk>/' , views.CustomerDetail.as_view()),
    path('qwc/', views.QwcList.as_view()),
    path('login/', views.Login.as_view()),
    path('index/', views.Home.as_view()),
    path('download_qwc/', views.download_qwc),
    path('logout/', views.log_out)
]