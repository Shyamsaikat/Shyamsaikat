from re import I
from unicodedata import category
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from more_itertools import quantify
from django.db.models import Sum

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    status = models.CharField(max_length=2, choices=(('1','Active'),('2','Inactive')), default=1)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    location = models.CharField(max_length=250)
    status = models.CharField(max_length=2, choices=(('1','Active'),('2','Inactive')), default=1)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.location

class Bus(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE, blank= True, null = True)
    bus_number = models.CharField(max_length=250)
    seats = models.FloatField(max_length=5, default=0)
    status = models.CharField(max_length=2, choices=(('1','Active'),('2','Inactive')), default=1)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bus_number

class Schedule(models.Model):
    code = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus,on_delete=models.CASCADE)
    depart = models.ForeignKey(Location,on_delete=models.CASCADE, related_name='depart_location')
    destination = models.ForeignKey(Location,on_delete=models.CASCADE, related_name='destination')
    schedule= models.DateTimeField()
    fare= models.FloatField()
    status = models.CharField(max_length=2, choices=(('1','Active'),('2','Cancelled')), default=1)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.code + ' - ' + self.bus.bus_number)

    def count_available(self):
        booked = Booking.objects.filter(schedule=self).aggregate(Sum('seats'))['seats__sum']
        if booked:
            return self.bus.seats - booked
        return self.bus.seats 

class Booking(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=250)
    schedule = models.ForeignKey(Schedule,on_delete=models.CASCADE)
    seats = models.IntegerField()
    status = models.CharField(max_length=2, choices=(('1','Pending'),('2','Paid')), default=1)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.code + ' - ' + self.name)

    def total_payable(self):
        return self.seats * self.schedule.fare
from django.db import models

from django.db import models

class Requisition(models.Model):
    date = models.DateField(auto_now=True)
    requested_by = models.CharField(max_length=100, default="none")
    faculty = models.CharField(max_length=100, default="none")
    profession = models.CharField(max_length=100, default="none")  # New field for profession
    email = models.EmailField(max_length=254, default="none@example.com")  # New field for email
    location_from = models.CharField(max_length=100, default="none")
    location_to = models.CharField(max_length=100, default="none")
    purpose_of_trip = models.CharField(max_length=50, choices=[('govt', 'Government'), ('personal', 'Personal')], default='personal')
    departure_date = models.DateField()
    return_date = models.DateField()
    number_of_passengers = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"Requisition by {self.requested_by} on {self.date}"

class Seat(models.Model):
    SEAT_STATUS = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('selected', 'Selected')
    ]
    
    seat_number = models.CharField(max_length=5)
    status = models.CharField(max_length=10, choices=SEAT_STATUS, default='available')
    
    def __str__(self):
        return self.seat_number



# @receiver(models.signals.post_save, sender=Invoice_Item)
# def stock_update(sender, instance, **kwargs):
#     stock = Stock(product = instance.product, quantity = instance.quantity, type = 2)
#     stock.save()
#     # stockID = Stock.objects.last().id
#     Invoice_Item.objects.filter(id= instance.id).update(stock=stock)

# @receiver(models.signals.post_delete, sender=Invoice_Item)
# def delete_stock(sender, instance, **kwargs):
#     try:
#         stock = Stock.objects.get(id=instance.stock.id).delete()
#     except:
#         return instance.stock.id



    
    