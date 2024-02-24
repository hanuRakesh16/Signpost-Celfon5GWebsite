import http.client
import json
from django.urls import include

import requests
import http.client
from crispy_forms.templatetags.crispy_forms_filters import as_crispy_field
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import permission_required
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .forms import *
from todo import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist.')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.has_perm('base.is_media_partner'):
            login(request, user)
            return redirect('tasks')
        else:
            messages.error(request, 'Incorret Username or Password.')
    return render(request, 'base/login.html')
# class CustomLoginView(LoginView):
#     template_name = 'base/login.html'
#     fields = '__all__'
#     redirect_authenticated_user = True

#     def get_success_url(self):
#         return reverse_lazy('tasks')

def logoutUser(request):
    logout(request)
    messages.success(request, 'User was successfully logged out.')
    return redirect('login')
# class CustomLogoutView(LogoutView):
#     next_page = reverse_lazy('login')


def forgot_pwd(request):
    if request.method == 'POST':
        uname = request.POST['username']
        print(uname)
        try:
            get_user = User.objects.get(username=uname)
            if not isValidUsername(get_user.username):
                messages.error(request, 'Username must be your mobile number')
            else:
                request.session['username'] = get_user.id
                send_otp_for_rest_password(get_user)
                return redirect('mp_cnfrm_otp')
                # return redirect('reset_password')
        except Exception as e:
            print('Error', e)
            messages.error(request, 'Username does not exist.')
    return render(request, 'base/forgot_password.html')


def send_otp_for_rest_password(phn_number):
    formatted_phn_number = f"91{phn_number}"

    url = f"https://control.msg91.com/api/v5/otp?mobile={formatted_phn_number}&template_id=64919d76d6fc050fcc155362"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": settings.MGS91_AUTH_KEY
    }
    response = requests.post(url, headers=headers)
    print(phn_number)

def isValidUsername(s):
     
    # 1) Begins with 0 or 91
    # 2) Then contains 6,7 or 8 or 9.
    # 3) Then contains 9 digits
    Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
    return Pattern.match(s)

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
            return redirect('mp_reset_password')
        else:
            messages.error(request, 'Please enter Valid OTP')

    return render(request, 'base/otp_cnfrm.html')


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
        else:
            messages.error(request, "Password is not strong enough.")
    return render(request, 'base/reset_password.html')

def validate_password(password):
    # define our regex pattern for validation
    pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"

    # We use the re.match function to test the password against the pattern
    match = re.match(pattern, password)

    # return True if the password matches the pattern, False otherwise
    return bool(match)

class TaskList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Task
    template_name = 'base/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 50
    # p = Paginator(tasks, 2)
    # page_number = requests.GET.get('page')
    # page_obj = p.get_page(page_number)
    ordering = ['-id']
    permission_required = "base.is_media_partner"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['tasks'] = context['tasks'].all()
        context['nbar'] = 'firm_list'
        return context
    


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'base/task_detail.html'
    context_object_name = 'task'
    permission_required = "base.is_media_partner"


# Define a function to send SMS
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


