import calendar
from io import BytesIO
import email
import re
from io import BytesIO
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
import requests
from base.models import *
from user.models import *
from base.forms import AddShopForm
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from user.forms import CutsomUserCreationForm
from .forms import UpdateUserForm, UpdateProfileForm, signForm, otpForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserDetailForm, BusinessForm, CreditPoint
import csv
from datetime import date
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from . import forms
from base.views import ack_email, send_ack_sms
from django.utils.safestring import mark_safe
import json
from django.db.models import Sum
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import base64
from datetime import datetime
from collections import defaultdict
from todo import settings

# Create your views here.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def signin(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist.')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Incorret Username or Password.')
    return render(request, 'account/login.html')


def logoutUser(request):
    logout(request)
    messages.error(request, 'User was successfully logged out.')
    return redirect('user-login')


def forgot_pwd(request):
    if request.method == 'POST':
        username = request.POST['username']
        try:
            get_user = User.objects.get(username=username)
            request.session['username'] = get_user.id
            send_otp(get_user)
            return redirect('cnfrm_otp')
            # return redirect('reset_password')
        except:
            messages.error(request, 'Username does not exist.')
    return render(request, 'user/forget_pwd.html')


def otp_cnfrm(request):
    profile_id = request.session.get('username')
    if not profile_id:
        return HttpResponse("403 Forbidden.")
    if request.method == 'POST':
        username = User.objects.get(pk=profile_id)
        otp = request.POST['otp']
        formatted_username = f"91{username}"
        url = f"https://control.msg91.com/api/v5/otp/verify?otp={otp}&mobile={formatted_username}"
        headers = {
            "accept": "application/json",
            "authkey": settings.MGS91_AUTH_KEY
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        if data.get('type') == 'success':
            request.session['status'] = 'success'
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'user/otp_cnfrm.html')


def reset_password(request):
    profile_id = request.session.get('username')
    status = request.session.get('status')
    if not (profile_id or status):
        return HttpResponse("403 Forbidden.")
    if request.method == 'POST':
        username = User.objects.get(pk=profile_id)
        password = request.POST['password']
        cnfrm_password = request.POST['cnfrm_password']
        if not password == cnfrm_password:
            messages.error(request, 'Password does not match')
        elif username.check_password(password):
            messages.error(request, "New password is same as old password.")
        elif validate_password(password):
            username.set_password(password)
            username.save()
            messages.success(request, "success")
            del request.session['username']
            del request.session['status']
        else:
            messages.error(request, "Password is not strong enough.")
    return render(request, 'user/reset_password.html')


def validate_password(password):
    # define our regex pattern for validation
    pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"

    # We use the re.match function to test the password against the pattern
    match = re.match(pattern, password)

    # return True if the password matches the pattern, False otherwise
    return bool(match)


