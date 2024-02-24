
from django.contrib.auth.models import User, AbstractUser
from django.db.models import Q
from django.urls import reverse
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from cities_light.models import City, Region, SubRegion
from django.db import models
from .utils import *
from django_resized import ResizedImageField

# Create your models here.
PREFIX_FIELD_CHOICES = [('Mr', 'Mr.'), ('Mrs', 'Mrs.'), ('Ms', 'Ms.'), ('Dr', 'Dr.'), ('Prof', 'Prof.'),
                        ('Lion', 'Lion'), ('Adv', 'Adv'), ('CA', 'CA'), ('Er', 'Er'), ('Rtn', 'Rtn'), ('Vn', 'Vn'), ]

LISTING_TYPE_CHOICES = [('Free', 'Free'), ('Premium', 'Premium')]

PRODUCT_TYPE_CHOICES = [('M', 'Manufacturer'), ('D', 'Dealer'), ('S', 'Service')]

NATURE_CHOICES = [('Branch Office', 'Branch Office'),
                  ('Consultant', 'Consultant'),
                  ('Dealer', 'Dealer'),
                  ('Dealer', 'Dealer'),
                  ('Exporter', 'Exporter'),
                  ('Franchises', 'Franchises'),
                  ('Head Office', 'Head Office'),
                  ('Industry', 'Industry'),
                  ('MicroIndustry', 'MicroIndustry'), ('Office', 'Office'), ('Professional', 'Professional'),
                  ('Service Firm', 'Service Firm'), ('Shop', 'Shop'),
                  ('SSI', 'SSI'),
                  ('Tiny Industry', 'Tiny Industry'),
                  ('Wholesaler', 'Wholesaler')]

PAYMENT_MODE_CHOICES = [('UPI', 'UPI'), ('GPay', 'GPay'), ('NEFT', 'NEFT'), ('CHEQUE', 'Cheque'), ('ONLINE', 'Online'), ('AFTER PROOF APPROVAL', 'After Proof Approval')]

DESIGNATION_CHOICES = [('Prop.', 'Prop.'), ('Partner', 'Partner'), ('Mg.Partner', 'Mg.Partner'), ('Director', 'Director'), ('MD', 'MD'), ('Chairman', 'Chairman'), ('Manager', 'Manager'), ('Executive', 'Executive')]

DONATE = [('Yes', 'Yes'), ('No', 'No')]
BLOOD_GROUP = [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),]
GENDER = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
MARTIAL_STATUS = [('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced')]
EDUCATION = [('Post Gratuate', 'Post Gratuate'), ('Graduate', 'Graduate'), ('High School', 'High School'), ('School', 'School'),  ('No School', 'No School')]
EMPLOYMENT = [('Govt. Employed', 'Govt. Employed'), ('Govt.Undertakings Employed', 'Govt.Undertakings Employed'), ('Private Firm Employed', 'Private Firm Employed'), ('Self Employed', 'Self Employed'), ('Free Lancer - Part Time', 'Free Lancer - Part Time'), ('Retired Sr.Citizen', 'Retired Sr.Citizen'), ('Un Employed', 'Un Employed')]
FAMILY_RESPONSIBILITY = [('Head of Family', 'Head of Family'), ('House Wife', 'House Wife'), ('Student', 'Student'), ('Senior Citizen', 'Senior Citizen')]
INCOME = [('Affluent', 'Affluent'), ('Higher Income', 'Higher Income'), ('Middle Income', 'Middle Income'), ('Lower Income', 'Lower Income')]
POSITION_CHOICES = [('President', 'President'), ('Secretary', 'Secretary'),('Treasurer', 'Treasurer'),
                    ('Member', 'Member')]
TYPES = [('Firm', 'Firm'), ('Person', 'Person')]
ACCOUNT_TYPES =[('Free', 'Free'), ('Premium', 'Premium')]


class CustomPermission(models.Model):
    class Meta:
        permissions = [
            ("is_media_partner", "Is Media Partner?"),
        ]

# class Wallet(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     credit_points = models.BigIntegerField(default=100)

