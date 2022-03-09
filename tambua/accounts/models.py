from django.db import models
class Customers(models.Model):
    customer_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    customer_photo = models.CharField(max_length=50)
    customer_recording = models.CharField(max_length=50)
    customer_signature = models.CharField(max_length=50)
    customer_fingerprint = models.CharField(max_length=50)
    enrollment_date = models.DateField(auto_now=True)
    
class CustomersWithFiles(models.Model):
    customer_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    customer_photo = models.FileField(upload_to='')
    customer_recording = models.FileField(upload_to='')
    customer_signature = models.FileField(upload_to='')
    customer_fingerprint = models.FileField(upload_to='')
    enrollment_date = models.DateField(auto_now=True)
    
    