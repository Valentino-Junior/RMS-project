import json
import logging
from datetime import datetime
from io import BytesIO
import matplotlib
import tempfile
import os
from matplotlib import pyplot as plt
from django.contrib import messages  # Correct import for messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, user_passes_test  # Correct import for login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.timezone import make_aware
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from weasyprint import HTML

from Company import settings
from .forms import *
from .models import Email
from .models import *
from .modules import EmailService
from django.db.models import Sum


logger = logging.getLogger(__name__)

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'  # Specify your custom template
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Get default context
        website = Website.objects.all()  # Or use .all() if needed, adjust as necessary
        context['website'] = website  # Add custom data to the context
        return context

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'  # Specify your custom template
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Get the default context
        website = Website.objects.all()  # Or use .all() if needed, adjust as necessary
        context['website'] = website  # Add custom data to the context
        return context
        
class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'  # Specify your custom template
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Get the default context
        website = Website.objects.all()  # Or use .all() if needed, adjust as necessary
        context['website'] = website  # Add custom data to the context
        return context
        
def trigger_error(request):
    division_by_zero = 1 / 0

def index(request):
    # Query all the sections from the database
    section1_data = Section1.objects.all()
    section10_data = Section10.objects.all()
    section11_data = Section11.objects.all()
    section13_data = Section13.objects.all()
    website = Website.objects.all()
    group_users_data = GroupUsers.objects.all()

    # Initialize forms
    form = SubscriptionForm()
    messages_form = MessagesForm()

    # Prepare context data to be passed to the template
    context = {
        'section1_data': section1_data,
        'section10_data': section10_data,
        'section11_data': section11_data,
        'section13_data': section13_data,
        'website': website,
        'group_users_data': group_users_data,
        'subscription_messages': [message for message in messages.get_messages(request) if message.tags == 'subscription'],
        'messages_forms': [message for message in messages.get_messages(request) if message.tags != 'subscription']
    }

    if request.method == 'POST':
        if request.POST.get('form_type') == 'subscription':
            form = SubscriptionForm(request.POST)
            messages_form = MessagesForm()
            if not form.is_valid():
                messages.error(request, 'Email already exists! Please use a different email.')
            else:
                email = form.cleaned_data['email']
                if Subscription.objects.create(email=email):
                    messages.success(request, 'Subscription successful! Thank you for subscribing.')
                    return redirect('index')
            context['form'] = form
            context['messages_form'] = messages_form

    else:
        context['form'] = SubscriptionForm()
        context['messages_form'] = MessagesForm()

    if request.method == 'POST':
        if request.POST.get('form_type') == 'messages':
            messages_form = MessagesForm(request.POST)
            form = SubscriptionForm()
            if messages_form.is_valid():
                messages_form.save()
                messages.success(request, 'Message sent successfully!')
                return redirect('index')
            else:
                messages.error(request, 'Failed to send message. Please check your input.')
            context['form'] = form
            context['messages_form'] = messages_form
    elif request.method == 'POST':
        context['form'] = SubscriptionForm()
        context['messages_form'] = MessagesForm()
    # Render the template and pass the context data
    return render(request, 'index.html', context)
    
@login_required(login_url='/account/signin/')
def notifications(request):
    user = request.user

    # Retrieve notifications for the user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    # Update the read status for unread notifications
    unread_notifications = notifications.filter(read=False)
    unread_notifications.update(read=True)

    # Fetch profile picture if exists and ensure the image exists
    try:
        profile_picture = ProfilePicture.objects.get(user=user)
        # Ensure the image exists before trying to access its URL
        if not profile_picture.image or not profile_picture.image.name:
            profile_picture = None
    except ProfilePicture.DoesNotExist:
        profile_picture = None

    # Fetch website data (you may want to get a specific object, or all of them)
    website = Website.objects.all()  # Fetch all Website instances (or modify as needed)

    # Pass website data to the context
    context = {
        'notifications': notifications,
        'username': user.username,
        'email': user.email,
        'profile_picture': profile_picture,
        'website': website,  # Updated variable name
    }

    return render(request, 'account/notification.html', context)

def forgot(request):
    # Query the Website model to get the website data
    website = Website.objects.all()  # Query website model to get all data

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        email = request.POST.get('email')  # Get email from POST data

        # Check if the email is associated with a registered user
        if User.objects.filter(email=email).exists():
            if form.is_valid():  # Validate the form
                user = User.objects.get(email=email)  # Get the user object
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    token_generator=default_token_generator,  # Use the default token generator
                )
                messages.success(request, 'Password reset email has been sent.')
                return redirect('password_reset_done')
        else:
            messages.error(request, 'This email is not registered.')
    else:
        form = PasswordResetForm()

    # Pass website data to the template
    return render(request, 'account/forgot.html', {'form': form, 'website': website})
    
def password_reset_done(request, auth_views=None):
    website = Website.objects.all()
    return auth_views.PasswordResetDoneView.as_view(
        template_name='account/password_reset_done.html'
    )(request)

def password_reset_confirm(request, uidb64, token):
    global form
    website = Website.objects.all()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')

            if new_password1 != new_password2:
                messages.error(request, "Passwords do not match.")
            else:
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Your password has been reset successfully. Please log in.')
                    return redirect('signin')
                else:
                    messages.error(request, "There was an error with the form.")
        else:
            form = SetPasswordForm(user)
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('password_reset_done')

    return render(request, 'account/password_reset_confirm.html', {'form': form, 'website': website})

def password_reset_complete(request, auth_views=None):
    website = Website.objects.all()
    return auth_views.PasswordResetCompleteView.as_view(
        template_name='account/password_reset_complete.html'
    )(request)

def track_email_read(request, email_id):
    email = get_object_or_404(Email, id=email_id)
    if not email.is_read:
        EmailService.mark_as_read(email.id)

    # Return a 1x1 transparent pixel
    return HttpResponse(
        '<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" width="1" height="1"  style="display:none;" />'
    )

