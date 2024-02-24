from cgitb import lookup
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from . models import *
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget
from django.contrib.auth.models import User


# Register your models here.
admin.site.site_header = "Signpost Celfon Admin Panel"
admin.site.site_title = "Signpost Celfon Admin Panel"
admin.site.index_title = "Welcome to Signpost Celfon Admin Panel"

class SubResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'main_category'))

    class Meta:
        model = Sub_category
        import_id_fields = ('sub_category', 'category')
        exclude = ('id',)
        fields = (
            'category',
            'sub_category',
        )


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'main_category'))

    sub_category = fields.Field(
        column_name='sub_category',
        attribute='sub_category',
        widget=ForeignKeyWidget(Sub_category, 'sub_category'))

    class Meta:
        model = Product
        import_id_fields = ('sub_category', 'product_name', 'category')
        exclude = ('id',)
        fields = (
            'category',
            'sub_category',
            'product_name'
        )


class TaskResource(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username'))

    state = fields.Field(
        column_name='state',
        attribute='state',
        widget=ForeignKeyWidget(Region, 'name'))

    district = fields.Field(
        column_name='district',
        attribute='district',
        widget=ForeignKeyWidget(SubRegion, 'name'))

    mcategory1 = fields.Field(
        column_name='mcategory1',
        attribute='mcategory1',
        widget=ForeignKeyWidget(Category, 'main_category'))

    mcategory2 = fields.Field(
        column_name='mcategory2',
        attribute='mcategory2',
        widget=ForeignKeyWidget(Category, 'main_category'))

    mcategory3 = fields.Field(
        column_name='mcategory3',
        attribute='mcategory3',
        widget=ForeignKeyWidget(Category, 'main_category'))

    msub_category1 = fields.Field(
        column_name='msub_category1',
        attribute='msub_category1',
        widget=ForeignKeyWidget(Sub_category, 'sub_category'))

    msub_category2 = fields.Field(
        column_name='msub_category2',
        attribute='msub_category2',
        widget=ForeignKeyWidget(Sub_category, 'sub_category'))

    msub_category3 = fields.Field(
        column_name='msub_category3',
        attribute='msub_category3',
        widget=ForeignKeyWidget(Sub_category, 'sub_category'))

    mproducts1 = fields.Field(
        column_name='mproducts1',
        attribute='mproducts1',
        widget=ForeignKeyWidget(Product, 'product_name'))

    mproducts2 = fields.Field(
        column_name='mproducts2',
        attribute='mproducts2',
        widget=ForeignKeyWidget(Product, 'product_name'))

    mproducts3 = fields.Field(
        column_name='mproducts3',
        attribute='mproducts3',
        widget=ForeignKeyWidget(Product, 'product_name'))
    
    club_name = fields.Field(
        column_name='club_name',
        attribute='club_name',
        widget=ForeignKeyWidget(Clubs, 'name'))

    class Meta:
        model = Task
        skip_unchanged = True
        import_id_fields = ('name', 'user', 'state', 'district', 'mcategory1', 'mcategory2', 'mcategory3',
                            'msub_category1', 'msub_category2', 'msub_category3', 'mproducts1', 'mproducts2',
                            'mproducts3', 'club_name')
        exclude = ('id',)
        export_order = ['name', 'prefix', 'altname', 'mobile_number', 'detailType', 'door_no', 'building_name', 'street_name', 'area', 'landmark',
                        'city', 'state', 'district',
                        'pincode', 'email', 'website', 'std_code', 'landline',
                        'club_name', 'description', 'nature', 'firm_type', 'mproducts1', 'mcategory1',
                        'msub_category1','mtype1', 'mproducts2', 'mcategory2', 'msub_category2', 'mtype2',
                        'mproducts3', 'mcategory3', 'msub_category3','mtype3',
                        'blood_donor', 'blood_group', 'year_of_birth', 'gender', 'martial_status', 'education', 'employment', 'responsibility', 'income', 'hobbies',
                        'video']

 
class IncomeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('worker', 'id')


class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass


class SubCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('sub_category', 'category')
    list_filter = ('category',)
    resource_class = SubResource


class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('product_name', 'category', 'sub_category')
    list_filter = ('category', 'sub_category')
    search_fields = ('product_name',)
    resource_class = ProductResource


class EcomProductsInline(admin.StackedInline):
    model = EcomProducts
    extra = 0


class TaskAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, admin.ModelAdmin):
    inlines = [EcomProductsInline]
    list_display = ('name', 'detailType', 'listing_owner', 'listing_type', 'city', 'referred_by')
    list_filter = ('referred_by', 'pincode', 'city',)
    readonly_fields = ('referred_by',)
    resource_class = TaskResource
    search_fields = Task.get_searchable_fields()
    

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        #get search value
        searchable_fields = Task.get_searchable_fields()
        search_q = models.Q()
        for field in searchable_fields:
            search_q |= models.Q(**{f"{field}__icontains": search_term})

        #filter 
        queryset = queryset.filter(search_q)

        return queryset, use_distinct
    


class TeamsAdmin(admin.ModelAdmin):
    list_display = ('user', 'team_leader')
    list_filter = ('team_leader',)
    lookup_fields = ('user', 'team_leader')




admin.site.register(Task, TaskAdmin)
admin.site.register(Profile)
admin.site.register(Teams, TeamsAdmin)
admin.site.register(Profession)
admin.site.register(Income, IncomeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Sub_category, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(WorkSummary)
admin.site.register(BusinessListing)
admin.site.register(BusinessListingIncome)
admin.site.register(BusinessListingIncomeDelivery)
admin.site.register(Clubs)
admin.site.register(IndividualTotalIncome)
admin.site.register(IndividualIncome)
admin.site.register(CustomProfile)
# admin.site.register(CustomProfile, CustomUserProfile)
admin.site.register(Firmresults)
admin.site.register(Subscriptions)
admin.site.register(Advertisement)

