from email import message
from unicodedata import category
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from btrs_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from reservationApp.forms import UserRegistration, UpdateProfile, UpdatePasswords, SaveCategory, SaveLocation, SaveBus, SaveSchedule, SaveBooking, PayBooked
from reservationApp.models import Booking, Category, Location, Bus, Schedule
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from datetime import datetime
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import render

context = {
    'page_title' : 'File Management System',
}
#login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# @login_required
def home(request):
    context['page_title'] = 'Home'
    context['buses'] = Bus.objects.count()
    context['categories'] = Category.objects.count()
    context['upcoming_trip'] = Schedule.objects.filter(status= 1, schedule__gt = datetime.today()).count()
    return render(request, 'home.html',context)

def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)


@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html',context)


# Category
@login_required
def category_mgt(request):
    context['page_title'] = "Bus Categories"
    categories = Category.objects.all()
    context['categories'] = categories

    return render(request, 'category_mgt.html', context)

@login_required
def save_category(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            category = Category.objects.get(pk=request.POST['id'])
        else:
            category = None
        if category is None:
            form = SaveCategory(request.POST)
        else:
            form = SaveCategory(request.POST, instance= category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_category(request, pk=None):
    context['page_title'] = "Manage Category"
    if not pk is None:
        category = Category.objects.get(id = pk)
        context['category'] = category
    else:
        context['category'] = {}

    return render(request, 'manage_category.html', context)

@login_required
def delete_category(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            category = Category.objects.get(id = request.POST['id'])
            category.delete()
            messages.success(request, 'Category has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Category has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Category has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Location
@login_required
def location_mgt(request):
    context['page_title'] = "Locations"
    locations = Location.objects.all()
    context['locations'] = locations

    return render(request, 'location_mgt.html', context)

@login_required
def save_location(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            location = Location.objects.get(pk=request.POST['id'])
        else:
            location = None
        if location is None:
            form = SaveLocation(request.POST)
        else:
            form = SaveLocation(request.POST, instance= location)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_location(request, pk=None):
    context['page_title'] = "Manage Location"
    if not pk is None:
        location = Location.objects.get(id = pk)
        context['location'] = location
    else:
        context['location'] = {}

    return render(request, 'manage_location.html', context)

@login_required
def delete_location(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            location = Location.objects.get(id = request.POST['id'])
            location.delete()
            messages.success(request, 'Location has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'location has failed to delete'
            print(err)

    else:
        resp['msg'] = 'location has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")


# bus
@login_required
def bus_mgt(request):
    context['page_title'] = "Buses"
    buses = Bus.objects.all()
    context['buses'] = buses

    return render(request, 'bus_mgt.html', context)

@login_required
def save_bus(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            bus = Bus.objects.get(pk=request.POST['id'])
        else:
            bus = None
        if bus is None:
            form = SaveBus(request.POST)
        else:
            form = SaveBus(request.POST, instance= bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_bus(request, pk=None):
    context['page_title'] = "Manage Bus"
    categories = Category.objects.filter(status = 1).all()
    context['categories'] = categories
    if not pk is None:
        bus = Bus.objects.get(id = pk)
        context['bus'] = bus
    else:
        context['bus'] = {}

    return render(request, 'manage_bus.html', context)

@login_required
def delete_bus(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            bus = Bus.objects.get(id = request.POST['id'])
            bus.delete()
            messages.success(request, 'Bus has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'bus has failed to delete'
            print(err)

    else:
        resp['msg'] = 'bus has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")    


# schedule
@login_required
def schedule_mgt(request):
    context['page_title'] = "Trip Schedules"
    schedules = Schedule.objects.all()
    context['schedules'] = schedules

    return render(request, 'schedule_mgt.html', context)

@login_required
def save_schedule(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            schedule = Schedule.objects.get(pk=request.POST['id'])
        else:
            schedule = None
        if schedule is None:
            form = SaveSchedule(request.POST)
        else:
            form = SaveSchedule(request.POST, instance= schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_schedule(request, pk=None):
    context['page_title'] = "Manage Schedule"
    buses = Bus.objects.filter(status = 1).all()
    locations = Location.objects.filter(status = 1).all()
    context['buses'] = buses
    context['locations'] = locations
    if not pk is None:
        schedule = Schedule.objects.get(id = pk)
        context['schedule'] = schedule
    else:
        context['schedule'] = {}

    return render(request, 'manage_schedule.html', context)

@login_required
def delete_schedule(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            schedule = Schedule.objects.get(id = request.POST['id'])
            schedule.delete()
            messages.success(request, 'Schedule has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'schedule has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Schedule has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")  


# scheduled Trips
def scheduled_trips(request):
    if not request.method == 'POST':
        context['page_title'] = "Scheduled Trips"
        schedules = Schedule.objects.filter(status = 1, schedule__gt = datetime.now()).all()
        context['schedules'] = schedules
        context['is_searched'] = False
        context['data'] = {}
    else:
        context['page_title'] = "Search Result | Scheduled Trips"
        context['is_searched'] = True
        date = datetime.strptime(request.POST['date'],"%Y-%m-%d").date()
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        depart = Location.objects.get(id = request.POST['depart'])
        destination = Location.objects.get(id = request.POST['destination'])
        schedules = Schedule.objects.filter(Q(status = 1) & Q(schedule__year = year) & Q(schedule__month = month) & Q(schedule__day = day) & Q(Q(depart = depart) | Q(destination = destination ))).all()
        context['schedules'] = schedules
        context['data'] = {'date':date,'depart':depart, 'destination': destination}

    return render(request, 'scheduled_trips.html', context)

def manage_booking(request, schedPK=None, pk=None):
    context['page_title'] = "Manage Booking"
    context['schedPK'] = schedPK
    if not schedPK is None:
        schedule = Schedule.objects.get(id = schedPK)
        context['schedule'] = schedule
    else:
        context['schedule'] = {}
    if not pk is None:
        book = Booking.objects.get(id = pk)
        context['book'] = book
    else:
        context['book'] = {}

    return render(request, 'manage_book.html', context)

def save_booking(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            booking = Booking.objects.get(pk=request.POST['id'])
        else:
            booking = None
        if booking is None:
            form = SaveBooking(request.POST)
        else:
            form = SaveBooking(request.POST, instance= booking)
        if form.is_valid():
            form.save()
            if booking is None:
                booking = Booking.objects.last()
                messages.success(request, f'Booking has been saved successfully. Your Booking Refderence Code is: <b>{booking.code}</b>', extra_tags = 'stay')
            else:
                messages.success(request, f'<b>{booking.code}</b> Booking has been updated successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

def bookings(request):
    context['page_title'] = "Bookings"
    bookings = Booking.objects.all()
    context['bookings'] = bookings

    return render(request, 'bookings.html', context)


@login_required
def view_booking(request,pk=None):
    if pk is None:
        messages.error(request, "Unkown Booking ID")
        return redirect('booking-page')
    else:
        context['page_title'] = 'Vieww Booking'
        context['booking'] = Booking.objects.get(id = pk)
        return render(request, 'view_booked.html', context)


@login_required
def pay_booked(request):
    resp = {'status':'failed','msg':''}
    if not request.method == 'POST':
        resp['msg'] = "Unknown Booked ID"
    else:
        booking = Booking.objects.get(id= request.POST['id'])
        form = PayBooked(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, f"<b>{booking.code}</b> has been paid successfully", extra_tags='stay')
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += str(error + "<br>")
    
    return HttpResponse(json.dumps(resp),content_type = 'application/json')

@login_required
def delete_booking(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            booking = Booking.objects.get(id = request.POST['id'])
            code = booking.code
            booking.delete()
            messages.success(request, f'[<b>{code}</b>] Booking has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'booking has failed to delete'
            print(err)

    else:
        resp['msg'] = 'booking has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")  

def find_trip(request):
    context['page_title'] = 'Find Trip Schedule'
    context['locations'] = Location.objects.filter(status = 1).all
    today = datetime.today().strftime("%Y-%m-%d")
    context['today'] = today
    return render(request, 'find_trip.html', context)
def requisition_on(request):
    context['page_title'] = 'requisition'
    context['locations'] = Location.objects.filter(status = 1).all
    today = datetime.today().strftime("%Y-%m-%d")
    context['today'] = today
    return render(request, 'requisition-form.html', context)
# views.py

from django.shortcuts import render

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import Requisition  # Ensure Requisition model includes profession and email

# Function to create a requisition
def create_requisition(request):
    if request.method == 'POST':
        # Handle form submission
        date = request.POST.get('date')
        requested_by = request.POST.get('requested_by')
        faculty = request.POST.get('faculty')
        profession = request.POST.get('profession')  # New field for profession
        email = request.POST.get('email')  # New field for email
        purpose_of_trip = request.POST.get('purpose_of_trip')
        location_from = request.POST.get('location_from')
        location_to = request.POST.get('location_to')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date')
        number_of_passengers = request.POST.get('number_of_passengers')

        # Save requisition details to database
        requisition = Requisition.objects.create(
            date=date,
            requested_by=requested_by,
            faculty=faculty,
            profession=profession,  # Save profession
            email=email,            # Save email
            location_from=location_from,
            location_to=location_to,
            purpose_of_trip=purpose_of_trip,
            departure_date=departure_date,
            return_date=return_date,
            number_of_passengers=number_of_passengers
        )

        # Render a template to display the requisition details
        return render(request, 'requisition_details.html', {
            'requisition': requisition,  # Pass the requisition object to the template
        })
    else:
        # Render the form template
        return render(request, 'requisition.html')

# Function to save requisition via AJAX
@csrf_exempt  # only if you are using AJAX; otherwise, CSRF token is handled by Django form
def save_requisition(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        purpose_of_trip = request.POST.get('purpose_of_trip')
        requested_by = request.POST.get('requested_by')
        faculty = request.POST.get('faculty')
        profession = request.POST.get('profession')  # New field for profession
        email = request.POST.get('email')  # New field for email
        location_from = request.POST.get('location_from')
        location_to = request.POST.get('location_to')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date')
        number_of_passengers = request.POST.get('number_of_passengers')

        # Save the data to the database
        requisition = Requisition.objects.create(
            date=date,
            purpose_of_trip=purpose_of_trip,
            requested_by=requested_by,
            faculty=faculty,
            profession=profession,  # Save profession
            email=email,            # Save email
            location_from=location_from,
            location_to=location_to,
            departure_date=departure_date,
            return_date=return_date,
            number_of_passengers=number_of_passengers
        )
        requisition.save()

        return JsonResponse({"message": "Requisition saved successfully!"})

from django.core.mail import send_mail
from django.http import JsonResponse

def send_requisition_email(request):
    if request.method == 'POST':
        try:
            data = request.POST
            fixed_email = 'shyamsaikat16@cse.pstu.ac.bd'  # Set your fixed email address here
            
            subject = f"Requisition Details - {data.get('requested_by', 'Unknown')}"
            message = (
                f"Date: {data.get('date', 'N/A')}\n"
                f"Requested By: {data.get('requested_by', 'N/A')}\n"
                f"Faculty: {data.get('faculty', 'N/A')}\n"
                f"Profession: {data.get('profession', 'N/A')}\n"
                f"Email: {data.get('email', 'N/A')}\n"
                f"Location From: {data.get('location_from', 'N/A')}\n"
                f"Location To: {data.get('location_to', 'N/A')}\n"
                f"Purpose of Trip: {data.get('purpose_of_trip', 'N/A')}\n"
                f"Departure Date: {data.get('departure_date', 'N/A')}\n"
                f"Return Date: {data.get('return_date', 'N/A')}\n"
                f"Number of Passengers: {data.get('number_of_passengers', 'N/A')}\n"
            )
            
            recipient_list = [fixed_email]  # Use the fixed recipient email
            
            # Send the email
            send_mail(
                subject,
                message,
                None,  # Default sender (or you can specify one if required)
                recipient_list,
                fail_silently=False
            )
            
            # Return success response
            return JsonResponse({'message': 'Email sent successfully.'}, status=200)

        except Exception as e:
            # Log the error and return a failure response
            print(f"Error sending email: {e}")
            return JsonResponse({'error': 'Failed to send email. Please try again.'}, status=500)


from django.shortcuts import redirect
import requests
from django.urls import reverse
def initiate_payment(request):
    # Process form submission and get necessary data
    amount = request.POST.get('amount')
    order_id = request.POST.get('order_id')
    # Get other necessary data

    # Make a POST request to SSLCommerz API
    sslcommerz_data = {
        'store_id': 'pstut6601ab84d15f7',
        'store_password': 'pstut6601ab84d15f7@ssl',
        'currency': 'BDT',  # or any other currency
        'total_amount': amount,
        'tran_id': order_id,
        'success_url': request.build_absolute_uri(reverse('payment_success')),  # Dynamic success URL
        'fail_url': request.build_absolute_uri(reverse('payment_fail')),  # Dynamic fail URL
        'cancel_url': 'YOUR_CANCEL_URL',  # Redirect URL after canceled payment
        # Add other necessary data
    }

    # Send the request to SSLCommerz API
    response = requests.post('https://sandbox.sslcommerz.com/manage/', data=sslcommerz_data)

    # Assuming SSLCommerz returns a redirect URL
    redirect_url = response.json()['GatewayPageURL']

    # Redirect the user to SSLCommerz payment gateway
    return redirect(redirect_url)


# views.py

from django.shortcuts import render

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_fail(request):
    return render(request, 'payment_fail.html')
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Requisition  # Ensure Requisition model includes profession and email
from django.core.mail import send_mail  # Ensure this import is included

def requisition_list(request):
    requisitions = Requisition.objects.all()  # Fetch all requisition records
    return render(request, 'requisition_list.html', {'requisitions': requisitions})

def accept_requisition(request, pk):
    requisition = get_object_or_404(Requisition, pk=pk)
    requisition.status = 'accepted'  # Assuming you have a status field
    requisition.save()
    send_confirmation_email(requisition)  # Call a function to send email confirmation
    return redirect('requisition_list')  # Redirect to the list page

def reject_requisition(request, pk):
    requisition = get_object_or_404(Requisition, pk=pk)
    requisition.status = 'rejected'  # Assuming you have a status field
    requisition.save()
    send_rejection_email(requisition)  # Call a function to send email rejection
    return redirect('requisition_list')  # Redirect to the list page

def delete_requisition(request, id):
    requisition = get_object_or_404(Requisition, id=id)
    requisition.delete()
    return redirect('requisition_list')  # Redirect to the list page after deletion

# Optional: Functions to send confirmation and rejection emails
def send_confirmation_email(requisition):
    subject = f"Requisition {requisition.id} Accepted"
    message = (
        f"Your requisition has been accepted.\n"
        f"Requested By: {requisition.requested_by}\n"
        f"Profession: {requisition.profession}\n"
        f"Email: {requisition.email}\n"
        f"Purpose of Trip: {requisition.purpose_of_trip}\n"
        f"Departure Date: {requisition.departure_date}\n"
        f"Return Date: {requisition.return_date}\n"
        f"Status: {requisition.status}\n"
    )
    recipient_list = [requisition.email]  # Use the requisition's email
    send_mail(subject, message, None, recipient_list, fail_silently=False)

def send_rejection_email(requisition):
    subject = f"Requisition {requisition.id} Rejected"
    message = (
        f"Your requisition has been rejected.\n"
        f"Requested By: {requisition.requested_by}\n"
        f"Profession: {requisition.profession}\n"
        f"Email: {requisition.email}\n"
        f"Purpose of Trip: {requisition.purpose_of_trip}\n"
        f"Departure Date: {requisition.departure_date}\n"
        f"Return Date: {requisition.return_date}\n"
        f"Status: {requisition.status}\n"
    )
    recipient_list = [requisition.email]  # Use the requisition's email
    send_mail(subject, message, None, recipient_list, fail_silently=False)


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Seat
from .forms import SeatSelectionForm

def seat_selection_view(request):
    seats = Seat.objects.all()  # Fetch all seats and their statuses
    context = {
        'seats': seats
    }
    return render(request, 'seat_selection.html', context)

def submit_seat_selection(request):
    if request.method == 'POST':
        seat_number = request.POST.get('selected_seat')
        
        # Get the selected seat from the database
        try:
            selected_seat = Seat.objects.get(seat_number=seat_number)
        except Seat.DoesNotExist:
            return HttpResponse("Seat does not exist", status=400)
        
        # Check if the seat is available
        if selected_seat.status == 'available':
            selected_seat.status = 'selected'
            selected_seat.save()
            return HttpResponse("Seat selection successful!")
        else:
            return HttpResponse("Seat is already reserved or selected", status=400)
    
    return redirect('seat-selection')
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.conf import settings
from .models import Requisition  # Assuming you have a Requisition model

from django.core.mail import send_mail
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def send_mail_view(request):
    if request.method == 'POST':
        requisition_id = request.POST.get('requisition_id')
        driver_name = request.POST.get('driver_name')
        bus_number = request.POST.get('bus_number')
        status = request.POST.get('status')
        email = request.POST.get('email')

        subject = f"Requisition {requisition_id} - {status}"
        message = (
            f"Requisition ID: {requisition_id}\n"
            f"Driver Name: {driver_name}\n"
            f"Bus Number: {bus_number}\n"
            f"Status: {status}\n"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Email sent successfully!')
        except Exception as e:
            logger.error(f'Error sending email: {str(e)}')
            messages.error(request, 'There was an error sending the email.')
        
        return redirect('requisition_list')

def delete_requisition(request, id):
    requisition = get_object_or_404(Requisition, id=id)
    requisition.delete()
    return redirect('requisition_list')  # Redirect to the requisition list after deletion