@login_required(login_url='/account/signin/')
def notifications(request):
    user = request.user

    # Retrieve notifications for the user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    # Update the read status for unread notifications
    unread_notifications = notifications.filter(read=False)
    unread_notifications.update(read=True)

    # Fetch profile picture if exists and ensure the image exists
    try:
        profile_picture = ProfilePicture.objects.get(user=user)
        # Ensure the image exists before trying to access its URL
        if not profile_picture.image or not profile_picture.image.name:
            profile_picture = None
    except ProfilePicture.DoesNotExist:
        profile_picture = None

    # Fetch website data (you may want to get a specific object, or all of them)
    website = Website.objects.all()  # Fetch all Website instances (or modify as needed)

    # Pass website data to the context
    context = {
        'notifications': notifications,
        'username': user.username,
        'email': user.email,
        'profile_picture': profile_picture,
        'website': website,  # Updated variable name
    }

    return render(request, 'account/notification.html', context)

def trigger_error(request):
    # This will raise a server error (division by zero)
    division_by_zero = 1 / 0

@login_required
def profile_view(request):
    # Fetch or create profile object
    profile, created = ProfilePicture.objects.get_or_create(user=request.user)

    # Initialize user_form, profile_form, and password_form
    user_form = UserProfileForm(instance=request.user)
    profile_form = ProfileForm(instance=profile)
    password_form = CustomPasswordChangeForm(user=request.user)

    # Fetch the profile picture safely
    profile_picture = None
    if profile.image and profile.image.name:
        profile_picture = profile

    # Handle form submissions (both AJAX and regular POST requests)
    if request.method == 'POST':
        action = request.POST.get('action')  # Identify the action (profile picture, user info, password change)

        # Handle Profile Picture Update (AJAX)
        if action == 'update_profile_picture':
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()  # Save the profile picture
                return JsonResponse({
                    'success': True,
                    'message': 'Profile picture updated successfully.',
                    'new_image_url': profile.image.url if profile.image else None  # Return the updated image URL for AJAX update
                })
            else:
                return JsonResponse({'success': False, 'message': 'Failed to update profile picture.'})

        # Handle User Info Update (First Name, Last Name, Email, Username)
        elif action == 'update_user_info':
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()  # Update user model fields (username, email, etc.)
                return JsonResponse({
                    'success': True,
                    'message': 'Your information has been updated successfully.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'There was an error updating your information. Please try again.'
                })

        # Handle Password Change
        elif action == 'change_password':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)  # Keep user logged in after password change
                return JsonResponse({
                    'success': True,
                    'message': 'Your password has been updated successfully.'
                })
            else:
                # Concatenate all form errors into a single message
                error_messages = "\n".join([str(error) for error in form.errors.values()])
                return JsonResponse({
                    'success': False,
                    'message': error_messages  # Concatenate errors for user-friendly message
                })

    # Format last login and date joined for human readability
    last_login = request.user.last_login
    date_joined = request.user.date_joined

    # Format the datetime fields (if they exist) for human-readable output
    if last_login:
        last_login = last_login.strftime('%B %d, %Y, %I:%M %p')  # Example: "October 18, 2024, 03:25 PM"
    else:
        last_login = 'N/A'

    if date_joined:
        date_joined = date_joined.strftime('%B %d, %Y, %I:%M %p')  # Example: "October 18, 2024, 03:25 PM"
    else:
        date_joined = 'N/A'

    # Render the profile template with the formatted dates
    return render(
        request,
        'account/profile.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
            'profile_picture': profile_picture,  # Pass profile picture if it exists
            'username': request.user.username,  # Pass username
            'email': request.user.email,  # Pass email
            'first_name': request.user.first_name,  # Pass first name
            'last_name': request.user.last_name,  # Pass last name
            'last_login': last_login,  # Pass formatted last login
            'date_joined': date_joined,  # Pass formatted date joined
        }
    )

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)

        # Check if it's an AJAX request
        if request.is_ajax():
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)  # Keep the user logged in after password change
                return JsonResponse({
                    'success': True,
                    'message': 'Your password has been updated successfully.'
                })
            else:
                # Concatenate all form errors into a single message
                error_messages = "\n".join([str(error) for error in form.errors.values()])
                return JsonResponse({
                    'success': False,
                    'message': error_messages  # Concatenate errors for user-friendly message
                })

    # Non-AJAX POST requests (redirect or render the form again)
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'account/profile.html', {'form': form})

@login_required
def update_user_info(request):
    """View to handle changes for First Name, Last Name, Email, and Username."""
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your information has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'There was an error updating your information. Please try again.')
    else:
        user_form = UserProfileForm(instance=request.user)

    return render(request, 'account/profile.html', {'user_form': user_form})


def signin(request):
    context = {
        'error_message': None
    }

    # Query the Website model to get website data
    website = Website.objects.all()  # Query website model

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Check if the input is an email or username
        if '@' in username_or_email:
            # If it's an email, use it to authenticate
            user = authenticate(request, username=username_or_email, password=password)
        else:
            # If it's a username, use it to authenticate
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)

            # Add user to 'User' group
            group, created = Group.objects.get_or_create(name='User')
            if not user.groups.filter(name='User').exists():
                user.groups.add(group)

            return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            context['error_message'] = "Invalid username/email or password. Please try again."

    # Add the website data to the context before rendering the template
    context['website'] = website

    # Render the signin template with the context
    return render(request, 'account/signin.html', context)

def signout(request):
    logout(request)
    return redirect('account')

def activate(request, uidb64, token):
    context = {
        'error_message': None,
        'success_message': None,
        'website': Website.objects.all()  # Adding Website data to the context
    }

    try:
        # Decode the uid and get the corresponding user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Activate the user account
        user.is_active = True
        user.save()

        # Success message
        messages.success(request, 'Your account has been activated successfully.')
        context['success_message'] = "Your account has been activated. You can now log in."

        # Send the user a confirmation email with the login link
        send_login_link_email(user, request)

        # Redirect user to the login page (signin.html)
        return render(request, 'account/signin.html', context)
    else:
        # If the token is invalid or expired
        messages.error(request, 'The activation link is invalid or has expired.')
        context['error_message'] = "The activation link is invalid or expired. Please request a new one."

        return render(request, 'account/signup.html', context)

