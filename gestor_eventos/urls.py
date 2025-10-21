"""
URL configuration for gestor_eventos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from eventos import views as eventos_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs para login/logout usando vistas genéricas de Django
    path('login/', auth_views.LoginView.as_view(template_name='eventos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Registro personalizado de usuarios
    path('registro/', eventos_views.registro, name='registro'),

    # URLs app eventos
    path('eventos/', include('eventos.urls')),

    # Redirección raíz a la lista de eventos
    path('', lambda request: redirect('eventos:lista_eventos')),
]

# Vista personalizada para acceso denegado 403
handler403 = 'eventos.views.permiso_denegado'