#     def __str__(self):
#         return f"Wallet of {self.user.username}"

class CustomProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image =ResizedImageField(force_format="WEBP", quality=75,upload_to='webimages/user-profiles/', blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    street_address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=25, blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=25,choices=TYPES, default="Person")
    mobile_number = models.BigIntegerField(blank=True, null=True)
    credit_points = models.BigIntegerField(default=100)
    minimum_points = models.BigIntegerField(default=9)
    account_type = models.CharField(max_length=15, choices=ACCOUNT_TYPES, default="Free")

    def __str__(self):
        return self.user.username

class Category(models.Model):
    main_category = models.CharField(max_length=100)
    image = ResizedImageField(force_format="WEBP", quality=75,blank=True, null=True, upload_to='webimages/category_images/')
    slug = models.SlugField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.main_category

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

def category_pre_save(sender, instance, *args, ** kwargs):
    print('pre_save')
    if instance.slug is None:
        slugify_instance_category(instance, save=False)


pre_save.connect(category_pre_save, sender=Category)


def category_post_save(sender, instance, created, *args, ** kwargs):
    print('post_save')
    if created:
        slugify_instance_category(instance, save=True)


post_save.connect(category_post_save, sender=Category)


def get_default_category():
    return Category.objects.get(main_category="Others")


class Sub_category(models.Model):
    sub_category = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.sub_category


def sub_category_pre_save(sender, instance, *args, ** kwargs):
    print('pre_save')
    if instance.slug is None:
        slugify_instance_sub_category(instance, save=False)


pre_save.connect(sub_category_pre_save, sender=Sub_category)


def sub_category_post_save(sender, instance, created, *args, ** kwargs):
    print('post_save')
    if created:
        slugify_instance_sub_category(instance, save=True)


post_save.connect(sub_category_post_save, sender=Sub_category)


def get_default_sub_category():
    return Sub_category.objects.get(sub_category="Others")


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    sub_category = models.ForeignKey(Sub_category, on_delete=models.CASCADE, default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.product_name


def product_pre_save(sender, instance, *args, ** kwargs):
    print('pre_save')
    if instance.slug is None:
        slugify_instance_product(instance, save=False)


pre_save.connect(product_pre_save, sender=Product)


def product_post_save(sender, instance, created, *args, ** kwargs):
    print('post_save')
    if created:
        slugify_instance_product(instance, save=True)


post_save.connect(product_post_save, sender=Product)


class TaskManager(models.Manager):
    def search(self, query):
        if query is None or query == "":
            return self.get_queryset().none()
        lookups = (Q(name__icontains=query) | Q(altname__icontains=query)) & Q(listing_type="Free")
        return self.get_queryset().filter(lookups)

class TaskManagerPremium(models.Manager):
    def search(self, query):
        if query is None or query == "":
            return self.get_queryset().none()
        lookups = (Q(name__icontains=query) | Q(altname__icontains=query)) & Q(listing_type="Premium")
        return self.get_queryset().filter(lookups)

class TaskManagerProduct(models.Manager):
    def product(self, query):
        if query is None or query == "":
            return self.get_queryset().none()
        lookups = (Q(mproducts1__product_name__icontains=query) | Q(mproducts2__product_name__search=query) | Q(mproducts3__product_name__search=query) | Q(description__icontains=query)) & Q(listing_type="Free")
        return self.get_queryset().filter(lookups)

class TaskManagerProductPremium(models.Manager):
    def product(self, query):
        if query is None or query == "":
            return self.get_queryset().none()
        lookups = (Q(mproducts1__product_name__icontains=query) | Q(mproducts2__product_name__search=query) | Q(mproducts3__product_name__search=query) | Q(description__icontains=query)) & Q(listing_type="Premium")
        return self.get_queryset().filter(lookups)


class Clubs(models.Model):
    name = models.CharField(max_length=100)
    short_url = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True, null=True,)
    image = ResizedImageField(force_format="WEBP", quality=75,blank=True, null=True, upload_to='webimages/club_images/')
    slug = models.SlugField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('clubdetail', kwargs={'slug': self.slug})

