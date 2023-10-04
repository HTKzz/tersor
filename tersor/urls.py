from django.urls import path
from . import views
from .apis import Model1, Model2, Model3

urlpatterns = [
    path('api/', Model1.as_view()),
    path('api2/', Model2.as_view()),
    path('api3/', Model3.as_view()),

    path('', views.tenList, name='model_list'),
    path('<str:pk>/', views.model_detail, name='model_detail'),
    # path('model/new/', views.model_newPost, name='model_post'),
    path('update/<str:pk>/', views.model_update, name='model_update'),
    path('model/delete/<int:pk>/', views.model_delete, name='model_delete'),
    path('<str:pk>', views.tensorDetail, name='tensor_Detail'),

    path('model/new/', views.model_newPost, name='model_add'),
]