from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User, AbstractUser


TRANSACTION_TYPE = [('Credit', 'Credit'), ('Debit', 'Debit')]

class Careers(models.Model):
    role = models.CharField(max_length=50, blank=True, null=False)
    description = models.CharField(max_length=10000, blank=True, null=False)
    education = models.CharField(max_length=1000, blank=True, null=True)
    experience = models.CharField(max_length=1000, blank=True, null=True)
    preference = models.CharField(max_length=1000, blank=True, null=True)
    package = models.CharField(max_length=1000, blank=True, null=True)
    
    def __str__(self):
        return f"{self.role}:{self.description}"


class Creditvalues(models.Model):
    sms = models.IntegerField(default=2)
    email = models.IntegerField(default=2)
    whatsapp = models.IntegerField(default=2)
    bulk_sms = models.IntegerField(default=5)
    bulk_email = models.IntegerField(default=5)
    bulk_whatsapp = models.IntegerField(default=5)
    download = models.IntegerField(default=2)
    
    def __str__(self):
        return f"{self.sms}:{self.email}:{self.whatsapp}:{self.download}:{self.bulk_sms}:{self.bulk_email}:{self.bulk_whatsapp}"


class otp(models.Model):
    otp = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.otp}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE, blank=True, null=True)
    desc = models.CharField(max_length=20, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

class FaqSub(models.Model):
    subject = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.subject}"


class Faqs(models.Model):
    subject = models.ForeignKey(FaqSub, on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=255, blank=True, null=True)
    answer = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.title}"