def clubs_pre_save(sender, instance, *args, ** kwargs):
    print('pre_save')
    if instance.slug is None:
        slugify_instance_clubs(instance, save=False)


pre_save.connect(clubs_pre_save, sender=Clubs)


def clubs_post_save(sender, instance, created, *args, ** kwargs):
    print('post_save')
    if created:
        slugify_instance_clubs(instance, save=True)


post_save.connect(clubs_post_save, sender=Clubs)


class Wishlists(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_wishlists')
    shops = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='shops')


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    listing_owner = models.ForeignKey(User, related_name='listing_owner', on_delete=models.CASCADE,  null=True, blank=True)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES, default="Free")
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    prefix = models.CharField(max_length=10, choices=PREFIX_FIELD_CHOICES, blank=True, null=True)
    altname = models.CharField(max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=10)
    detailType = models.CharField(max_length=2, default='F')
    gst_no = models.CharField(max_length=20, blank=True, null=True)
    # count
    view_count = models.IntegerField(default=0)
    search_count = models.IntegerField(default=0)
    # address
    door_no = models.CharField(max_length=50, null=True, blank=True)
    building_name = models.CharField(max_length=50, null=True, blank=True)
    street_name = models.CharField(max_length=50)
    area = models.CharField(max_length=50, null=True, blank=True)
    landmark = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.ForeignKey(Region, on_delete=models.CASCADE, default=None)
    district = models.ForeignKey(SubRegion, on_delete=models.CASCADE, default=None)
    pincode = models.CharField(max_length=7, verbose_name='Pincode')
    # contact
    email = models.EmailField(max_length=100, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    std_code = models.CharField(max_length=5, null=True, blank=True)
    landline = models.CharField(max_length=11, null=True, blank=True)
    # club
    club_name = models.ForeignKey(Clubs, on_delete=models.CASCADE, default=None, null=True, blank=True)
    # image
    logo = ResizedImageField(force_format="WEBP", quality=75, blank=True, null=True, upload_to='webimages/logo/')
    description = models.TextField(max_length=255, null=True, blank=True)
    nature = models.CharField(max_length=100, choices=NATURE_CHOICES, blank=True, null=True)
    firm_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, blank=True, null=True, default='Suppliers')
    # products
    mcategory1 = models.ForeignKey(Category, related_name="mc1", on_delete=models.CASCADE, blank=True, null=True,
                                   default=None)
    msub_category1 = models.ForeignKey(Sub_category, related_name="msc1", on_delete=models.CASCADE, blank=True,
                                       null=True, default=None)
    mproducts1 = models.ForeignKey(Product, related_name="mp1", max_length=100, default=None, blank=True, null=True,
                                   on_delete=models.CASCADE)
    mtype1 = models.CharField(max_length=100, choices=PRODUCT_TYPE_CHOICES, default='Service')
    mcategory2 = models.ForeignKey(Category, related_name="mc2", on_delete=models.CASCADE, blank=True, null=True,
                                   default=None)
    msub_category2 = models.ForeignKey(Sub_category, related_name="msc2", on_delete=models.CASCADE, blank=True,
                                       null=True, default=None)
    mproducts2 = models.ForeignKey(Product, related_name="mp2", max_length=100, default=None, blank=True, null=True,
                                   on_delete=models.CASCADE)
    mtype2 = models.CharField(max_length=100, choices=PRODUCT_TYPE_CHOICES, default='Service')
    mcategory3 = models.ForeignKey(Category, related_name="mc3", on_delete=models.CASCADE, blank=True, null=True,
                                   default=None)
    msub_category3 = models.ForeignKey(Sub_category, related_name="msc3", on_delete=models.CASCADE, blank=True,
                                       null=True, default=None)
    mproducts3 = models.ForeignKey(Product, related_name="mp3", max_length=100, default=None, blank=True, null=True,
                                   on_delete=models.CASCADE)
    mtype3 = models.CharField(max_length=100, choices=PRODUCT_TYPE_CHOICES, default='Service')
    # visiting card
    visiting_card = ResizedImageField(force_format="WEBP", quality=75,upload_to='webimages/visitingcard/', null=True, blank=True)
    # persons only
    blood_donor = models.CharField(max_length=5, choices=DONATE, blank=True, null=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP, null=True, blank=True)
    year_of_birth = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, choices=GENDER, blank=True, null=True)
    martial_status = models.CharField(max_length=50, choices=MARTIAL_STATUS, blank=True, null=True)
    education = models.CharField(max_length=50, choices=EDUCATION, blank=True, null=True)
    employment = models.CharField(max_length=50, choices=EMPLOYMENT, blank=True, null=True)
    responsibility = models.CharField(max_length=50, choices=FAMILY_RESPONSIBILITY, blank=True, null=True)
    income = models.CharField(max_length=50, choices=INCOME, blank=True, null=True)
    hobbies = models.CharField(max_length=255, blank=True, null=True)
    # advertisers only
    colour_advertisement = ResizedImageField(force_format="WEBP", quality=75,upload_to='webimages/advertisement/', null=True, blank=True)
    business_listing =ResizedImageField(force_format="WEBP", quality=75,upload_to='webimages/colour_advertisement/', null=True, blank=True)  
    video = models.CharField(max_length=200, null=True, blank=True)
    catalogue = models.FileField(upload_to='webimages/catalog/', null=True, blank=True)
    referred_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    agree = models.BooleanField(default=True, blank=True)
    users_wishlist = models.ManyToManyField(User, related_name='users_wishlist', blank=True, null=True)
    shop_created_at = models.DateTimeField(auto_now_add=True)
    # img = ResizedImageField(force_format="WEBP", quality=75, upload_to="webimages/visitingcard/")
    # #search bar
    # searchableFields=['user','name']
    def get_searchable_fields():
        return ['user__username', 'name']  
    
    objects = TaskManager()
    objectp = TaskManagerPremium()
    object = TaskManagerProduct()
    objectpp = TaskManagerProductPremium()
    

    class Meta:
        verbose_name = "firm"
        verbose_name_plural = "firms"
        ordering = ['-listing_type']

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Income.objects.create(worker=instance, income_amount=0, listings=0)
            BusinessListingIncome.objects.create(user=instance, total=0)
            BusinessListingIncomeDelivery.objects.create(user=instance, total=0)
            IndividualTotalIncome.objects.create(user=instance, total_income=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('firmdetail', kwargs={'slug': self.slug})

    def get_person_url(self):
        return reverse('persondetail', kwargs={'slug': self.slug})


def article_pre_save(sender, instance, *args, ** kwargs):
    print('pre_save')
    if instance.slug is None:
        slugify_instance_title(instance, save=False)


pre_save.connect(article_pre_save, sender=Task)


def article_post_save(sender, instance, created, *args, ** kwargs):
    print('post_save')
    if created:
        slugify_instance_title(instance, save=True)


post_save.connect(article_post_save, sender=Task)
class Firmresults(models.Model):
    firm = models.ForeignKey('Task', on_delete=models.SET_NULL, blank=True, null=True)
    searchquery = models.CharField(max_length=50,blank=True,null=True)
    nsearchcount = models.IntegerField(blank=True,null=True)
    timestamp = models.DateTimeField(auto_now=True)
    timestamp_sent = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.firm},{self.searchquery},{self.nsearchcount},{self.timestamp},{self.timestamp_sent}"
   