def send_login_link_email(user, request):
    """Send the user an email with the login link after account activation."""
    subject = f"Welcome to {settings.SITE_NAME} - Account Activated"
    from_email = settings.DEFAULT_FROM_EMAIL

    # Get the domain of the current site (subdomain + domain)
    current_site = get_current_site(request)

    # Force HTTPS for the login URL (Ensure the URL starts with https://)
    login_url = f"https://{current_site.domain}/account/signin/"

    # Fetch website data (if needed)
    website = Website.objects.all()  # Adding Website data to the email context

    # Context for the email
    context = {
        'user': user,
        'login_url': login_url,  # The login link after activation
        'site_name': settings.SITE_NAME,  # Use the root domain for site_name
        'username': user.username,
        'domain': current_site.domain,  # Include the current subdomain for the link
        'website': website  # Adding website data to the email context if necessary
    }

    # Render the email body from a template (plain-text)
    message = render_to_string('account/login_link_email.txt', context)

    # Send the email
    send_mail(subject, message, from_email, [user.email])

def signup(request):
    context = {
        'error_message': None,
        'success_message': None,
        'business_categories': BusinessCategory.objects.all(),
        'website': Website.objects.all(),  # Fetch website data to display
    }

    # Create a dictionary to hold categories and their subcategories
    business_subcategories = {}
    for category in context['business_categories']:
        business_subcategories[category.id] = BusinessSubCategory.objects.filter(category=category)

    if request.method == 'POST':
        # Collect user and company details
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        company_name = request.POST.get('company_name')
        license_number = request.POST.get('license_number')
        company_email = request.POST.get('company_email')
        company_phone = request.POST.get('company_phone')
        company_address = request.POST.get('company_address')

        # Business category and subcategories
        business_category_ids = request.POST.getlist('categories')
        business_categories = BusinessCategory.objects.filter(id__in=business_category_ids)

        # Collect selected subcategories
        business_subcategory_ids = []
        for category_id in business_category_ids:
            subcategory_ids = request.POST.getlist(f'subcategories_{category_id}[]')
            business_subcategory_ids.extend(subcategory_ids)

        # Get selected subcategories from the database
        business_subcategories_selected = BusinessSubCategory.objects.filter(id__in=business_subcategory_ids)

        # Validation: Ensure all fields are filled
        if not (username and email and password and phone and company_name and license_number and company_email and company_phone and company_address):
            context['error_message'] = "Please fill out all required fields."
            return render(request, 'account/signup.html', context)

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            context['error_message'] = "Username already exists."
            return render(request, 'account/signup.html', context)

        if User.objects.filter(email=email).exists():
            context['error_message'] = "Email already exists."
            return render(request, 'account/signup.html', context)

        # Create the user (inactive until email is verified)
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # Set user as inactive until email is verified
        user.save()

        # Create Company Profile
        company_profile = CompanyProfile.objects.create(
            user=user,
            company_name=company_name,
            license_number=license_number,
            company_email=company_email,
            company_phone=company_phone,
            company_address=company_address
        )
        company_profile.business_categories.set(business_categories)
        company_profile.business_subcategories.set(business_subcategories_selected)
        company_profile.save()

        # Generate token and uid for email verification
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        # Get current domain and root domain for email
        current_site = get_current_site(request)
        root_domain = settings.SITE_NAME  # The root domain (e.g., kncmap.com)

        # Prepare the email message
        mail_subject = "Activate your account"
        activation_link = f"https://{current_site.domain}/account/activate/{uid}/{token}/"

        # Prepare the context for the email
        context_email = {
            'user': user,
            'domain': current_site.domain,  # Current domain (subdomain + domain)
            'uid': uid,
            'token': token,
            'site_name': root_domain,  # Use the root domain (e.g., kncmap.com)
            'activation_link': activation_link,
        }

        # Render the email body from the template
        message = render_to_string('account/activation_email.txt', context_email)

        # Send the email
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        # Set success message
        context['success_message'] = "Registration successful! Please check your email to verify your account."
        return render(request, 'account/signup.html', context)

    # Pass business subcategories to the template
    context['business_subcategories'] = business_subcategories  # Dictionary of categories and their subcategories

    return render(request, 'account/signup.html', context)

# Handle AJAX request to fetch subcategories
def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = BusinessSubCategory.objects.filter(category_id=category_id)
    subcategory_data = [{"id": sub.id, "name": sub.name} for sub in subcategories]
    return JsonResponse(subcategory_data, safe=False)

def forbidden(request, exception):
    website = Website.objects.all()
    context = {'website': website}
    return render(request, 'account/403.html', context=context, status=403)

def error(request, exception):
    website = Website.objects.all()
    context = {'website': website}
    return render(request, 'account/404.html', context=context, status=404)

def server_error(request):
    website = Website.objects.all()
    context = {'website': website}
    return render(request, 'account/500.html', context=context, status=500)

