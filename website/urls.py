from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('track-order/', views.track_order, name='track_order'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/product/edit/<int:id>/', views.edit_product, name='edit_product'),
    path('farmer/product/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('farmer/orders/', views.farmer_orders, name='farmer_orders'),
    path('products/', views.products, name='products'),
    path("contact/", views.contact, name="contact"),
    path('wishlist/sidebar/', views.wishlist_sidebar, name='wishlist_sidebar'),
    path('checkout/', views.checkout, name='checkout'),
    path('track-order/', views.track_order, name='track_order'),
    path("profile/sidebar/", views.sidebar_profile, name="sidebar_profile"),
    path("update-cart-qty/", views.update_cart_qty, name="update_cart_qty"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("wishlist/remove/<int:product_id>/", views.remove_wishlist_item, name="remove_wishlist_item"),
    path("payment/<int:order_id>/", views.payment, name="payment"),
    path("payment-success/<str:order_id>/", views.payment_success, name="payment_success"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path('farmer/orders/', views.farmer_orders, name='farmer_orders'),











]