def send_login_sms(recipient_mobile, password='signpost'):
    url = "https://control.msg91.com/api/v5/flow/"
    payload = {
        "template_id": "64fc0a53d6fc05110f21a303",
        "short_url": "1 (On) or 0 (Off)",
        "recipients": [
            {
                "mobiles": str(91) + str(recipient_mobile),
                "username": recipient_mobile,
                "password": password
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": settings.MGS91_AUTH_KEY
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)


def login_email(name, email, uname, password='signpost'):
    url = "https://control.msg91.com/api/v5/email/send"

    payload = {
        "recipients": [
            {
                "to": [
                    {
                        "name": name,
                        "email": email,
                    }
                ],
                "variables": {"VAR1": name, "VAR2": uname, "VAR3": password}
            },
        ],
        "from": {
            "name": "Signpost Celfon5G+",
            "email": "customercare@celfon5g.in"
        },
        "domain": "mail.celfon5g.in",
        "template_id": "LoginDetails"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": settings.MGS91_AUTH_KEY
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)


def send_otp(phn_number):
    formatted_phn_number = f"91{phn_number}"

    url = f"https://control.msg91.com/api/v5/otp?mobile={formatted_phn_number}&template_id=64919d76d6fc050fcc155362"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": settings.MGS91_AUTH_KEY
    }
    response = requests.post(url, headers=headers)
    print(phn_number)


# formatted_phn_number = f"91{phn_number}"
# url = f"https://control.msg91.com/api/v5/otp/verify?otp={otp}&mobile={formatted_phn_number}"
# headers = {
#     "accept": "application/json",
#     "authkey": "379995ABvZq4Jo64aa3124P1"
# }

# response = requests.get(url, headers=headers)
# print(response.text)

def verify_otp(request):
    phn_number = None
    verified = False
    if request.method == 'POST':
        form = otpForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            phn_number = request.session.get('username')
            formatted_phn_number = f"91{phn_number}"
            name = request.session.get('first_name')
            email = request.session.get('email')
            url = f"https://control.msg91.com/api/v5/otp/verify?otp={otp}&mobile={formatted_phn_number}"
            headers = {
                "accept": "application/json",
                "authkey": settings.MGS91_AUTH_KEY
            }

            response = requests.get(url, headers=headers)
            data = response.json()
            if data.get('type') == 'success':
                customer = User.objects.create_user(first_name=name, email=email, username=str(phn_number),
                                                    password='signpost')
                verified = True
                messages.success(request, "Your account was created Successfully")
                form = otpForm()
                send_login_sms(phn_number)
                login_email(name, email, phn_number)
                ack_email(email, name)
                send_ack_sms(phn_number, name)
            else:
                messages.error(request, 'An error occurred. Please try again.')

    else:
        form = otpForm()
    context = {'form': form, 'phn_number': phn_number, 'verified': verified}
    # del request.session['username']
    # del request.session['email']
    # del request.session['first_name']
    return render(request, 'user/otp_verify.html', context)


def register(request):
    page = 'register'
    form = signForm()
    form2 = UpdateProfileForm()
    phn_number = None

    if request.method == 'POST':
        form = signForm(request.POST)
        # otp=otp(request.post)
        # form2 = UpdateProfileForm(request.POST)
        # type = request.POST['type']
        if form.is_valid():
            # user = form.save(commit=False)
            # user.username = user.username.lower()
            name = form.cleaned_data['first_name']
            phn_number = form.cleaned_data['username']
            email = form.cleaned_data['email']
            try:
                check_data = User.objects.get(username=phn_number)
                messages.error(request, 'User already exists.')
                return redirect('register')
            except Exception:
                send_otp(phn_number)
            request.session['first_name'] = name
            request.session['email'] = email
            request.session['username'] = phn_number

            # customer= User.objects.create_user(first_name=name,email=email,username=str(phn_number), password='signpost')
            #     else:
            #         print("OTP verification failed")

            # username = user.username
            # user.save()

            # # user_id = User.objects.get(username=username)
            # print(user_id)
            # f_type = CustomProfile(user=user_id, profile_image=None, street_address=None, city=None, state=None, zipcode=None, mobile_number=username, type=type)
            # f_type.save()
            # current_user = User.objects.get(username=str(phn_number))
            form = signForm()
            # print(current_user)
            # map_mylisting(current_user)
            # send_login_sms(phn_number)
            # if email:
            #     ack_email(name,email,phn_number)
            # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('verify')


        else:
            messages.error(request, 'An error occurred. Please try again.')
    context = {'page': page, 'form': form, 'form2': form2}
    print(phn_number)
    return render(request, 'user/register.html', context)


@login_required
def user_profile(request):
    obj = get_object_or_404(User, username=request.user)
    listings = Task.objects.filter(listing_owner=request.user)
    user_objs = CustomProfile.objects.filter(user=obj)
    credit_points = CustomProfile.objects.filter(user=request.user)
    plans = Subscriptions.objects.all()
    firm_results = Firmresults.objects.filter(firm__listing_owner=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-id')[:10]
    notification_messages = []
    for firm_result in firm_results:
        if firm_result.nsearchcount % 5 == 0:
            notification_messages.append(firm_result)
           
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.customprofile)
 
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect('user-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.customprofile)
   
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'obj': obj,
        'listings': listings,
        'credit_points': credit_points,
        'plans': plans,
        'notification_messages': notification_messages,
        'transactions': transactions,
    }
    return render(request, 'account/profile.html', context)


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'account/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('user-profile')


def index(request):
    category = Category.objects.all()
    shop = Task.objects.all()
    sub_category = []
    cat = Sub_category.objects.values('category', 'category_id')
    sub = {item['category'] for item in cat}
    for i in sub:
        scat = Sub_category.objects.filter(category_id=i)
        sub_category.append(scat)
    show_popup = request.GET.get('show_popup', False)
    context = {'category': category, 'shop': shop, 'sub_category': sub_category, 'show_popup': show_popup}
    return render(request, 'user/index.html', context=context)

def searchcount(query, queryset):
    #print(query)
    #print(queryset)
    for result in queryset:
        result.search_count = result.search_count + 1
        #print(result.search_count)
        result.save()
 
def firmresults(query, results):
    for result in results:
        try:
            firm = Firmresults.objects.get(firm=result)
            firm.searchquery=firm.searchquery+","+query
            firm.nsearchcount = firm.nsearchcount + 1
            #print(firm)
            firm.save()
        except:
            firm=Firmresults.objects.create(firm=result, searchquery=query,nsearchcount=1)
            #print(firm)
            firm.save()
 

def search(request):
    query = request.GET.get('firms')
    qs = Task.objects.filter(name__search=query).order_by("name")
    ps = Task.objects.filter(name__search=query).order_by("name")
    wishlist_name = []
    if query is not None:
        qs = Task.objects.search(query)
        ps = Task.objectp.search(query)
        if request.user.is_authenticated:
            wishlist = Task.objects.filter(users_wishlist=request.user)
            for wish in wishlist:
                wishlist_name.append(wish.pk)
        searchcount(query, qs)
        searchcount(query, ps)
        firmresults(query, qs)
        firmresults(query, ps)
    context = {
        "objects": qs,
        "premiums": ps,
        "query": query,
        "wishlist": wishlist_name,
    }
    return render(request, 'user/search.html', context=context)


def p_search(request):
    query = request.GET.get('products')
    qs = Task.objects.filter(mproducts1__product_name__icontains=query) | Task.objects.filter(
        mproducts2__product_name__search=query) | Task.objects.filter(
        mproducts3__product_name__search=query) | Task.objects.filter(description__icontains=query)
    ps = Task.objects.filter(mproducts1__product_name__icontains=query) | Task.objects.filter(
        mproducts2__product_name__search=query) | Task.objects.filter(
        mproducts3__product_name__search=query) | Task.objects.filter(description__icontains=query)
    wishlist_name = []
    if query is not None:
        qs = Task.object.product(query)
        ps = Task.objectpp.product(query)
        if request.user.is_authenticated:
            wishlist = Task.objects.filter(users_wishlist=request.user)
            for wish in wishlist:
                wishlist_name.append(wish.pk)
        searchcount(query, qs)
        searchcount(query, ps)
        firmresults(query, qs)
        firmresults(query, ps)
    context = {
        "objects": qs,
        "premiums": ps,
        "query": query,
        "wishlist": wishlist_name,
    }
    return render(request, 'user/search.html', context=context)


def cat_search(request, slug=None):
    wishlist_name = []
    if Category.objects.filter(slug=slug).exists():
        category = Category.objects.get(slug=slug)
        firms = Task.objects.filter(mcategory1__slug=slug) | Task.objects.filter(
            mcategory2__slug=slug) | Task.objects.filter(mcategory3__slug=slug)
        if request.user.is_authenticated:
            wishlist = Task.objects.filter(users_wishlist=request.user)
            for wish in wishlist:
                wishlist_name.append(wish.pk)
        context = {'objects': firms, 'query': category, "wishlist": wishlist_name}
        return render(request, 'user/search.html', context=context)
    else:
        messages.error(request, "No firms exists")
        return redirect('index')


def scat_search(request, slug=None):
    wishlist_name = []
    if Sub_category.objects.filter(slug=slug).exists():
        scategory = Sub_category.objects.get(slug=slug)
        firms = Task.objects.filter(msub_category1__slug=slug) | Task.objects.filter(
            msub_category2__slug=slug) | Task.objects.filter(msub_category3__slug=slug)
        # print(firms)
        if request.user.is_authenticated:
            wishlist = Task.objects.filter(users_wishlist=request.user)
            for wish in wishlist:
                wishlist_name.append(wish.pk)
        context = {
            "objects": firms,
            "query": scategory,
            "wishlist": wishlist_name,
        }
        return render(request, 'user/search.html', context=context)
    else:
        messages.error(request, "No firms exists")
        return redirect('index')

def viewcount(query, queryset):
    #print(query)
    #print(queryset)
    for result in queryset:
        result.view_count = result.view_count + 1
        #print(result.view_count)
        result.save()

@login_required(login_url='/login')
def search_details(request, slug=None):
    # if not request.user.is_authenticated:
    #     return redirect('%s?next=%s' % (settings.USER_LOGIN_URL, request.path))
    wishlist_name = []
    obj = get_object_or_404(Task, slug=slug)
    if obj:
        wishlist = Task.objects.filter(users_wishlist=request.user)
        queryset = Task.objects.filter(name=obj.name)
        viewcount(obj.name, queryset)
        for wish in wishlist:
            wishlist_name.append(wish.pk)
        #firmresults(obj.name, queryset)
    context = {'object_list': obj, "wishlist": wishlist_name}
    return render(request, 'user/SearchDetail.html', context)


@login_required(login_url='/login')
def search_details_person(request, slug=None):
    # if not request.user.is_authenticated:
    #     return redirect('%s?next=%s' % (settings.USER_LOGIN_URL, request.path))
    wishlist_name = []
    obj = get_object_or_404(Task, slug=slug)
    if obj:
        wishlist = Task.objects.filter(users_wishlist=request.user)
        queryset = Task.objects.filter(name=obj.name)
        viewcount(obj.name, queryset)
        for wish in wishlist:
            wishlist_name.append(wish.pk)
        #firmresults(obj.name, queryset)
        #print(obj
    context = {'object_list': obj, "wishlist": wishlist_name}
    return render(request, 'user/SearchDetailPerson.html', context)


def search_results(request):
    business_name = request.GET.get('business_name')
    payload = []
    if business_name:
        fake_address_objs = Task.objects.filter(name__icontains=business_name)

        for fake_address_obj in fake_address_objs:
            item = {
                'pk': fake_address_obj.pk,
                'slug': fake_address_obj.slug,
                'name': fake_address_obj.name,
                'image': str(fake_address_obj.logo.url),
            }
            payload.append(item)

    return JsonResponse({'status': 200, 'data': payload})


def search_results_p(request):
    product_name = request.GET.get('product_name')
    payload = []
    if product_name:
        fake_address_objs = Product.objects.filter(product_name__icontains=product_name)

        for fake_address_obj in fake_address_objs:
            item = {
                'pk': fake_address_obj.pk,
                'slug': fake_address_obj.slug,
                'name': fake_address_obj.product_name,
                # 'image': str(fake_address_obj.logo.url),
            }
            payload.append(item)

    return JsonResponse({'status': 200, 'data': payload})


def clubs(request):
    clubs = Clubs.objects.all()
    context = {'clubs': clubs}
    return render(request, 'user/clubs.html', context)


# @login_required(login_url='/login')
def clubs_view(request, slug=None):
    # if not request.user.is_authenticated:
    #     return redirect('%s?next=%s' % (settings.USER_LOGIN_URL, request.path))
    wishlist_name = []
    if Clubs.objects.filter(slug=slug).exists():
        clubs = Clubs.objects.get(slug=slug)
        clubmembers = Task.object.filter(club_name_id=clubs.pk).order_by('name')
        if request.user.is_authenticated:
            wishlist = Task.objects.filter(users_wishlist=request.user)
            for wish in wishlist:
                wishlist_name.append(wish.pk)
        context = {'clubs': clubs, 'clubmembers': clubmembers, 'wishlist': wishlist_name}
        return render(request, 'user/clubs_view.html', context)
    else:
        messages.error(request, "No Clubs exists")
        return redirect('index')


@login_required(login_url='/login')
def user_wishlist(request, slug=None):
    firm = get_object_or_404(Task, slug=slug)
    if firm.users_wishlist.filter(id=request.user.id).exists():
        firm.users_wishlist.remove(request.user)
    else:
        firm.users_wishlist.add(request.user)
        messages.success(request, "Added to Wishlist")

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required(login_url='/login')
def wishlist(request, slug=None):
    firms = Task.objects.filter(users_wishlist=request.user)
    current_value = CustomProfile.objects.get(user=request.user)
    creditvalues = Creditvalues.objects.all()
    context = {
        'wishlist': firms,
        'creditvalues': creditvalues,
        'current_value': current_value,
        "prospects_length": len(firms)
    }
    return render(request, 'user/wishlist.html', context)


def download_details(request):
    wishlist = Task.objects.filter(users_wishlist=request.user)
    current_date = date.today()
    filename_pdf = str(current_date) + '-Signpost_Prospects.pdf'
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    data = [['Name', 'Email', 'Phone Number', 'City', 'Description']]
    for customer in wishlist:
        data.append([customer.name, customer.email, customer.mobile_number, customer.city, customer.description])
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    doc.build([table])
    buffer.seek(0)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename_pdf}'
    response.write(buffer.read())
    return response


