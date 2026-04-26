"""
URL configuration for organichub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from website import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('wishlist/sidebar/', views.wishlist_sidebar, name='wishlist_sidebar'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("payment-success/<str:order_id>/", views.payment_success, name="payment_success"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