def send_ack_sms(recipient_mobile, name, city=""):
    url = "https://control.msg91.com/api/v5/flow/"
    payload = {
        "template_id": "652ca4a8d6fc0572b2263e72",
        "short_url": "1 (On) or 0 (Off)",
        "recipients": [
            {
                "mobiles": str(91) + str(recipient_mobile),
                "name": name,
                "city": city
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


def ack_email(email, name, city=''):
    url = "https://control.msg91.com/api/v5/email/send"

    payload = {
        "recipients": [
            {
                "to": [
                    {
                        "name": name,
                        "email": email
                    }
                ],
                "variables": {"VAR1": name, "VAR2": city}
            },
        ],
        "from": {
            "name": "Signpost Celfon5G+",
            "email": "customercare@celfon5g.in"
        },
        "domain": "mail.celfon5g.in",
        "template_id": "cityacknowledgement"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": settings.MGS91_AUTH_KEY
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

def otp_send(request):
    phn_number = request.GET.get('phone_number')
    print(phn_number)
   
    formatted_phn_number = f"91{phn_number}"

    url = f"https://control.msg91.com/api/v5/otp?mobile={formatted_phn_number}&template_id=64919d76d6fc050fcc155362"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey":settings.MGS91_AUTH_KEY
    }
    response = requests.post(url, headers=headers)
    data = response.json()
    print(data)
    print(data.get('type'))
    # print(phn_number)
    #print(response.)
    return render(request,'base/otp_response.html')
    
def verify_otp(request):
        phn_number = request.GET.get('phone_number')
        otp = request.GET.get('otp')
        print(otp)
        formatted_phn_number = f"91{phn_number}"
        url = f"https://control.msg91.com/api/v5/otp/verify?otp={otp}&mobile={formatted_phn_number}"
        headers = {
            "accept": "application/json",
            "authkey": settings.MGS91_AUTH_KEY
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        if data.get('type') == 'success':
            messages.success(request, "OTP verified")
        else:
            messages.error(request, 'Otp is not verified')
        return render(request, 'base/otp_response.html')

@login_required
def adds(request):
    # try:
    form = AddShopForm(request.POST)
    worker = request.user
    FirmProductFormSet = modelformset_factory(EcomProducts, form=EcomProductsForm, extra=0)
    formset = FirmProductFormSet(request.POST, request.FILES, queryset=EcomProducts.objects.none())
    # mobile = request.session['mobile_number']
    # context = {'mobile': mobile}
    # print(mobile)
    context = {
        'form': form,
        # 'form_2': form_2,
        'formset': formset,
        'nbar': 'add_firm_dm'
    }
    if request.method == 'POST':
        income = 0
        form = AddShopForm(request.POST, request.FILES)
        form.instance.user = request.user
        # listing_type = request.POST.get('listing_type')
        name = request.POST.get('name')
        nature = request.POST.get('nature')
        door_no = request.POST.get('door_no')
        building = request.POST.get('building_name')
        street = request.POST.get('street_name')
        state = request.POST.get('state')
        city = request.POST.get('city')
        area = request.POST.get('area')
        district = request.POST.get('district')
        pincode = request.POST.get('pincode')
        landmark = request.POST.get('landmark')
        mobile_number = request.POST.get('mobile_number')
        prefix = request.POST.get('prefix')
        altname = request.POST.get('altname')
        std_code = request.POST.get('std_code')
        landline = request.POST.get('landline')
        email = request.POST.get('email')
        website = request.POST.get('website')
        firm_type = request.POST.get('firm_type')
        gst_no = request.POST.get('gst_no')
        description = request.POST.get('description')
        mc1 = request.POST.get('mcategory1')
        msc1 = request.POST.get('msub_category1')
        mp1 = request.POST.get('mproducts1')
        mtype1 = request.POST.get('mtype1')
        mc2 = request.POST.get('mcategory2')
        msc2 = request.POST.get('msub_category2')
        mp2 = request.POST.get('mproducts2')
        mtype2 = request.POST.get('mtype2')
        mc3 = request.POST.get('mcategory3')
        msc3 = request.POST.get('msub_category3')
        mp3 = request.POST.get('mproducts3')
        mtype3 = request.POST.get('mtype3')
        visiting_card = request.FILES.get('visiting_card')
        logo = request.FILES.get('logo')
        catalogue = request.FILES.get('catalogue')
        video = request.POST.get('video')
        agree = request.POST.get('agree')
        # votp=form.cleaned_data['otp']
        # verified_otp=False
        # if otp:
        #     verified_otp=True

        # Manufacturer Product
        if mp1 != '':
            try:
                Product.objects.get(pk=mp1)
            except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                p = Product(product_name=mp1, category=get_default_category(),
                            sub_category=get_default_sub_category())
                print("p")
                p.save()

        if mp2 != '':
            try:
                Product.objects.get(pk=mp2)
            except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                p1 = Product(product_name=mp2, category=get_default_category(),
                             sub_category=get_default_sub_category())
                print("p1")
                p1.save()

        if mp3 != '':
            try:
                Product.objects.get(pk=mp3)
            except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                p2 = Product(product_name=mp3, category=get_default_category(),
                             sub_category=get_default_sub_category())
                print("p2")
                p2.save()

        if mp1 == '':
            new_product1_id = None
        else:
            try:
                new_product1 = Product.objects.get(product_name=mp1)
            except Product.DoesNotExist:
                new_product1 = Product.objects.get(pk=mp1)

            new_product1_id = new_product1.pk

        if mp2 == '':
            new_product2_id = None
        else:
            try:
                new_product2 = Product.objects.get(product_name=mp2)
            except Product.DoesNotExist:
                new_product2 = Product.objects.get(pk=mp2)

            new_product2_id = new_product2.pk

        if mp3 == '':
            new_product3_id = None
        else:
            try:
                new_product3 = Product.objects.get(product_name=mp3)
            except Product.DoesNotExist:
                new_product3 = Product.objects.get(pk=mp3)

            new_product3_id = new_product3.pk

        # Income calculation
        if name and street and city:
            income += 1
        if email:
            income += 0.5
        if website:
            income += 0.5
        if nature:
            income += 0.5
        if mobile_number:
            income += 0.5
        if landline:
            income += 0.5
        if firm_type:
            income += 0.5
        if gst_no:
            income += 0.5
        if description:
            income += 0.5
        if mp1:
            income += 0.5
        if mp2:
            income += 0.5
        if mp3:
            income += 0.5
        if visiting_card:
            income += 0.5
        if logo:
            income += 0.5
        if catalogue:
            income += 0.5
        if video:
            income += 0.5
        

        # listing_owner = User.objects.create_user(username=mobile_number, email='example@gmail.com', password='signpost#123')

        # FORM SAVE
        new_shop = Task(user=worker, name=name, listing_type='Free', nature=nature, detailType='F', door_no=door_no, area=area, city=city,
                        building_name=building, street_name=street, state_id=state, district_id=district,
                        pincode=pincode, landmark=landmark, mobile_number=mobile_number, prefix=prefix,
                        altname=altname,
                        std_code=std_code,
                        landline=landline, email=email, website=website, description=description,
                        firm_type=firm_type, gst_no=gst_no,
                        mproducts1_id=new_product1_id, mcategory1_id=mc1, msub_category1_id=msc1, mtype1=mtype1,
                        mproducts2_id=new_product2_id, mcategory2_id=mc2, msub_category2_id=msc2, mtype2=mtype2,
                        mproducts3_id=new_product3_id, mcategory3_id=mc3, msub_category3_id=msc3, mtype3=mtype3,
                        visiting_card=visiting_card, logo=logo, catalogue=catalogue, video=video)
        check_data = Task.objects.filter(mobile_number=mobile_number)
        if check_data:
            messages.error(request, 'Firm already exists.')
            return redirect('task-create')
        new_shop.save()
        send_ack_sms(mobile_number, name, city)
        if email:
            ack_email(email, name, city)


        # sms(mobile, promoter, name)
        # send_email()
        # del request.session['mobile_number']
         # Send SMS using the send_sms function


        # try:
        #     if not email and not website and not visiting_card and not video:
        #         income = 5
        #         print(income)
        #         a = Income.objects.get(worker=worker)
        #         a.income_amount += income
        #         a.save()
        #         o = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         o.save()
        #     elif not website and not visiting_card and not video:
        #         income = 6
        #         print(income)
        #         b = Income.objects.get(worker=worker)
        #         b.income_amount += income
        #         b.save()
        #         p = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         p.save()
        #     elif not email and not visiting_card and not video:
        #         income = 6
        #         print(income)
        #         c = Income.objects.get(worker=worker)
        #         c.income_amount += income
        #         c.save()
        #         q = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         q.save()
        #     elif not website and not email and not video:
        #         income = 6
        #         print(income)
        #         d = Income.objects.get(worker=worker)
        #         d.income_amount += income
        #         d.save()
        #         r = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         r.save()
        #     elif not website and not visiting_card and not email:
        #         income = 6
        #         print(income)
        #         e = Income.objects.get(worker=worker)
        #         e.income_amount += income
        #         e.save()
        #         s = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         s.save()
        #     elif not visiting_card and not video:
        #         income = 7
        #         print(income)
        #         f = Income.objects.get(worker=worker)
        #         f.income_amount += income
        #         f.save()
        #         t = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         t.save()
        #     elif not website and not email:
        #         income = 7
        #         print(income)
        #         g = Income.objects.get(worker=worker)
        #         g.income_amount += income
        #         g.save()
        #         u = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         u.save()
        #     elif not email and not video:
        #         income = 7
        #         print(income)
        #         h = Income.objects.get(worker=worker)
        #         h.income_amount += income
        #         h.save()
        #         v = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         v.save()
        #     elif not website and not video:
        #         income = 7
        #         print(income)
        #         i = Income.objects.get(worker=worker)
        #         i.income_amount += income
        #         i.save()
        #         w = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         w.save()
        #     elif not email:
        #         income = 8
        #         print('email')
        #         print(income)
        #         j = Income.objects.get(worker=worker)
        #         j.income_amount += income
        #         j.save()
        #         x = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         x.save()
        #     elif verified_otp:
        #         income = 2
        #         print(income)
        #         i = Income.objects.get(worker=worker)
        #         i.income_amount += income
        #         i.save()
        #         w = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         w.save()
        #     elif not website:
        #         income = 8
        #         print(income)
        #         print('website')
        #         k = Income.objects.get(worker=worker)
        #         k.income_amount += income
        #         k.save()
        #         y = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         y.save()
        #     elif not visiting_card:
        #         income = 8
        #         print(income)
        #         print('visiting_card')
        #         l = Income.objects.get(worker=worker)
        #         l.income_amount += income
        #         l.save()
        #         z = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         z.save()
        #     elif not video:
        #         income = 8
        #         print('video')
        #         print(income)
        #         m = Income.objects.get(worker=worker)
        #         m.income_amount += income
        #         m.save()
        #         aa = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         aa.save()
        #     else:
        #         income = 10
        #         print(income)
        #         print('all')
        #         n = Income.objects.get(worker=worker)
        #         n.income_amount += income
        #         n.save()
        #         bb = WorkSummary(mp=worker, firm_name=new_shop, income=income)
        #         bb.save()
        # except TypeError:
        #     pass
        for form in formset:
            child = form.save(commit=False)
            child.firm_name = new_shop
            mp = WorkSummary.objects.get(firm_name=new_shop)
            mp.income += 5
            mp.save()
            child.save()

            print("saved ")
        income_user = Income.objects.get(worker=request.user)
        income_user.income_amount += income
        income_user.save()
        inc_summary = WorkSummary(mp=request.user, firm_name=new_shop, income=income)
        inc_summary.save()
        # form.save()
        # if email:
        #     email_from = settings.EMAIL_HOST_USER
        #     recipient_list = [email]
        #     subject = 'Registered Successfully!'
        #     message = f'hi {name}'
        #     send_mail(
        #         subject,
        #         message,
        #         email_from,
        #         recipient_list,
        #         fail_silently=False
        #     )
        # else:
        #     pass
        # request.session.delete('mobile_number')
        return redirect('tasks')
    else:
        return render(request, 'base/task_form.html', context)
    # except KeyError:
    #     return redirect('register')
    return render(request, 'base/task_form.html', context)


def referral(request):
    # try:
    profile_id = request.session.get('ref_profile')
    print('profile_id', profile_id)
    form = AddShopForm(request.POST)
    if not profile_id:
        return HttpResponse("403 Forbidden.")
    # worker = request.user
    FirmProductFormSet = modelformset_factory(EcomProducts, form=EcomProductsForm, extra=0)
    formset = FirmProductFormSet(request.POST, request.FILES, queryset=EcomProducts.objects.none())
    # mobile = request.session['mobile_number']
    # context = {'mobile': mobile}
    # print(mobile)
    context = {
        'form': form,
        # 'form_2': form_2,
        'formset': formset,
    }
    if request.method == 'POST':
        if profile_id is not None:
            worker = User.objects.get(id=profile_id)
            print("worker", worker)
            form = AddShopForm(request.POST, request.FILES)
            # user = request.POST.get('referred')
            # form.instance.user = request.user
            # listing_type=request.POST.get('listing_type')
            name = request.POST.get('name')
            nature = request.POST.get('nature')
            door_no = request.POST.get('door_no')
            building = request.POST.get('building_name')
            street = request.POST.get('street_name')
            state = request.POST.get('state')
            city = request.POST.get('city')
            area = request.POST.get('area')
            district = request.POST.get('district')
            pincode = request.POST.get('pincode')
            landmark = request.POST.get('landmark')
            mobile_number = request.POST.get('mobile_number')
            prefix = request.POST.get('prefix')
            altname = request.POST.get('altname')
            std_code = request.POST.get('std_code')
            landline = request.POST.get('landline')
            email = request.POST.get('email')
            website = request.POST.get('website')
            firm_type = request.POST.get('firm_type')
            description = request.POST.get('description')
            mc1 = request.POST.get('mcategory1')
            msc1 = request.POST.get('msub_category1')
            mp1 = request.POST.get('mproducts1')
            mtype1 = request.POST.get('mtype1')
            mc2 = request.POST.get('mcategory2')
            msc2 = request.POST.get('msub_category2')
            mp2 = request.POST.get('mproducts2')
            mtype2 = request.POST.get('mtype2')
            mc3 = request.POST.get('mcategory3')
            msc3 = request.POST.get('msub_category3')
            mp3 = request.POST.get('mproducts3')
            mtype3 = request.POST.get('mtype3')
            visiting_card = request.FILES.get('visiting_card')
            logo = request.FILES.get('logo')
            catalogue = request.FILES.get('catalogue')
            video = request.POST.get('video')
           

            # Manufacturer Product
            if mp1 != '':
                try:
                    Product.objects.get(pk=mp1)
                except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                    p = Product(product_name=mp1, category=get_default_category(),
                                sub_category=get_default_sub_category())
                    print("p")
                    p.save()

            if mp2 != '':
                try:
                    Product.objects.get(pk=mp2)
                except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                    p1 = Product(product_name=mp2, category=get_default_category(),
                                 sub_category=get_default_sub_category())
                    print("p1")
                    p1.save()

            if mp3 != '':
                try:
                    Product.objects.get(pk=mp3)
                except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                    p2 = Product(product_name=mp3, category=get_default_category(),
                                 sub_category=get_default_sub_category())
                    print("p2")
                    p2.save()

            if mp1 == '':
                new_product1_id = None
            else:
                try:
                    new_product1 = Product.objects.get(product_name=mp1)
                except Product.DoesNotExist:
                    new_product1 = Product.objects.get(pk=mp1)

                new_product1_id = new_product1.pk

            if mp2 == '':
                new_product2_id = None
            else:
                try:
                    new_product2 = Product.objects.get(product_name=mp2)
                except Product.DoesNotExist:
                    new_product2 = Product.objects.get(pk=mp2)

                new_product2_id = new_product2.pk

            if mp3 == '':
                new_product3_id = None
            else:
                try:
                    new_product3 = Product.objects.get(product_name=mp3)
                except Product.DoesNotExist:
                    new_product3 = Product.objects.get(pk=mp3)

                new_product3_id = new_product3.pk

            # listing_owner = User.objects.create_user(username=mobile_number, email='example@gmail.com', password='signpost#123')
            # FORM SAVE
            new_shop = Task(user=worker, name=name,  listing_type='Free', nature=nature, detailType='F', door_no=door_no, area=area, city=city,
                        building_name=building, street_name=street, state_id=state, 
                        
                        trict_id=district,
                        pincode=pincode, landmark=landmark, mobile_number=mobile_number, prefix=prefix,
                        altname=altname,
                        std_code=std_code,
                        landline=landline, email=email, website=website, description=description,
                        firm_type=firm_type,
                        mproducts1_id=new_product1_id, mcategory1_id=mc1, msub_category1_id=msc1, mtype1=mtype1,
                        mproducts2_id=new_product2_id, mcategory2_id=mc2, msub_category2_id=msc2, mtype2=mtype2,
                        mproducts3_id=new_product3_id, mcategory3_id=mc3, msub_category3_id=msc3, mtype3=mtype3,
                        referred_by=worker,
                        visiting_card=visiting_card, logo=logo, catalogue=catalogue, video=video)
            check_data = Task.objects.filter(mobile_number=mobile_number)
            if check_data:
                messages.error(request, 'Firm already exists.')
                return redirect('referral')
            new_shop.save()
            send_ack_sms(mobile_number, name, city)
            if email:
                ack_email(email, name, city)


        # del request.session['mobile_number']
            try:
                if not email and not website and not visiting_card and not video:
                    income = 5
                    print(income)
                    a = Income.objects.get(worker=worker)
                    a.income_amount += income
                    a.save()
                    o = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    o.save()
                elif not website and not visiting_card and not video:
                    income = 6
                    print(income)
                    b = Income.objects.get(worker=worker)
                    b.income_amount += income
                    b.save()
                    p = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    p.save()
                elif not email and not visiting_card and not video:
                    income = 6
                    print(income)
                    c = Income.objects.get(worker=worker)
                    c.income_amount += income
                    c.save()
                    q = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    q.save()
                elif not website and not email and not video:
                    income = 6
                    print(income)
                    d = Income.objects.get(worker=worker)
                    d.income_amount += income
                    d.save()
                    r = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    r.save()
                elif not website and not visiting_card and not email:
                    income = 6
                    print(income)
                    e = Income.objects.get(worker=worker)
                    e.income_amount += income
                    e.save()
                    s = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    s.save()
                elif not visiting_card and not video:
                    income = 7
                    print(income)
                    f = Income.objects.get(worker=worker)
                    f.income_amount += income
                    f.save()
                    t = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    t.save()
                elif not website and not email:
                    income = 7
                    print(income)
                    g = Income.objects.get(worker=worker)
                    g.income_amount += income
                    g.save()
                    u = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    u.save()
                elif not email and not video:
                    income = 7
                    print(income)
                    h = Income.objects.get(worker=worker)
                    h.income_amount += income
                    h.save()
                    v = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    v.save()
                elif not website and not video:
                    income = 7
                    print(income)
                    i = Income.objects.get(worker=worker)
                    i.income_amount += income
                    i.save()
                    w = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    w.save()
                elif not email:
                    income = 8
                    print('email')
                    print(income)
                    j = Income.objects.get(worker=worker)
                    j.income_amount += income
                    j.save()
                    x = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    x.save()
                elif not website:
                    income = 8
                    print(income)
                    print('website')
                    k = Income.objects.get(worker=worker)
                    k.income_amount += income
                    k.save()
                    y = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    y.save()
                elif not visiting_card:
                    income = 8
                    print(income)
                    print('visiting_card')
                    l = Income.objects.get(worker=worker)
                    l.income_amount += income
                    l.save()
                    z = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    z.save()
                elif not video:
                    income = 8
                    print('video')
                    print(income)
                    m = Income.objects.get(worker=worker)
                    m.income_amount += income
                    m.save()
                    aa = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    aa.save()
                else:
                    income = 10
                    print(income)
                    print('all')
                    n = Income.objects.get(worker=worker)
                    n.income_amount += income
                    n.save()
                    bb = WorkSummary(mp=worker, firm_name=new_shop, income=income)
                    bb.save()
            except TypeError:
                pass
            for form in formset:
                child = form.save(commit=False)
                child.firm_name = new_shop
                mp = WorkSummary.objects.get(firm_name=new_shop)
                mp.income += 5
                mp.save()
                child.save()

                print("saved ")
            else:
                pass

        # form.save()
        # if email:
        #     email_from = settings.EMAIL_HOST_USER
        #     recipient_list = [email]
        #     subject = 'Registered Successfully!'
        #     message = f'hi {name}'
        #     send_mail(
        #         subject,
        #         message,
        #         email_from,
        #         recipient_list,
        #         fail_silently=False
        #     )
        # else:
        #     pass

        # return redirect('tasks')
        messages.error(request, 'Form submission successful')
        # request.session.delete('ref_profile')
        del request.session['ref_profile']
    else:
        return render(request, 'base/referral_form.html', context)
    # except KeyError:
    #     return redirect('register')
    return render(request, 'base/referral_form.html', context)


def get_referred_firms_view(request):
    qs = Task.objects.all().filter(referred_by=request.user).order_by('-id')
    # my_recs = [p for p in qs if p.recommended_by == self.user]
    query = Teams.objects.all().filter(team_leader=request.user).order_by('-id')
    my_recs = []
    my_teams = []
    for profile in qs:
        my_recs.append(profile)
    for teams in query:
        my_teams.append(teams)
    context = {'my_recs': my_recs, 'my_teams': my_teams, 'nbar': 'referrals'}
    return render(request, 'base/ref.html', context)


def main_view(request, *args, **kwargs):
    code = str(kwargs.get('ref_code'))
    try:
        profile = User.objects.get(username=code)
        request.session['ref_profile'] = profile.id
        print('id', profile.id)
    except:
        return HttpResponse('Invalid Referral Code')
    print(request.session.get_expiry_age())
    return render(request, 'base/r1.html')

def send_email(subject, message, from_email, recipient_list):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(recipient_list)
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(from_email, recipient_list, msg.as_string())
        server.quit()
    except Exception as e:
        # Handle email sending error
        print(f"Email sending failed with error: {e}")
        return False
    return True


@login_required
def basic_form(request):
    # form = BasicForm()
    if request.method == 'POST':
        form = BasicForm(request.POST, request.FILES)
        income = 0
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        logo = request.FILES.get('logo')
        email = request.POST.get('email')
        city = request.POST.get('city')
        desc = request.POST.get('description')
        if name and city and mobile_number:
            income += 1
        if email:
            income += 0.5
        if desc:
            income += 0.5
        if logo is not None:
            income += 1
        print("logo", logo)
        if form.is_valid():
            user = form.save(commit=False)
            user.user = request.user
            user.detailType = 'F'
            mobile_number = form.cleaned_data['mobile_number']
            name = form.cleaned_data['name']
            # email = form.cleaned_data['email']
            # city = form.cleaned_data['city']
            # description = form.cleaned_data['description']
            # logo = form.cleaned_data['logo']
            # votp=form.cleaned_data['otp']
            # verified_otp = False
            # otp_send(mobile_number)
            # otp=verify_otp(mobile_number,votp)
            # if otp:
            #     verified_otp=True
            check_data = Task.objects.filter(mobile_number=mobile_number)
            if check_data:
                messages.error(request, 'Firm already exists.')
                return redirect('tasks')
            user.save() 

            income_user = Income.objects.get(worker=request.user)
            income_user.income_amount += income
            income_user.save()
            inc_summary = WorkSummary(mp=request.user, firm_name=user, income=income)
            inc_summary.save()
            form = BasicForm()
            messages.success(request, "Your details were saved Successfully")

            # Send SMS using the send_sms function
            send_ack_sms(mobile_number, name, city)
            if email:
                ack_email(email, name, city)
       
        else:
            messages.error(request, "Oops! There is an error. Try again.")
    else:
        form = BasicForm()
    return render(request, 'base/basicform.html', {'form': form, 'nbar': 'add_firm_tm'})

def otp(request):
    mobile = request.session['mobile_number']
    context = {'mobile': mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()

        if otp == profile.otp:
            return redirect('task-create')
        else:
            context = {'message': 'Invalid', 'class': 'danger', 'mobile': mobile}
            return render(request, 'base/otp.html', context)

    return render(request, 'base/otp.html', context)


# def confirm(promoter, name, mobile):
#     print("FUNCTION CALLED")
#     account_sid = ''
#     auth_token = ''
#     client = Client(account_sid, auth_token)

#     message = client.messages.create(
#         from_='whatsapp:+14155238886',
#         body='Your {} code is {}'.format(promoter, name),
#         to='whatsapp:+91{}'.format(mobile)
#     )
#     print(message.sid)
#     return None


def send_otp(mobile, otp):
    print("FUNCTION CALLED")
    conn = http.client.HTTPSConnection("api.msg91.com")
    authkey = ''
    headers = {
        'content-type': "application/JSON"
    }
    url = "http://control.msg91.com/api/sendotp.php?otp=" + otp + "&message=" + "Your otp is " + otp + "&mobile=" + mobile + "&authkey=" + authkey + "&country=91"
    url = url.replace(" ", "")
    conn.request("POST", url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data)
    return None


def register(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        def isValid(s):
            Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
            return Pattern.match(s)
        if isValid(mobile):
            pass
        else:
            context = {'message': 'Please enter a valid mobile number', 'class': 'danger'}
            return render(request, 'base/register.html', context)
        # check_user = User.objects.filter(email=email).first()
        check_profile = Profile.objects.filter(mobile=mobile).first()
        if check_profile:
            context = {'message': 'User already exists', 'class': 'danger'}
            return render(request, 'base/register.html', context)

        # user = User(email=email, first_name=name)
        # user.save()
        otp = str(random.randint(100000, 999999))
        profile = Profile(mobile=mobile, otp=otp)
        profile.save()
        send_otp(mobile, otp)
        request.session['mobile_number'] = mobile
        return redirect('otp')
    return render(request, 'base/register.html')

@login_required
def work(request):
    user = request.user
    blworker = BusinessListingIncome.objects.filter(user=user).last()
    bltotal = BusinessListingIncomeDelivery.objects.filter(user=user).last()
    
    worker = Income.objects.filter(worker=user).last()
    # for add firm total
    summary = WorkSummary.objects.all().filter(mp=user).order_by('-id')[:50]
    blsummary = BusinessListing.objects.all().filter(user=user).order_by('-id')[:50]
    # For add person 
    individualincome = IndividualIncome.objects.all().filter(user=user).order_by('-id')[:50]
    individualtotal = IndividualTotalIncome.objects.filter(user=user).last()
    try:
        pass
    except AttributeError:
        pass
    context = {'user': user, 'worker': worker, 'summary': summary, 'blsummary': blsummary, 'blworker': blworker, 'bltotal': bltotal, 'individualincome': individualincome, 'individualtotal': individualtotal, 'nbar': 'earnings'}
    return render(request, 'base/income.html', context)


def check_bname(request):
    form = AddShopForm(request.GET)
    return HttpResponse(as_crispy_field(form['business_name']))


# AJAX
def load_cities(request):
    country_id = request.GET.get('region_id')
    cities = SubRegion.objects.filter(region_id=country_id).all()
    return render(request, 'base/city_dropdown_list_options.html', {'cities': cities})


def load_cat(request):
    product_id = request.GET.get('product_id')
    sub = Sub_category.objects.filter(product=product_id)
    return render(request, 'base/load_cat.html', {'sub': sub})


def load_p(request):
    pr_id = request.GET.get('pr_id')
    product = Category.objects.filter(product=pr_id)
    return render(request, 'base/load_p.html', {'product': product})


def check_mobile_if_already_exists(request):
    mobile = request.GET.get('mobile')
    data = ''
    try:
        firm = Task.objects.filter(mobile_number=mobile).first()
        data = 'This Mobile number is already registered with firm named : ' + firm.name
    except Exception as e:
        data = ''
    
    return JsonResponse(data, safe=False)

def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get['term']
        qs = Product.objects.filter(product_name__startswith=request.GET.get['term'])
        titles = list()
        for q in qs:
            titles.append(q.product_name)
        return JsonResponse(titles, safe=False)


def verify(request):
    mobile = request.GET.get("number")
    check_profile = Profile.objects.filter(mobile=mobile).first()
    if check_profile:
        messages.error(request, 'Mobile number is already exists.')
        return redirect('task-create')
    else:
        otp = str(random.randint(100000, 999999))
        profile = Profile(mobile=mobile, otp=otp)
        profile.save()
        send_otp(mobile, otp)
        request.session['mobile_number'] = mobile
    return HttpResponse(otp)


# ad
def create_ad(request):
    context = {'nbar': 'adv'}
    return render(request, 'base/create_ad.html', context)

def list_ad(request):
    ads = Advertisement.objects.filter(user=request.user.id)
    context = {'ads': ads, 'nbar': 'adv'}
    return render(request, 'base/list_ad.html', context)

def update_ad(request, slug=None):
    ad = Advertisement.objects.get(slug=slug)
    if request.method == 'POST':
        form = CreateAdForm(request.POST, instance=ad)
        if form.is_valid():
            # update the existing `Band` in the database
            form.save()
            # redirect to the detail page of the `Band` we just updated
            return redirect('list-ad')
    else:
        form = CreateAdForm(instance=ad)

    context = {'form': form, 'ad': ad}
    return render(request, 'base/update_ad.html', context)


def newad(request):
    form = CreateAdForm(request.POST)
    if request.method == 'POST':
        user = request.user
        pink_pg_title = request.POST.get('ping_pg_title')
        business_name = request.POST.get('business_name')
        slogan = request.POST.get('slogan')
        door_st = request.POST.get('door_st')
        city = request.POST.get('city')
        landline = request.POST.get('landline')
        mobile = request.POST.get('mobile')
        whatsapp = request.POST.get('whatsapp')
        email = request.POST.get('email')
        website = request.POST.get('website')
        fp_name = request.POST.get('fp_name')
        fp_number = request.POST.get('fp_number')
        sp_name = request.POST.get('sp_name')
        sp_number = request.POST.get('sp_number')
        tp_name = request.POST.get('tp_name')
        tp_number = request.POST.get('tp_number')
        f_activity = request.POST.get('f_activity')
        s_activity = request.POST.get('s_activity')

        new_ad = Advertisement(user=request.user, pink_pg_title=pink_pg_title, business_name=business_name,
                               slogan=slogan, door_street=door_st, city_pincode=city, landline=landline,
                               mobile=mobile, whatsapp=whatsapp, email=email, website=website, name_desg1=fp_name,
                               number1=fp_number, name_desg2=sp_name, number2=sp_number, name_desg3=tp_name,
                               number3=tp_number, activity1=f_activity, activity2=s_activity)
        new_ad.save()
        return redirect('list-ad')
    context = {'form': form}
    return render(request, 'base/newad.html', context)


def order_confirm(request):
    form = BusinessListingForm(request.POST, request.FILES)
    context = {'form': form, 'nbar': 'order_booking'}
    if form.is_valid():
        amount = form.cleaned_data['amount']
        # payment_mode = form.cleaned_data['payment_mode']
        # print(amount, payment_mode)
        obj = form.save(commit=False)
        # if payment_mode == 'CASH':
        #     blincome = BusinessListingIncomeDelivery.objects.get(user=request.user)
        #     blincome.total += amount
        #     blincome.save()
        income = (amount / 100) * 15
        blcommission = BusinessListingIncome.objects.get(user=request.user)
        blcommission.total += income
        blcommission.save()
        obj.user = request.user
        obj.income = income
        obj.save()
        return redirect('tasks')
    return render(request, 'base/order_confirm.html', context)


def individual(request):
    form = IndividualForm(request.POST, request.FILES)
    if request.method == 'POST':
        income = 0
        prefix = request.POST.get('prefix')
        name = request.POST.get('name')
        logo = request.FILES.get('logo')
        door = request.POST.get('door_no')
        street = request.POST.get('street_name')
        building = request.POST.get('building_name')
        area = request.POST.get('area')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        state = request.POST.get('state')
        district = request.POST.get('district')
        pincode = request.POST.get('pincode')
        blood_donor = request.POST.get('blood_donor')
        blood_group = request.POST.get('blood_group')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        website = request.POST.get('website')
        mc1 = request.POST.get('mcategory1')
        msc1 = request.POST.get('msub_category1')
        profession = request.POST.get('mproducts1')
        altname = request.POST.get('altname')
        firm_type = request.POST.get('firm_type')
        nature = request.POST.get('nature')
        description = request.POST.get('description')
        year_of_birth = request.POST.get('year_of_birth')
        gender = request.POST.get('gender')
        martial_status = request.POST.get('martial_status')
        education = request.POST.get('education')
        employment = request.POST.get('employment')
        responsibility = request.POST.get('responsibility')
        data_income = request.POST.get('income')
        hobbies = request.POST.get('hobbies')
        visiting_card = request.FILES.get('visiting_card')

        if profession != '':
                try:
                    Product.objects.get(pk=profession)
                except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                    p = Product(product_name=profession, category=get_default_category(),
                                sub_category=get_default_sub_category())
                    p.save()

        if profession == '':
                new_product1_id = None
        else:
            try:
                new_product1 = Product.objects.get(product_name=profession)
            except Product.DoesNotExist:
                new_product1 = Product.objects.get(pk=profession)

            new_product1_id = new_product1.pk

        # listing_owner = User.objects.create_user(username=mobile_number, email='example@gmail.com', password='signpost#123')

        if name and street and pincode:
            income += 1
        if blood_donor:
            income += 0.5
        if mobile_number:
            income += 0.5
        if email:
            income += 0.5
        if website:
            income += 0.5
        if description:
            income += 0.5
        if mc1:
            income += 0.5
        if year_of_birth:
            income += 0.5
        if martial_status:
            income += 0.5
        if gender:
            income += 0.5
        if education:
            income += 0.5
        if employment:
            income += 0.5
        if data_income:
            income += 0.5
        if responsibility:
            income += 0.5
        if hobbies:
            income += 0.5
        if visiting_card:
            income += 0.5
        new_person = Task(user=request.user, prefix=prefix, name=name, listing_type='Free', logo=logo, detailType='P', door_no=door, street_name=street,
                                building_name=building, area=area, landmark=landmark, city=city, state_id=state,
                                district_id=district, pincode=pincode, blood_donor=blood_donor, blood_group=blood_group,
                                mobile_number=mobile_number, email=email, website=website,  description=description, mcategory1_id=mc1, msub_category1_id=msc1, mproducts1_id=new_product1_id, altname=altname, firm_type=firm_type,nature=nature,
                                year_of_birth=year_of_birth, martial_status=martial_status, gender=gender, education=education,
                                employment=employment, income=data_income, responsibility=responsibility, hobbies=hobbies,
                                visiting_card=visiting_card)
        check_data = Task.objects.filter(name=name, mobile_number=mobile_number)
        if check_data:
            messages.error(request, 'Person already exists.')
            return redirect('individual')
        
        new_person.save()
        field_income = IndividualIncome(user=request.user, name=name, total_fields=0, income=income)
        field_income.save()
        total_field_income = IndividualTotalIncome.objects.get(user=request.user)
        total_field_income.total_income += income
        total_field_income.save()
        # send_login_sms(mobile_number)
        # if email:
        #     ack_email(email, name, city)

        # if profession and email and education and income and visiting_card:
        #     field_income1 = IndividualIncome(user=request.user, name=name, total_fields=0, income=5)
        #     field_income1.save()
        #     total_field_income1 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income1.total_income += 5
        #     total_field_income1.save()
        # elif profession and email and visiting_card:
        #     field_income3 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
        #     field_income3.save()
        #     total_field_income3 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income3.total_income += 4
        #     total_field_income3.save()
        # elif profession and email and education and income:
        #     field_income4 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
        #     field_income4.save()
        #     total_field_income4 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income4.total_income += 4
        #     total_field_income4.save()
        # elif profession and education and income and visiting_card:
        #     field_income5 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
        #     field_income5.save()
        #     total_field_income5 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income5.total_income += 4
        #     total_field_income5.save()
        # elif email and education and income and visiting_card:
        #     field_income6 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
        #     field_income6.save()
        #     total_field_income6 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income6.total_income += 4
        #     total_field_income6.save()
        # elif profession and email:
        #     field_income7 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
        #     field_income7.save()
        #     total_field_income7 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income7.total_income += 3
        #     total_field_income7.save()
        # elif education and income and visiting_card:
        #     field_income8 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
        #     field_income8.save()
        #     total_field_income8 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income8.total_income += 3
        #     total_field_income8.save()
        # elif profession and education and income:
        #     field_income9 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
        #     field_income9.save()
        #     total_field_income9 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income9.total_income += 3
        #     total_field_income9.save()
        # elif profession and visiting_card:
        #     field_income0 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
        #     field_income0.save()
        #     total_field_income0 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income0.total_income += 3
        #     total_field_income0.save()
        # elif email and visiting_card:
        #     field_income11 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
        #     field_income11.save()
        #     total_field_income11 = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income11.total_income += 3
        #     total_field_income11.save()
        # else:
        #     field_income = IndividualIncome(user=request.user, name=name, total_fields=0, income=1)
        #     field_income.save()
        #     total_field_income = IndividualTotalIncome.objects.get(user=request.user)
        #     total_field_income.total_income += 1
        #     total_field_income.save()
        # print("empty values ", empty_values_count)
        return redirect('tasks')
    context = {'form': form, 'nbar': 'add_person'}
    return render(request, 'base/individual.html', context)


def ref_individual(request):
    profile_id = request.session.get('ref_profile')
    form = IndividualForm(request.POST, request.FILES)
    if not profile_id:
        return HttpResponse("403 Forbidden.")
    if request.method == 'POST':
        if profile_id is not None:
            income = 0
            worker = User.objects.get(id=profile_id)
            form = IndividualForm(request.POST, request.FILES)
            print("worker", worker)
            # if form.is_valid():
            # listing_type = request.POST.get('listing_type')
            prefix = request.POST.get('prefix')
            name = request.POST.get('name')
            logo = request.FILES.get('logo')
            door = request.POST.get('door_no')
            street = request.POST.get('street_name')
            building = request.POST.get('building_name')
            area = request.POST.get('area')
            landmark = request.POST.get('landmark')
            city = request.POST.get('city')
            state = request.POST.get('state')
            district = request.POST.get('district')
            pincode = request.POST.get('pincode')
            blood_donor = request.POST.get('blood_donor')
            blood_group = request.POST.get('blood_group')
            mobile_number = request.POST.get('mobile_number')
            email = request.POST.get('email')
            website = request.POST.get('website')
            mc1 = request.POST.get('mcategory1')
            msc1 = request.POST.get('msub_category1')
            profession = request.POST.get('mproducts1')
            altname = request.POST.get('altname')
            firm_type = request.POST.get('firm_type')
            nature = request.POST.get('nature')
            description = request.POST.get('description')
            year_of_birth = request.POST.get('year_of_birth')
            gender = request.POST.get('gender')
            martial_status = request.POST.get('martial_status')
            education = request.POST.get('education')
            employment = request.POST.get('employment')
            responsibility = request.POST.get('responsibility')
            data_income = request.POST.get('income')
            hobbies = request.POST.get('hobbies')
            visiting_card = request.FILES.get('visiting_card')
            # fields = [name, door, street, building, locality, landmark, city, state, district, pincode, blood_group,
            #           mobile_number, email, about, year_of_birth, gender, martial_status, education, employment,
            #           responsibility, income, hobbies]
            # empty_values = {"", None}
            # empty_values_count = 0
            # for field in fields:
            #     if field in empty_values:
            #         empty_values_count += 1

            # individual_income = ((23 - empty_values_count) * 2)
            # total_fields = (23 - empty_values_count)

            if profession != '':
                try:
                    Product.objects.get(pk=profession)
                except (ObjectDoesNotExist, Product.DoesNotExist, ValueError):
                    p = Product(product_name=profession, category=get_default_category(),
                                sub_category=get_default_sub_category())
                    p.save()

            if profession == '':
                    new_product1_id = None
            else:
                try:
                    new_product1 = Product.objects.get(product_name=profession)
                except Product.DoesNotExist:
                    new_product1 = Product.objects.get(pk=profession)

                new_product1_id = new_product1.pk

            # listing_owner = User.objects.create_user(username=mobile_number, email='example@gmail.com', password='signpost#123')

            new_person = Task(user=worker, prefix=prefix, name=name,  listing_type='Free', logo=logo, detailType='P', door_no=door, street_name=street,
                                building_name=building, area=area, landmark=landmark, city=city, state_id=state,
                                district_id=district, pincode=pincode, blood_donor=blood_donor, blood_group=blood_group,
                                mobile_number=mobile_number, email=email, website=website,  description=description, mcategory1_id=mc1, msub_category1_id=msc1, mproducts1_id=new_product1_id, altname=altname, firm_type=firm_type,nature=nature,
                                year_of_birth=year_of_birth, martial_status=martial_status, gender=gender, education=education,
                                employment=employment, income=data_income, responsibility=responsibility, hobbies=hobbies,
                                visiting_card=visiting_card, referred_by=worker,)
            new_person.save()

            if name and street and pincode:
                income += 1
            if blood_donor:
                income += 0.5
            if mobile_number:
                income += 0.5
            if email:
                income += 0.5
            if website:
                income += 0.5
            if description:
                income += 0.5
            if mc1:
                income += 0.5
            if year_of_birth:
                income += 0.5
            if martial_status:
                income += 0.5
            if gender:
                income += 0.5
            if education:
                income += 0.5
            if employment:
                income += 0.5
            if data_income:
                income += 0.5
            if responsibility:
                income += 0.5
            if hobbies:
                income += 0.5
            if visiting_card:
                income += 0.5

            field_income = IndividualIncome(user=request.user, name=name, total_fields=0, income=income)
            field_income.save()
            total_field_income = IndividualTotalIncome.objects.get(user=request.user)
            total_field_income.total_income += income
            total_field_income.save()
            
            send_ack_sms(mobile_number, name, city)
            if email:
                ack_email(email, name, city)
            # if profession and email and education and income and visiting_card:
            #     field_income1 = IndividualIncome(user=request.user, name=name, total_fields=0, income=5)
            #     field_income1.save()
            #     total_field_income1 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income1.total_income += 5
            #     total_field_income1.save()
            # elif profession and email and visiting_card:
            #     field_income3 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
            #     field_income3.save()
            #     total_field_income3 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income3.total_income += 4
            #     total_field_income3.save()
            # elif profession and email and education and income:
            #     field_income4 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
            #     field_income4.save()
            #     total_field_income4 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income4.total_income += 4
            #     total_field_income4.save()
            # elif profession and education and income and visiting_card:
            #     field_income5 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
            #     field_income5.save()
            #     total_field_income5 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income5.total_income += 4
            #     total_field_income5.save()
            # elif email and education and income and visiting_card:
            #     field_income6 = IndividualIncome(user=request.user, name=name, total_fields=0, income=4)
            #     field_income6.save()
            #     total_field_income6 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income6.total_income += 4
            #     total_field_income6.save()
            # elif profession and email:
            #     field_income7 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
            #     field_income7.save()
            #     total_field_income7 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income7.total_income += 3
            #     total_field_income7.save()
            # elif education and income and visiting_card:
            #     field_income8 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
            #     field_income8.save()
            #     total_field_income8 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income8.total_income += 3
            #     total_field_income8.save()
            # elif profession and education and income:
            #     field_income9 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
            #     field_income9.save()
            #     total_field_income9 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income9.total_income += 3
            #     total_field_income9.save()
            # elif profession and visiting_card:
            #     field_income0 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
            #     field_income0.save()
            #     total_field_income0 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income0.total_income += 3
            #     total_field_income0.save()
            # elif email and visiting_card:
            #     field_income11 = IndividualIncome(user=request.user, name=name, total_fields=0, income=3)
            #     field_income11.save()
            #     total_field_income11 = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income11.total_income += 3
            #     total_field_income11.save()
            # else:
            #     field_income = IndividualIncome(user=request.user, name=name, total_fields=0, income=1)
            #     field_income.save()
            #     total_field_income = IndividualTotalIncome.objects.get(user=request.user)
            #     total_field_income.total_income += 1
            #     total_field_income.save()
            messages.error(request, 'Form submission successful')
            del request.session['ref_profile']
        else:
            return render(request, 'base/ref_individual.html')
    context = {'form': form}
    return render(request, 'base/ref_individual.html', context)\
    