def careers(request):
    careers = Careers.objects.all()
    context = {
        'careers': careers,
    }
    return render(request, 'user/careers.html', context)


def check_balance(request):
    current_value = CustomProfile.objects.get(user=request.user)
    creditvalues = Creditvalues.objects.all()
    insufficient = CustomProfile.objects.get(user=request.user)
    boxes = request.GET.get('checkboxes')
    tick = int(boxes)
    proceed = request.GET.get('value')
    if proceed:
        for field in creditvalues:
            # if proceed == 'email':
            #     if current_value.credit_points > insufficient.minimum_points:
            #         if current_value.credit_points >= field.email:
            #             current_value.credit_points = current_value.credit_points - field.email
            #         else:
            #             current_value.credit_points = current_value.credit_points
            # elif proceed == 'whatsapp':
            #     if current_value.credit_points > insufficient.minimum_points:
            #         if current_value.credit_points >= field.email:
            #             current_value.credit_points = current_value.credit_points - field.whatsapp
            #         else:
            #             current_value.credit_points = current_value.credit_points
            # elif proceed == 'sms':
            #     if current_value.credit_points > insufficient.minimum_points:
            #         if current_value.credit_points >= field.email:
            #             current_value.credit_points = current_value.credit_points - field.sms
            #         else:
            #             current_value.credit_points = current_value.credit_points
            if proceed == 'download':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.email:
                        current_value.credit_points = current_value.credit_points - field.download
                    else:
                        current_value.credit_points = current_value.credit_points
            elif proceed == 'bulk_sms':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.email:
                        current_value.credit_points = current_value.credit_points - (field.bulk_sms * tick)
                    else:
                        current_value.credit_points = current_value.credit_points
            elif proceed == 'bulk_whatsapp':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.email:
                        current_value.credit_points = current_value.credit_points - (field.bulk_whatsapp * tick)
                    else:
                        current_value.credit_points = current_value.credit_points
            elif proceed == 'bulk_email':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.email:
                        current_value.credit_points = current_value.credit_points - (field.bulk_email * tick)
                    else:
                        current_value.credit_points = current_value.credit_points
            else:
                current_value.credit_points = current_value.credit_points
    available_value = int(current_value.credit_points)
    required_value = int(insufficient.minimum_points)
    return JsonResponse({'available_value': available_value, 'required_value': required_value}, status=200)


