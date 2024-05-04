"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.i18n import urlpatterns as i18n_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from detector.forms import LanguageForm
from detector.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', encrypt_text, name='encrypt_text'),
    path('decrypt/', decrypt_text, name='decrypt_text'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('', include('django.contrib.auth.urls')),  # Включаем стандартные URL для аутентификации
    path('cust-logout/', CustomLogoutView.as_view(), name='cust-logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('profile/', profile, name='profile'),
    path('set_language/', LanguageForm, name='set_language'),
    path('encrypt-image/', encrypt_image, name='encrypt-image'),
    path('decrypt-image/', decrypt_image, name='decrypt-image'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_urlpatterns