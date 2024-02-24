
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from base.models import *
from user.models import *


class CutsomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'username': 'Mobile Number',
        }
    def __init__(self, *args, **kwargs):
        super(CutsomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})

class signForm(forms.Form):
    first_name = forms.CharField(label="first name", max_length=100)
    last_name = forms.CharField(label="last name", max_length=100)
    email = forms.EmailField(label="email", max_length=100)
    username = forms.IntegerField(label="Phone number")
    
    def __str__(self):
        return self.username
    def __init__(self, *args, **kwargs):
        super(signForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        


class otpForm(forms.Form):
    otp = forms.IntegerField(label="Enter OTP")
   

    
  



class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UpdateProfileForm(forms.ModelForm):
    street_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '549 Sulphur Springs Road'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Coimbatore'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tamilnadu, India'}))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '641001'}))
    mobile_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'phone number'}))
    type = forms.Select(attrs={'class': 'form-control'})
    account_type = forms.Select(attrs={'class': 'form-control'}) 

    class Meta:
        model = Task
        fields = [ 'street_address', 'city', 'state', 'zipcode', 'mobile_number']


class UserDetailForm(forms.ModelForm):
   
    class Meta:
        model = Task
        fields = ['name',  'mobile_number',  'street_name', 'city', 'state', 'district', 'pincode', 
        'mcategory1', 'msub_category1', 'mproducts1', 'mtype1']

    def __init__(self, *args, **kwargs):
        super(UserDetailForm, self).__init__(*args, **kwargs)
        self.fields['district'].queryset = SubRegion.objects.none()

        if 'state' in self.data:
            try:
                country_id = int(self.data.get('state'))
                self.fields['district'].queryset = SubRegion.objects.filter(region_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.region.city_set.order_by('name')
        


class BusinessForm(forms.ModelForm): 

    class Meta:
        model = Task
        fields = ['name', 'mobile_number',  'street_name', 'city', 'state', 'district', 'pincode',
                    'mcategory1', 'msub_category1', 'mproducts1', 'mtype1','door_no', 'building_name',
                    'area', 'landmark',   'email','website', 'std_code', 'landline', 'logo',
                    'nature', 'gst_no','mcategory2', 'msub_category2', 'mproducts2', 'mtype2', 'mcategory3',
                    'msub_category3', 'mproducts3', 'mtype3','visiting_card', 'catalogue', 'video']


class CreditPoint(forms.ModelForm):
    
    class Meta:
        model = Creditvalues
        fields = ['sms', 'email', 'whatsapp', 'bulk_sms', 'bulk_email', 'bulk_whatsapp', 'download']
