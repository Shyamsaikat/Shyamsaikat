# Generated by Django 4.0.3 on 2024-09-12 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservationApp', '0004_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requisition',
            name='bus',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='code',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='date_updated',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='depart',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='destination',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='fare',
        ),
        migrations.RemoveField(
            model_name='requisition',
            name='schedule',
        ),
        migrations.AddField(
            model_name='requisition',
            name='date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='requisition',
            name='departure_date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='requisition',
            name='faculty',
            field=models.CharField(default='none', max_length=100),
        ),
        migrations.AddField(
            model_name='requisition',
            name='location_from',
            field=models.CharField(default='none', max_length=100),
        ),
        migrations.AddField(
            model_name='requisition',
            name='location_to',
            field=models.CharField(default='none', max_length=100),
        ),
        migrations.AddField(
            model_name='requisition',
            name='number_of_passengers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='requisition',
            name='purpose_of_trip',
            field=models.CharField(choices=[('govt', 'Government'), ('personal', 'Personal')], default='personal', max_length=50),
        ),
        migrations.AddField(
            model_name='requisition',
            name='requested_by',
            field=models.CharField(default='none', max_length=100),
        ),
        migrations.AddField(
            model_name='requisition',
            name='return_date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='seats',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('1', 'Pending'), ('2', 'Paid')], default=1, max_length=2),
        ),
        migrations.AlterField(
            model_name='requisition',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
