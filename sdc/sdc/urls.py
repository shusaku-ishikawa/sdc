"""sdc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include, url

from backend_v1.urls import router as v1_router
from backend_v2.urls import router as v2_router

from . import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'sdc/core/', include('core.urls')),
    url(r'^sdc/v1/api/', include(v1_router.urls)),
    url(r'^sdc/api/', include(v2_router.urls)),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