@login_required(login_url='/account/signin/')
def dashboard(request):
    # Handle POST requests (form submissions) first
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'bookmaker':
            form = BookmakerForm(request.POST)
            if form.is_valid():
                BookmakerSubmission.objects.create(
                    user=request.user,
                    category=form.cleaned_data['category'],
                    subcategory=None,  # Set to None for non-lottery submissions
                    date=form.cleaned_data['date'],
                    sales=form.cleaned_data['sales'],
                    payout=form.cleaned_data['payout'],
                    win_loss=form.cleaned_data['win_loss']
                )
                messages.success(request, 'Bookmaker submission successful!')
                return redirect('dashboard')
                
        elif form_type == 'online_gaming':
            form = OnlineGamingForm(request.POST)
            if form.is_valid():
                OnlineGamingSubmission.objects.create(
                    user=request.user,
                    category=form.cleaned_data['category'],
                    subcategory=None,  # Set to None for non-lottery submissions
                    date=form.cleaned_data['date'],
                    total_sales=form.cleaned_data['total_sales'],
                    total_payout=form.cleaned_data['total_payout'],
                    ggr=form.cleaned_data['ggr']
                )
                messages.success(request, 'Online Gaming submission successful!')
                return redirect('dashboard')
                
        elif form_type == 'physical_casino':
            form = PhysicalCasinoForm(request.POST)
            if form.is_valid():
                PhysicalCasinoSubmission.objects.create(
                    user=request.user,
                    category=form.cleaned_data['category'],
                    subcategory=None,  # Set to None for non-lottery submissions
                    date=form.cleaned_data['date'],
                    amount_totals=form.cleaned_data['amount_totals']
                )
                messages.success(request, 'Physical Casino submission successful!')
                return redirect('dashboard')
                
        elif form_type == 'lottery':
            form = LotteryForm(request.POST)
            if form.is_valid():
                LotterySubmission.objects.create(
                    user=request.user,
                    category=form.cleaned_data['category'],
                    subcategory=form.cleaned_data['subcategory'],
                    date=form.cleaned_data['date'],
                    sales=form.cleaned_data['sales'],
                    payout=form.cleaned_data['payout'],
                    win_loss=form.cleaned_data['win_loss']
                )
                messages.success(request, 'Lottery submission successful!')
                return redirect('dashboard')

        if not form.is_valid():
            messages.error(request, 'Please correct the errors in the form.')

    # Get filter parameters
    submission_type = request.GET.get('submission_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Fetch user's profile picture
    profile_picture = ProfilePicture.objects.get(user=request.user) if ProfilePicture.objects.filter(user=request.user).exists() else None

    # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=request.user, read=False).count()

    # Fetch the user's profile data
    profile = Profile.objects.get(user=request.user) if Profile.objects.filter(user=request.user).exists() else None

    # Fetch website data
    website = Website.objects.all()

    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Base querysets
    bookmaker_submissions = BookmakerSubmission.objects.filter(user=request.user)
    online_gaming_submissions = OnlineGamingSubmission.objects.filter(user=request.user)
    physical_casino_submissions = PhysicalCasinoSubmission.objects.filter(user=request.user)
    lottery_submissions = LotterySubmission.objects.filter(user=request.user)

    # Apply date filters if provided
    if start_date and end_date:
        start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
        
        bookmaker_submissions = bookmaker_submissions.filter(date__range=[start_date, end_date])
        online_gaming_submissions = online_gaming_submissions.filter(date__range=[start_date, end_date])
        physical_casino_submissions = physical_casino_submissions.filter(date__range=[start_date, end_date])
        lottery_submissions = lottery_submissions.filter(date__range=[start_date, end_date])

    # Calculate totals for each type
    bookmaker_totals = bookmaker_submissions.aggregate(
        total_sales=Sum('sales'),
        total_payout=Sum('payout'),
        total_win_loss=Sum('win_loss')
    )

    online_gaming_totals = online_gaming_submissions.aggregate(
        total_sales=Sum('total_sales'),
        total_payout=Sum('total_payout'),
        total_ggr=Sum('ggr')
    )

    physical_casino_totals = physical_casino_submissions.aggregate(
        total_amount=Sum('amount_totals')
    )

    lottery_totals = lottery_submissions.aggregate(
        total_sales=Sum('sales'),
        total_payout=Sum('payout'),
        total_win_loss=Sum('win_loss')
    )

    # Initialize empty list for all submissions
    all_submissions = []

    # Add submissions based on filter
    if not submission_type or submission_type == 'bookmaker':
        for submission in bookmaker_submissions:
            all_submissions.append({
                'date': submission.date,
                'type': 'Bookmaker',
                'category': submission.category.name if submission.category else 'N/A',
                'subcategory': 'N/A',
                'sales': submission.sales,
                'payout': submission.payout,
                'win_loss': submission.win_loss,
                'total_sales': None,
                'total_payout': None,
                'ggr': None,
                'amount_totals': None
            })

    if not submission_type or submission_type == 'online_gaming':
        for submission in online_gaming_submissions:
            all_submissions.append({
                'date': submission.date,
                'type': 'Online Gaming',
                'category': submission.category.name if submission.category else 'N/A',
                'subcategory': 'N/A',
                'sales': None,
                'payout': None,
                'win_loss': None,
                'total_sales': submission.total_sales,
                'total_payout': submission.total_payout,
                'ggr': submission.ggr,
                'amount_totals': None
            })

    if not submission_type or submission_type == 'physical_casino':
        for submission in physical_casino_submissions:
            all_submissions.append({
                'date': submission.date,
                'type': 'Physical Casino',
                'category': submission.category.name if submission.category else 'N/A',
                'subcategory': 'N/A',
                'sales': None,
                'payout': None,
                'win_loss': None,
                'total_sales': None,
                'total_payout': None,
                'ggr': None,
                'amount_totals': submission.amount_totals
            })

    if not submission_type or submission_type == 'lottery':
        for submission in lottery_submissions:
            all_submissions.append({
                'date': submission.date,
                'type': 'Lottery',
                'category': submission.category.name if submission.category else 'N/A',
                'subcategory': submission.subcategory.name if submission.subcategory else 'N/A',
                'sales': submission.sales,
                'payout': submission.payout,
                'win_loss': submission.win_loss,
                'total_sales': None,
                'total_payout': None,
                'ggr': None,
                'amount_totals': None
            })

    # Sort all submissions by date
    all_submissions.sort(key=lambda x: x['date'], reverse=True)

    # Calculate grand totals
    total_sales = (
        (bookmaker_totals['total_sales'] or 0) +
        (online_gaming_totals['total_sales'] or 0) +
        (lottery_totals['total_sales'] or 0)
    )

    total_payout = (
        (bookmaker_totals['total_payout'] or 0) +
        (online_gaming_totals['total_payout'] or 0) +
        (lottery_totals['total_payout'] or 0)
    )

    total_win_loss = (
        (bookmaker_totals['total_win_loss'] or 0) +
        (online_gaming_totals['total_ggr'] or 0) +
        (lottery_totals['total_win_loss'] or 0) +
        (physical_casino_totals['total_amount'] or 0)
    )

    # Get activity data with better error handling
    try:
        # Login frequency data
        login_frequency = Notification.objects.filter(
            created_at__month=current_month,
            created_at__year=current_year
        ).values('created_at__day').annotate(
            count=Count('created_at')
        ).order_by('created_at__day')

        # Convert QuerySet to lists for JSON serialization
        login_frequency_labels = json.dumps([str(day['created_at__day']) for day in login_frequency])
        login_frequency_data = json.dumps([day['count'] for day in login_frequency])

        # Notification frequency data
        notification_frequency = Notification.objects.filter(
            user=request.user,
            created_at__month=current_month,
            created_at__year=current_year
        ).values('created_at__day').annotate(
            count=Count('created_at')
        ).order_by('created_at__day')

        notification_frequency_labels = json.dumps([str(day['created_at__day']) for day in notification_frequency])
        notification_frequency_data = json.dumps([day['count'] for day in notification_frequency])

        # Account updates
        account_updates = ProfilePicture.objects.filter(
            user=request.user,
            updated_at__month=current_month,
            updated_at__year=current_year
        ).count()

    except Exception as e:
        print(f"Error fetching chart data: {str(e)}")
        login_frequency_labels = json.dumps([])
        login_frequency_data = json.dumps([])
        notification_frequency_labels = json.dumps([])
        notification_frequency_data = json.dumps([])
        account_updates = 0

    # Prepare forms
    bookmaker_form = BookmakerForm()
    online_gaming_form = OnlineGamingForm()
    physical_casino_form = PhysicalCasinoForm()
    lottery_form = LotteryForm()

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'profile_picture': profile_picture,
        'unread_notifications_count': unread_notifications_count,
        'profile': profile,
        'website': website,
        'last_login': request.user.last_login,
        'date_joined': request.user.date_joined,
        'login_frequency_labels': login_frequency_labels,
        'login_frequency_data': login_frequency_data,
        'notification_frequency_labels': notification_frequency_labels,
        'notification_frequency_data': notification_frequency_data,
        'account_updates': account_updates,
        'user_submissions': all_submissions,
        'total_sales': total_sales,
        'total_payout': total_payout,
        'total_win_loss': total_win_loss,
        'bookmaker_form': bookmaker_form,
        'online_gaming_form': online_gaming_form,
        'physical_casino_form': physical_casino_form,
        'lottery_form': lottery_form,
        'selected_type': submission_type,
        'start_date': start_date.strftime("%Y-%m-%d") if start_date else "",
        'end_date': end_date.strftime("%Y-%m-%d") if end_date else "",
        'submission_types': [
            ('', 'All Types'),
            ('bookmaker', 'Bookmaker'),
            ('online_gaming', 'Online Gaming'),
            ('physical_casino', 'Physical Casino'),
            ('lottery', 'Lottery')
        ]
    }

    return render(request, 'account/dashboard.html', context)

