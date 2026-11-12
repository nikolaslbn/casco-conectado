from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('api/ultima-alerta/', views.obtener_ultima_alerta, name='ultima_alerta'),
]