def add_transaction(user, trans_type, desc, value):
    transaction = Transaction(user=user, type=trans_type, desc=desc, value=value)
    transaction.save()

def detect_balance(request):
    current_value = CustomProfile.objects.get(user=request.user)
    creditvalues = Creditvalues.objects.all()
    insufficient = CustomProfile.objects.get(user=request.user)
    boxes = request.GET.get('checkboxes')
    tick = int(boxes)
    proceed = request.GET.get('value')
    if proceed:
        for field in creditvalues:
            # if proceed == 'email':
            #     if current_value.credit_points > insufficient.minimum_points:
            #         if current_value.credit_points >= field.email:
            #             current_value.credit_points = current_value.credit_points - field.email
            #             current_value.save()
            #         else:
            #             current_value.credit_points = current_value.credit_points
            #             current_value.save()
            # elif proceed == 'whatsapp':
            #     if current_value.credit_points > insufficient.minimum_points:
            #         if current_value.credit_points >= field.whatsapp:
            #             current_value.credit_points = current_value.credit_points - field.whatsapp
            #             current_value.save()
            #         else:
            #             current_value.credit_points = current_value.credit_points
            #             current_value.save()
            # elif proceed == 'sms':
            #     if current_value.credit_points > insufficient.minimum_points:
            #         if current_value.credit_points >= field.sms:
            #             current_value.credit_points = current_value.credit_points - field.sms
            #             current_value.save()
            #         else:
            #             current_value.credit_points = current_value.credit_points
            #             current_value.save()
            if proceed == 'download':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.download:
                        current_value.credit_points = current_value.credit_points - field.download
                        current_value.save()
                        print("Download")
                        add_transaction(request.user, "Debit", "PDF Download", field.download)
                    else:
                        current_value.credit_points = current_value.credit_points
                        current_value.save()
            elif proceed == 'bulk_sms':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.bulk_sms:
                        current_value.credit_points = current_value.credit_points - (field.bulk_sms * tick)
                        current_value.save()
                        add_transaction(request.user, "Debit", "Bulk SMS", (field.bulk_sms * tick))
                    else:
                        current_value.credit_points = current_value.credit_points
                        current_value.save()
            elif proceed == 'bulk_whatsapp':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.bulk_whatsapp:
                        current_value.credit_points = current_value.credit_points - (field.bulk_whatsapp * tick)
                        current_value.save()
                        add_transaction(request.user, "Debit", "Bulk WhatsApp", (field.bulk_whatsapp * tick))
                    else:
                        current_value.credit_points = current_value.credit_points
                        current_value.save()
            elif proceed == 'bulk_email':
                if current_value.credit_points > insufficient.minimum_points:
                    if current_value.credit_points >= field.bulk_email:
                        current_value.credit_points = current_value.credit_points - (field.bulk_email * tick)
                        current_value.save()
                        add_transaction(request.user, "Debit", "Bulk Email", (field.bulk_email * tick))
                    else:
                        current_value.credit_points = current_value.credit_points
                        current_value.save()
            else:
                current_value.credit_points = current_value.credit_points
                current_value.save()
    available_value = int(current_value.credit_points)
    required_value = int(insufficient.minimum_points)
    return JsonResponse({'available_value': available_value, 'required_value': required_value}, status=200)