@login_required
def generate_pdf(request):
    # Get the start and end date from the GET request
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # If both dates are provided, parse them
    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
    else:
        # Default to current date range if no date is selected (optional)
        start_date = datetime.now().replace(day=1)  # Start of the current month
        end_date = datetime.now()  # Today

    # Convert dates to "aware" datetime objects to handle time zone issues if needed
    start_date = make_aware(datetime.combine(start_date, datetime.min.time()))
    end_date = make_aware(datetime.combine(end_date, datetime.max.time()))

    # Filter the data based on the selected date range
    bookmaker_data = BookmakerSubmission.objects.filter(user=request.user, date__range=[start_date, end_date])
    online_gaming_data = OnlineGamingSubmission.objects.filter(user=request.user, date__range=[start_date, end_date])
    physical_casino_data = PhysicalCasinoSubmission.objects.filter(user=request.user, date__range=[start_date, end_date])
    lottery_data = LotterySubmission.objects.filter(user=request.user, date__range=[start_date, end_date])

    # Check if any data exists and log for debugging
    print(f"Bookmaker Data: {bookmaker_data.count()}")
    print(f"Online Gaming Data: {online_gaming_data.count()}")
    print(f"Physical Casino Data: {physical_casino_data.count()}")
    print(f"Lottery Data: {lottery_data.count()}")

    # Retrieve the company profile for the logged-in user
    try:
        company_profile = CompanyProfile.objects.get(user=request.user)
        company_name = company_profile.company_name  # Access the company name
    except CompanyProfile.DoesNotExist:
        company_name = "Unknown Company"  # Fallback if no company profile exists for the user

    # Create a BytesIO buffer to hold the PDF content
    buffer = BytesIO()

    # Create a PDF object using reportlab's canvas
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # These are the dimensions of the page

    # Add Title
    p.setFont("Helvetica", 12)
    p.drawString(200, height - 50, f"Report for {request.user.username}")

    # Add Company Name and Business Category
    y_position = height - 100
    p.drawString(50, y_position, f"Company Name: {company_name}")  # Use company_name from CompanyProfile
    y_position -= 20
    p.drawString(50, y_position, f"Business Category: User Submissions")

    # Add Returns Data (Bookmaker, Online Gaming, Physical Casino, and Lottery)
    data_categories = {
        'Bookmaker': bookmaker_data,
        'Online Gaming': online_gaming_data,
        'Physical Casino': physical_casino_data,
        'Lottery': lottery_data
    }

    # Loop through each category and print the corresponding data
    for category, data in data_categories.items():
        y_position -= 40
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y_position, f"{category} Data:")
        y_position -= 20

        p.setFont("Helvetica", 8)
        for entry in data:
            # Create the string for the data, dynamically including relevant fields
            entry_details = f"Date: {entry.date.strftime('%b. %d, %Y')}"

            if hasattr(entry, 'sales'):
                entry_details += f"  Sales: {entry.sales}"
            if hasattr(entry, 'payout'):
                entry_details += f"  Payout: {entry.payout}"
            if hasattr(entry, 'win_loss'):
                entry_details += f"  Win/Loss: {entry.win_loss}"
            if hasattr(entry, 'ggr'):
                entry_details += f"  GGR: {entry.ggr}"
            if hasattr(entry, 'amount_totals'):
                entry_details += f"  Amount Totals: {entry.amount_totals}"

            # Print the data entry
            p.drawString(50, y_position, entry_details)
            y_position -= 20

            # If near the bottom of the page, add a new page
            if y_position < 100:
                p.showPage()
                y_position = height - 50

    # Finalize the PDF
    p.showPage()
    p.save()

    # Get the PDF content from the buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Send the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="user_report.pdf"'
    return response



