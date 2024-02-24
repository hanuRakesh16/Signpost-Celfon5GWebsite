# import patterns as patterns
from django.urls import path
from . import views
from django.contrib import admin



urlpatterns =[
    path('', views.TaskList.as_view(), name='tasks'),
    # path('persons', PersonList.as_view(), name='persons'),
    path('task/<slug:slug>/', views.TaskDetail.as_view(), name='task'),
    # path('person/<slug:slug>/', PersonDetail.as_view(), name='pdetail'),
    # path('task-create/', TaskCreate.as_view(), name='task-create'),
    # path('login/', views.CustomLoginView.as_view(), name='login'),
    path('login/', views.signin, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    # path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('forgot-password', views.forgot_pwd, name='mp_forgot_pwd'),
    path('forgot-password/otp', views.otp_cnfrm, name='mp_cnfrm_otp'),
    path('forgot-password/reset', views.reset_password, name='mp_reset_password'),
    path('register/', views.register, name='register'),
    path('otp/', views.otp, name='otp'),
    path('income/', views.work, name='work'),
    path('add-firm/', views.adds, name='task-create'),
    path('individual/', views.individual, name='individual'),
    path('referral/', views.referral, name='referral'),
    path('person_referral/', views.ref_individual, name='ref_individual'),
    path('myreferrals', views.get_referred_firms_view, name='myreferrals'),
    path('short-form', views.basic_form, name='basic'),
    path('referral/<str:ref_code>/', views.main_view, name='main-view'),
    path('verify/', views.verify, name='verify'),
    path('check-bname/', views.check_bname, name='check-bname'),
    path('create/new/', views.create_ad, name='new-ad'),
    path('business-listing/create', views.newad, name='create-ad'),
    path('business-listing/update/<slug:slug>', views.update_ad, name='update-ad'),
    path('business-listing/', views.list_ad, name='list-ad'),
    path('create/business-listing/confirm-order', views.order_confirm, name='order-confirm'),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),#AJAX
    path('ajax/load-cat/', views.load_cat, name='ajax_load_cat'),#AJAX
    path('ajax/load-product/', views.load_p, name='ajax_load_p'),#AJAX
    path('ajax/autocomplete/', views.autocomplete, name='autocomplete'),#AJAX
    path('ajax/check_mobile/', views.check_mobile_if_already_exists, name='check_mobile'),#AJAX
    path('add-firm/ajax/send_otp/',views.otp_send,name='ajax_sendotp'),
    path('add-firm/ajax/verify_otp/',views.verify_otp,name='ajax_verifyotp')
]