def notification(request, slug=None):
   
    firmname = Firmresults.objects.get(firm__slug=slug)
    searchquery = firmname.searchquery.split(",")
    results = {}
    for query in searchquery:
        if query in results:
            results[query] += 1
        else:
            results[query] = 1
 
    # Create a pie chart
    plt.figure(figsize=(5, 5))
    labels = list(results.keys())
    searchcounts = list(results.values())
    plt.pie(searchcounts, labels=labels, autopct='%1.1f%%', startangle=140)
 
    # Convert the pie chart to a base64 encoded image
    pie_buffer = BytesIO()
    plt.savefig(pie_buffer, format='png')
    pie_buffer.seek(0)
    pie_chart_image = base64.b64encode(pie_buffer.read()).decode()
    pie_buffer.close()
 
    # Create a bar graph
    plt.figure(figsize=(7, 4))
    plt.bar(labels, searchcounts)
    plt.xlabel('Search Query')
    plt.ylabel('Searh Count')
 
    # Convert the bar graph to a base64 encoded image
    bar_buffer = BytesIO()
    plt.savefig(bar_buffer, format='png')
    bar_buffer.seek(0)
    bar_chart_image = base64.b64encode(bar_buffer.read()).decode()
    bar_buffer.close()
 
    context = {
        'firm': firmname,
        'pie_chart_image': pie_chart_image,
        'bar_chart_image': bar_chart_image,
    }
    return render(request, 'account/notification.html', context)
 
 
