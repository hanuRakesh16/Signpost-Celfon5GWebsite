from django import forms
from django.forms import ModelForm, widgets, MultiWidget, TextInput
from django.urls import reverse_lazy
from .models import *
import re
from django.contrib.auth.forms import AuthenticationForm

# create Add shop form
class AddShopForm(ModelForm):
    business_name = forms.CharField(help_text="Business name should not exceed 30 characters", max_length=30)

    class Meta:
        model = Task
        fields = ['name', 'prefix', 'altname', 'mobile_number', 'listing_type', 'door_no', 'building_name', 'street_name',
                  'area', 'landmark', 'city', 'state', 'district', 'pincode', 'email',
                  'website', 'std_code', 'landline', 'club_name',
                  'logo', 'description', 'nature', 'firm_type', 'gst_no', 'mcategory1', 'msub_category1', 'mproducts1', 'mtype1',
                  'mcategory2', 'msub_category2', 'mproducts2', 'mtype2', 'mcategory3', 'msub_category3', 'mproducts3',
                  'mtype3','visiting_card',
                  'logo', 'catalogue', 'video', 'agree']


    def __init__(self, *args, **kwargs):
        super(AddShopForm, self).__init__(*args, **kwargs)
        self.fields['district'].queryset = SubRegion.objects.none()

        if 'state' in self.data:
            try:
                country_id = int(self.data.get('state'))
                self.fields['district'].queryset = SubRegion.objects.filter(region_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.region.city_set.order_by('name')

    # def clean_mobile_number(self):
    #     mobile_number = self.cleaned_data['mobile_number']
    #     Pattern = re.compile("(0|91)?[6-9][0-9]{9}")
    #     if not Pattern.match(mobile_number):
    #         print("mobile number is not valid")
    #         raise forms.ValidationError("Enter a valid mobile number")
    #     return mobile_number

class EcomProductsForm(forms.ModelForm):
    class Meta:
        model = EcomProducts
        fields = ['product_name', 'product_price', 'product_descriptions', 'product_image']


class BusinessListingForm(forms.ModelForm):
    class Meta:
        model = BusinessListing
        fields = ['firm_name', 'image', 'space_code', 'space_value', 'payment_mode', 'amount']


class IndividualForm(ModelForm):
    business_name = forms.CharField(help_text="Business name should not exceed 30 characters", max_length=30)

    class Meta:
        model = Task
        fields = ['name', 'prefix', 'altname', 'mobile_number', 'listing_type', 'door_no', 'building_name', 'street_name',
                  'area', 'landmark', 'city', 'state', 'district', 'pincode', 'email',
                  'website', 'std_code', 'landline', 'club_name',
                  'logo', 'description', 'nature', 'firm_type', 'mcategory1', 'msub_category1', 'mproducts1', 'mtype1',
                  'mcategory2', 'msub_category2', 'mproducts2', 'mtype2', 'mcategory3', 'msub_category3', 'mproducts3',
                  'mtype3',
                  'visiting_card', 'blood_donor', 'blood_group', 'year_of_birth', 'gender', 'martial_status', 'education', 'employment', 'responsibility', 'income', 'hobbies']

        
    def __init__(self, *args, **kwargs):
        super(IndividualForm, self).__init__(*args, **kwargs)
        self.fields['district'].queryset = SubRegion.objects.none()

        if 'state' in self.data:
            try:
                country_id = int(self.data.get('state'))
                self.fields['district'].queryset = SubRegion.objects.filter(region_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.region.city_set.order_by('name')


class BasicForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'prefix', 'altname', 'mobile_number', 'door_no', 'building_name', 'street_name',
                  'area', 'landmark', 'city', 'state', 'district', 'pincode', 'email',
                  'website', 'std_code', 'landline', 
                   'description', 'nature', 'firm_type', 'gst_no', 
                  'logo']
        

    def __init__(self, *args, **kwargs):
        super(BasicForm, self).__init__(*args, **kwargs)
        self.fields['district'].queryset = SubRegion.objects.none()

        if 'state' in self.data:
            try:
                country_id = int(self.data.get('state'))
                self.fields['district'].queryset = SubRegion.objects.filter(region_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.region.city_set.order_by('name')


class CreateAdForm(ModelForm):
    class Meta:
        model = Advertisement
        fields = ['pink_pg_title', 'business_name', 'slogan', 'door_street', 'city_pincode',
                  'landline', 'mobile', 'whatsapp', 'email', 'website', 'name_desg1', 'number1',
                  'name_desg2', 'number2', 'name_desg3', 'number3', 'activity1', 'activity2']