def get_subcategories(request):
    category_id = request.GET.get('category_id')
    try:
        subcategories = BusinessSubCategory.objects.filter(category_id=category_id)
        data = list(subcategories.values('id', 'name'))
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def profile_view(request):
    # Fetch or create profile object
    profile, created = ProfilePicture.objects.get_or_create(user=request.user)

    # Initialize user_form, profile_form, and password_form
    user_form = UserProfileForm(instance=request.user)
    profile_form = ProfileForm(instance=profile)
    password_form = CustomPasswordChangeForm(user=request.user)

    # Fetch the profile picture safely
    profile_picture = None
    if profile.image and profile.image.name:
        profile_picture = profile

    # Fetch website data
    website = Website.objects.all()  # Fetch all Website instances (You can modify this as needed)

    # Handle form submissions (both AJAX and regular POST requests)
    if request.method == 'POST':
        action = request.POST.get('action')  # Identify the action (profile picture, user info, password change)

        # Handle Profile Picture Update (AJAX)
        if action == 'update_profile_picture':
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()  # Save the profile picture
                return JsonResponse({
                    'success': True,
                    'message': 'Profile picture updated successfully.',
                    'new_image_url': profile.image.url if profile.image else None  # Return the updated image URL for AJAX update
                })
            else:
                return JsonResponse({'success': False, 'message': 'Failed to update profile picture.'})

        # Handle User Info Update (First Name, Last Name, Email, Username)
        elif action == 'update_user_info':
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()  # Update user model fields (username, email, etc.)
                return JsonResponse({
                    'success': True,
                    'message': 'Your information has been updated successfully.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'There was an error updating your information. Please try again.' 
                })

        # Handle Password Change
        elif action == 'change_password':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)  # Keep user logged in after password change
                return JsonResponse({
                    'success': True,
                    'message': 'Your password has been updated successfully.'
                })
            else:
                # Concatenate all form errors into a single message
                error_messages = "\n".join([str(error) for error in form.errors.values()])
                return JsonResponse({
                    'success': False,
                    'message': error_messages  # Concatenate errors for user-friendly message
                })

    # Format last login and date joined for human readability
    last_login = request.user.last_login
    date_joined = request.user.date_joined

    # Format the datetime fields (if they exist) for human-readable output
    if last_login:
        last_login = last_login.strftime('%B %d, %Y, %I:%M %p')  # Example: "October 18, 2024, 03:25 PM"
    else:
        last_login = 'N/A'

    if date_joined:
        date_joined = date_joined.strftime('%B %d, %Y, %I:%M %p')  # Example: "October 18, 2024, 03:25 PM"
    else:
        date_joined = 'N/A'

    # Render the profile template with the formatted dates and website data
    return render(
        request,
        'account/profile.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
            'profile_picture': profile_picture,  # Pass profile picture if it exists
            'username': request.user.username,  # Pass username
            'email': request.user.email,  # Pass email
            'first_name': request.user.first_name,  # Pass first name
            'last_name': request.user.last_name,  # Pass last name
            'last_login': last_login,  # Pass formatted last login
            'date_joined': date_joined,  # Pass formatted date joined
            'website': website,  # Pass Website data to the template
        }
    )
    
def signout(request):
    logout(request)
    return redirect('../')

@login_required  # Ensure the user must be logged in
def send_email_view(request):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=403)

    if request.method == 'POST':
        recipients = request.POST.getlist('recipients')  # Get multiple emails from the form
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        # Handle additional emails
        additional_emails = request.POST.get('additional_emails', '').split(',')
        # Clean up additional emails
        additional_emails = [email.strip() for email in additional_emails if email.strip()]

        # Combine the recipient lists for emails
        all_recipients = recipients + additional_emails

        # Sending the email to each recipient
        for recipient in all_recipients:
            sent_successfully = EmailService.send_email(
                recipient=recipient,
                subject=subject,
                body=body
            )

            if not sent_successfully:
                messages.error(request, f'Failed to send email to {recipient}.')
                break  # Stop sending if any email fails
        else:
            messages.success(request, 'Emails sent successfully!')

        return redirect('send_email')  # Redirect back to the same page

    # For GET requests, display the user email selection form
    users = User.objects.all()  # Fetch all users
    user_name = request.user.get_full_name()  # Get the logged-in user's name

    # Get the profile picture for the navbar
    try:
        profile_picture = ProfilePicture.objects.get(user=request.user)
        # Ensure the image exists before trying to access its URL
        if not profile_picture.image or not profile_picture.image.name:
            profile_picture = None
    except ProfilePicture.DoesNotExist:
        profile_picture = None
        
    website = Website.objects.all()

    username = request.user.username

    return render(request, 'account/send_email.html', {
        'users': users,
        'user_name': user_name,
        'profile_picture': profile_picture,
        'username': username,
        'email': request.user.email,
        'website': website,
    })
    