def analytics(request, slug=None):
   
# Get the current date and time
    current_datetime = datetime.now()
    firmname = Task.objects.get(slug=slug)
    # Query the Task model to get search counts grouped by month
    search_counts = firmname.search_count
    view_counts = firmname.view_count
 
    # Calculate total search counts for the month
    # Create a dictionary with the month as the key and the search count as the value
    total_search_count = {}
    # Get all months' names using numbers
    for i in range(1, 13):
        if calendar.month_name[i] == datetime.now().strftime('%B'):
            total_search_count[datetime.now().strftime('%B')] = search_counts
        else:
            total_search_count[calendar.month_name[i]] = 0
 
    total_view_count = {}
    for i in range(1, 13):
        if calendar.month_name[i] == datetime.now().strftime('%B'):
            total_view_count[datetime.now().strftime('%B')] = view_counts
        else:
            total_view_count[calendar.month_name[i]] = 0
 
    # Create a grouped bar chart
    slabels = list(total_search_count.keys())
    vlabels = list(total_view_count.keys())
    bar_width = 0.35
    x = range(len(slabels))
 
    plt.figure(figsize=(16, 6))
    plt.bar(x, list(total_search_count.values()), bar_width, label='Search Counts', color='blue', alpha=0.7)
    plt.bar([i + bar_width for i in x], list(total_view_count.values()), bar_width, label='View Counts', color='green', alpha=0.7)
    plt.xlabel('Month')
    plt.ylabel('Counts')
    plt.title(f'Search and View Counts for {current_datetime.strftime("%B %Y")}')
    plt.xticks([i + bar_width / 2 for i in x], slabels)
    plt.legend()
 
    # Convert the chart to a base64 encoded image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()  # Close the figure to release resources
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.read()).decode()
    buffer.close()
 

    context = {
        'firm': firmname,
        'chart_image': chart_image,
       
    }
    return render(request, 'account/analytics.html', context)

