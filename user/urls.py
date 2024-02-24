from django.contrib import admin
from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('products/', views.p_search, name='products'),
    path('category/<slug:slug>/', views.cat_search, name='catsearch'),
    path('sub-category/<slug:slug>/', views.scat_search, name='subsearch'),
    path('firm/<slug:slug>/', views.search_details, name='firmdetail'),
    path('person/<slug:slug>/', views.search_details_person, name='persondetail'),
    path('account/profile/', views.user_profile, name='user-profile'),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
    # path('clubmember/<slug:slug>/', views.member_details, name='memberdetail'),
    path('c/', views.clubs, name='clubs'),
    path('c/<slug:slug>/', views.clubs_view, name='clubs_view'),
    path('login/', views.signin, name='user-login'),
    path('login/forgot-password', views.forgot_pwd, name='forgot_pwd'),
    path('login/forgot-password/otp', views.otp_cnfrm, name='cnfrm_otp'),
    path('login/forgot-password/reset', views.reset_password, name='reset_password'),
    path('logout/', views.logoutUser, name='user-logout'),
    path('register/', views.register, name='register'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add-to-wishlist/<slug:slug>', views.user_wishlist, name='user_wishlist'),
    path('creditvalues/', views.wishlist, name='creditvalues'),
    path('terms-and-conditions/', views.terms_form, name='terms'),
    path('faq/', views.faqs, name='faq'),
    path('privacy-policy/', views.privacy_form, name='privacy'),
    path('careers/', views.careers, name='careers'),
    path('firm/registration', views.user_detail_view, name='register_firm'),  # firm registration
    path('firm/update/<slug:slug>/', views.create_business, name='update_firm'),  # firm registeration update
    path('ajax/search/', views.search_results, name='ajax-search'),
    path('ajax/product/', views.search_results_p, name='ajax-search-p'),
    path('ajax/load-email/', views.load_email, name='ajax_load_email'),#AJAX
    path('ajax/load-mobile/', views.load_mobile, name='ajax_load_mobile'),#AJAX
    path('download/', download_details, name='download_details'),#CSV download
    # path('ajax/load-download/', views.load_download, name='ajax_load_download'),#AJAX
    path('ajax/load-detectbalance/', views.detect_balance, name='detect_values'),
    path('ajax/load-checkbalance/', views.check_balance, name='check_values'),
    path('verify_otp',views.verify_otp,name='verify'),
    path('analytics/<slug:slug>/',views.analytics,name='analytics'),
    path('notification/<slug:slug>/',views.notification,name='notification'),
]