def secure_email_read(request, email_id):
    # Fetch the email by ID
    email = get_object_or_404(Email, id=email_id)

    # Track if the email was read
    if not email.is_read:
        email.is_read = True
        email.read_at = timezone.now()  # Mark the current time as the read time
        email.save()

    # Logic to retrieve the User's name by their email address
    user_name = "User"  # Default name if not found
    if email.recipient:
        try:
            user = User.objects.get(email=email.recipient)
            user_name = user.username  # Get the username of the recipient
        except User.DoesNotExist:
            user_name = "User"  # If no user found, keep the default name

    # Fetch website-related data (Just using 'website' here as the variable)
    website = Website.objects.all()

    # Prepare context with website data and email content
    context = {
        'email_body': email.body, 
        'user_name': user_name,
        'website': website  # Using 'website' directly here
    }

    # Render the email content with the user's name and website data
    return render(request, 'account/email_template.html', context)
    
def about(request):
 
    about_info = About.objects.all()
    section1_data = Section1.objects.all()
    section10_data = Section10.objects.all()
    section11_data = Section11.objects.all()
    section13_data = Section13.objects.all()
    website = Website.objects.all()
    group_users_data = GroupUsers.objects.all()

    # Initialize forms
    form = SubscriptionForm()
    messages_form = MessagesForm()

    # Prepare context data to be passed to the template
    context = {
        'about': about_info,  
        'section1_data': section1_data,
        'section10_data': section10_data,
        'section11_data': section11_data,
        'section13_data': section13_data,
        'website': website,
        'group_users_data': group_users_data,
        'subscription_messages': [message for message in messages.get_messages(request) if message.tags == 'subscription'],
        'messages_forms': [message for message in messages.get_messages(request) if message.tags != 'subscription'],
    }

    # Handling the Subscription Form submission
    if request.method == 'POST':
        if request.POST.get('form_type') == 'subscription':
            form = SubscriptionForm(request.POST)
            messages_form = MessagesForm()
            if not form.is_valid():
                messages.error(request, 'Email already exists! Please use a different email.')
            else:
                email = form.cleaned_data['email']
                if Subscription.objects.create(email=email):
                    messages.success(request, 'Subscription successful! Thank you for subscribing.')
                    return redirect('about')  # Redirect to the about page after successful subscription
            context['form'] = form
            context['messages_form'] = messages_form

        elif request.POST.get('form_type') == 'messages':
            messages_form = MessagesForm(request.POST)
            form = SubscriptionForm()
            if messages_form.is_valid():
                messages_form.save()
                messages.success(request, 'Message sent successfully!')
                return redirect('about')  # Redirect to the about page after successful message
            else:
                messages.error(request, 'Failed to send message. Please check your input.')
            context['form'] = form
            context['messages_form'] = messages_form
    else:
        context['form'] = SubscriptionForm()
        context['messages_form'] = MessagesForm()

    # Render the 'about.html' template with all context data
    return render(request, 'about.html', context)