# firm registration
def user_detail_view(request):
    if request.method == 'POST':
        form = UserDetailForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user = request.user
            user.listing_owner = request.user
            user.save()
            form = UserDetailForm()
            messages.success(request,
                             "Your Firm was Registered Successfully. You can see your listings in your Profile Section.")
        else:
            messages.error(request, "Oops! There is an error. Try again.")
    else:
        form = UserDetailForm()

    return render(request, 'user/user_detail.html', {'form': form})


# firm registeration update
def create_business(request, slug=None):
    firm = get_object_or_404(Task, slug=slug)
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES, instance=firm)
        if form.is_valid():
            firm = form.save(commit=False)
            name = form.cleaned_data['name']
            mobile_number = form.cleaned_data['mobile_number']
            city = form.cleaned_data['city']
            email = form.cleaned_data['email']
            firm.save()
            send_ack_sms(mobile_number, name, city)
            ack_email(email, name, city)
            messages.success(request, "Your Firm was Updated Successfully...")
        else:
            messages.error(request, "Oops! There is an error...Try again.")
    else:
        form = BusinessForm(instance=firm)

    context = {'form': form}
    return render(request, 'user/input_form.html', context)


def terms_form(request):
    return render(request, 'user/terms.html')


def privacy_form(request):
    return render(request, 'user/privacy.html')


# AJAX
def load_email(request):
    obj_id = request.GET.get('obj_id')
    firms = Task.objects.filter(pk=obj_id).all()
    return render(request, 'user/ajax_email.html', {'firms': firms})


def load_mobile(request):
    obj_id = request.GET.get('obj_id')
    firms = Task.objects.filter(pk=obj_id).all()
    print(firms)
    return render(request, 'user/ajax_mobile.html', {'firms': firms})


def faqs(request):
    sub = FaqSub.objects.all()
    faq = Faqs.objects.all()
    titles = []
    title = Faqs.objects.values('subject', 'subject_id')
    sub = {item['subject'] for item in title}
    for i in sub:
        scat = Faqs.objects.filter(subject_id=i)
        titles.append(scat)
    context = {'subjects': sub, 'titles': titles}
    return render(request, 'user/faq.html', context)