class Subscriptions(models.Model):
    name = models.CharField(max_length=100)
    creditvalue = models.IntegerField(default=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
   
    def __str__(self):
        return f"{self.name},{self.creditvalue},{self.description},{self.price}"

class EcomProducts(models.Model):
    firm_name = models.ForeignKey('Task', on_delete=models.SET_NULL, blank=True, null=True)
    product_name = models.CharField(max_length=60, blank=True, null=True)
    product_price = models.IntegerField(blank=True, null=True)
    product_descriptions = models.TextField(max_length=300, blank=True, null=True)
    product_image = ResizedImageField(force_format="WEBP", quality=75,blank=True, null=True, upload_to='webimages/ecom_products/')


class Income(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    listings = models.BigIntegerField(null=True, blank=True)
    income_amount = models.FloatField()
    is_collected = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_collected:
            self.income_amount = 0
            self.is_collected = False
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.worker)


class IndividualIncome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    total_fields = models.IntegerField(blank=True, null=True)
    income = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class IndividualTotalIncome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    total_income = models.FloatField(blank=True, null=True)
    received = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.received:
            self.total_income = 0
            self.received = False
        super().save(*args, **kwargs)


class Profile(models.Model):
    mobile = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return self.mobile


class WorkSummary(models.Model):
    mp = models.ForeignKey(User, on_delete=models.CASCADE)
    firm_name = models.ForeignKey('Task', on_delete=models.CASCADE)
    income = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.firm_name.name


class BusinessListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    firm_name = models.ForeignKey('Task', on_delete=models.CASCADE)
    image = ResizedImageField(force_format="WEBP", quality=75,upload_to='webimages/business_listing/', null=True, blank=True)
    space_code = models.CharField(max_length=50, blank=True, null=True)
    space_value = models.CharField(max_length=50, blank=True, null=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='ONLINE')
    amount = models.FloatField(blank=True, null=True)
    income = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.income = (self.amount / 100) * 15
        super().save(*args, **kwargs)

    def __str__(self):
        return self.firm_name.business_name


class BusinessListingIncome(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    total = models.BigIntegerField(blank=True, null=True)
    received = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.received:
            self.total = 0
            self.received = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class BusinessListingIncomeDelivery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    total = models.BigIntegerField(blank=True, null=True)
    received = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.received:
            self.total = 0
            self.received = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class Profession(models.Model):
    name = models.CharField(max_length=255)
    # created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Teams(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    bl_income = models.ForeignKey(BusinessListingIncome, on_delete=models.CASCADE, blank=True, null=True)
    data_income = models.ForeignKey(Income, on_delete=models.CASCADE, blank=True, null=True)
    # ind_income = models.ForeignKey(IndividualTotalIncome, on_delete=models.CASCADE, blank=True, null=True)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_leader', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.bl_income = BusinessListingIncome.objects.get(user=self.user)
        self.data_income = Income.objects.get(worker=self.user)
        self.ind_income = IndividualTotalIncome.objects.get(user=self.user)
        super().save(*args, **kwargs)


class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    pink_pg_title = models.CharField(max_length=100, blank=True, null=True)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    slogan = models.CharField(max_length=100, blank=True, null=True)
    door_street = models.CharField(max_length=100, blank=True, null=True)
    city_pincode = models.CharField(max_length=100, blank=True, null=True)
    landline = models.PositiveBigIntegerField(blank=True, null=True)
    mobile = models.PositiveBigIntegerField(blank=True, null=True)
    whatsapp = models.PositiveBigIntegerField(blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    name_desg1 = models.CharField(max_length=100, blank=True, null=True)
    number1 = models.PositiveBigIntegerField(blank=True, null=True)
    name_desg2 = models.CharField(max_length=100, blank=True, null=True)
    number2 = models.PositiveBigIntegerField(blank=True, null=True)
    name_desg3 = models.CharField(max_length=100, blank=True, null=True)
    number3 = models.PositiveBigIntegerField(blank=True, null=True)
    activity1 = models.CharField(max_length=300, blank=True, null=True)
    activity2 = models.CharField(max_length=300, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


def ads_pre_save(sender, instance, *args, ** kwargs):
    print('pre_save')
    if instance.slug is None:
        slugify_instance_ads(instance, save=False)


pre_save.connect(ads_pre_save, sender=Advertisement)


def ads_post_save(sender, instance, created, *args, ** kwargs):
    print('post_save')
    if created:
        slugify_instance_ads(instance, save=True)


post_save.connect(ads_post_save, sender=Advertisement)