# Function to check if the user is an admin
def is_admin_user(user):
    return user.is_staff  # Assuming admin users are staff members


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
   # Get filter parameters
   start_date = request.GET.get('start_date')
   end_date = request.GET.get('end_date')
   submission_type = request.GET.get('submission_type')
   company_name = request.GET.get('company_name')

   # Base querysets 
   bookmaker_data = BookmakerSubmission.objects.all()
   online_gaming_data = OnlineGamingSubmission.objects.all()
   physical_casino_data = PhysicalCasinoSubmission.objects.all()
   lottery_data = LotterySubmission.objects.all()

   # Apply company name filter if provided
   if company_name:
       bookmaker_data = bookmaker_data.filter(user__companyprofile__company_name__icontains=company_name)
       online_gaming_data = online_gaming_data.filter(user__companyprofile__company_name__icontains=company_name)
       physical_casino_data = physical_casino_data.filter(user__companyprofile__company_name__icontains=company_name)
       lottery_data = lottery_data.filter(user__companyprofile__company_name__icontains=company_name)

   # Apply date filters if provided
   if start_date and end_date:
       start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
       end_date = make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
       
       bookmaker_data = bookmaker_data.filter(date__range=[start_date, end_date])
       online_gaming_data = online_gaming_data.filter(date__range=[start_date, end_date])
       physical_casino_data = physical_casino_data.filter(date__range=[start_date, end_date])
       lottery_data = lottery_data.filter(date__range=[start_date, end_date])

   # Apply submission type filter if provided
   if submission_type:
       if submission_type == 'bookmaker':
           online_gaming_data = online_gaming_data.none()
           physical_casino_data = physical_casino_data.none()
           lottery_data = lottery_data.none()
       elif submission_type == 'online_gaming':
           bookmaker_data = bookmaker_data.none()
           physical_casino_data = physical_casino_data.none()
           lottery_data = lottery_data.none()
       elif submission_type == 'physical_casino':
           bookmaker_data = bookmaker_data.none()
           online_gaming_data = online_gaming_data.none()
           lottery_data = lottery_data.none()
       elif submission_type == 'lottery':
           bookmaker_data = bookmaker_data.none()
           online_gaming_data = online_gaming_data.none()
           physical_casino_data = physical_casino_data.none()

   # Get unique company names for dropdown
   company_profiles = CompanyProfile.objects.all().values_list('company_name', flat=True).distinct()

   # Calculate totals with proper aggregation
   bookmaker_totals = bookmaker_data.aggregate(
       total_sales=Sum('sales'),
       total_payout=Sum('payout'),
       total_win_loss=Sum('win_loss')
   )
   
   online_gaming_totals = online_gaming_data.aggregate(
       total_sales=Sum('total_sales'),
       total_payout=Sum('total_payout'),
       total_ggr=Sum('ggr')
   )
   
   lottery_totals = lottery_data.aggregate(
       total_sales=Sum('sales'),
       total_payout=Sum('payout'),
       total_win_loss=Sum('win_loss')
   )
   
   physical_casino_totals = physical_casino_data.aggregate(
       total_amount=Sum('amount_totals')
   )

   # Calculate grand totals
   total_sales = (
       (bookmaker_totals['total_sales'] or 0) +
       (online_gaming_totals['total_sales'] or 0) +
       (lottery_totals['total_sales'] or 0) +
       (physical_casino_totals['total_amount'] or 0)
   )

   total_payout = (
       (bookmaker_totals['total_payout'] or 0) +
       (online_gaming_totals['total_payout'] or 0) +
       (lottery_totals['total_payout'] or 0)
   )

   total_win_loss = (
       (bookmaker_totals['total_win_loss'] or 0) +
       (online_gaming_totals['total_ggr'] or 0) +
       (lottery_totals['total_win_loss'] or 0) +
       (physical_casino_totals['total_amount'] or 0)
   )

   # Prepare submission type distribution
   submission_distribution = {
    'Bookmaker': bookmaker_data.count(),
    'Online_Gaming': online_gaming_data.count(),
    'Physical_Casino': physical_casino_data.count(),
    'Lottery': lottery_data.count()
}

   # Combine all submissions for the table view
   all_submissions = []
   
   for submission in bookmaker_data:
       all_submissions.append({
           'date': submission.date,
           'type': 'Bookmaker',
           'user': submission.user.username,
           'company_name': submission.user.companyprofile.company_name,
           'sales': submission.sales,
           'payout': submission.payout,
           'win_loss': submission.win_loss,
       })

   for submission in online_gaming_data:
       all_submissions.append({
           'date': submission.date,
           'type': 'Online Gaming',
           'user': submission.user.username,
           'company_name': submission.user.companyprofile.company_name,
           'sales': submission.total_sales,
           'payout': submission.total_payout,
           'win_loss': submission.ggr,
       })

   for submission in physical_casino_data:
       all_submissions.append({
           'date': submission.date,
           'type': 'Physical Casino',
           'user': submission.user.username,
           'company_name': submission.user.companyprofile.company_name,
           'sales': submission.amount_totals,
           'payout': 0,
           'win_loss': submission.amount_totals,
       })

   for submission in lottery_data:
       all_submissions.append({
           'date': submission.date,
           'type': 'Lottery',
           'user': submission.user.username,
           'company_name': submission.user.companyprofile.company_name,
           'sales': submission.sales,
           'payout': submission.payout,
           'win_loss': submission.win_loss,
           'subcategory': submission.subcategory.name
       })

   # Sort submissions by date
   all_submissions.sort(key=lambda x: x['date'], reverse=True)

   # Get user notifications
   try:
       unread_notifications_count = Notification.objects.filter(user=request.user, read=False).count()
   except:
       unread_notifications_count = 0

   context = {
       'total_sales': total_sales,
       'total_payout': total_payout,
       'total_win_loss': total_win_loss,
       'submission_distribution': submission_distribution,
       'all_submissions': all_submissions,
       'website': Website.objects.all(),
       'company_profiles': company_profiles,
       'submission_types': [
           ('all', 'All Types'),
           ('bookmaker', 'Bookmaker'),
           ('online_gaming', 'Online Gaming'),
           ('physical_casino', 'Physical Casino'),
           ('lottery', 'Lottery')
       ],
       'start_date': start_date.strftime("%Y-%m-%d") if start_date else "",
       'end_date': end_date.strftime("%Y-%m-%d") if end_date else "",
       'selected_type': submission_type,
       'selected_company': company_name,
       'username': request.user.username,
       'email': request.user.email,
       'unread_notifications_count': unread_notifications_count
   }

   # Get profile picture if exists
   try:
       profile_picture = ProfilePicture.objects.get(user=request.user)
       if profile_picture.image and profile_picture.image.name:
           context['profile_picture'] = profile_picture
   except ProfilePicture.DoesNotExist:
       pass

   return render(request, 'account/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin_user)
def generate_admin_pdf_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    category_id = request.GET.get('category')  # Business Category

    # Parse dates
    start_date = make_aware(datetime.strptime(start_date_str, "%Y-%m-%d"))
    end_date = make_aware(datetime.strptime(end_date_str, "%Y-%m-%d"))

    # Fetch data based on category and date range
    if category_id:
        category = BusinessCategory.objects.get(id=category_id)
        submissions = {
            'bookmaker': BookmakerSubmission.objects.filter(category=category, date__range=[start_date, end_date]),
            'online_gaming': OnlineGamingSubmission.objects.filter(category=category, date__range=[start_date, end_date]),
            'physical_casino': PhysicalCasinoSubmission.objects.filter(category=category, date__range=[start_date, end_date]),
            'lottery': LotterySubmission.objects.filter(category=category, date__range=[start_date, end_date]),
        }
    else:
        submissions = {
            'bookmaker': BookmakerSubmission.objects.filter(date__range=[start_date, end_date]),
            'online_gaming': OnlineGamingSubmission.objects.filter(date__range=[start_date, end_date]),
            'physical_casino': PhysicalCasinoSubmission.objects.filter(date__range=[start_date, end_date]),
            'lottery': LotterySubmission.objects.filter(date__range=[start_date, end_date]),
        }

    # Calculate totals for each category
    total_sales = sum([entry.sales for entry in submissions['bookmaker']]) + sum([entry.total_sales for entry in submissions['online_gaming']]) + sum([entry.sales for entry in submissions['lottery']])
    total_payout = sum([entry.payout for entry in submissions['bookmaker']]) + sum([entry.total_payout for entry in submissions['online_gaming']]) + sum([entry.payout for entry in submissions['lottery']])
    total_win_loss = sum([entry.win_loss for entry in submissions['bookmaker']]) + sum([entry.win_loss for entry in submissions['lottery']])
    

    # Create the PDF report
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add Title
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Admin Report - Summary of Returns", styles['Title']))
    elements.append(Paragraph(f"Date Range: {start_date_str} to {end_date_str}", styles['Normal']))

    # Add Totals Table
    totals_data = [
        ["Total Sales", total_sales],
        ["Total Payout", total_payout],
        ["Total Win/Loss", total_win_loss],
        
    ]

    totals_table = Table(totals_data)
    totals_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                      ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                      ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                      ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                      ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(totals_table)

    # No charts are created or added now, so skip this section

    # Build PDF
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="admin_report.pdf"'
    return response