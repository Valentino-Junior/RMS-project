from django.db import models
from django.contrib.auth.models import User


# Model for GroupUsers (manages users in groups)
class GroupUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"User: {self.user.username}"

    class Meta:
        verbose_name_plural = "Group Users"


# Section 1: Basic information with title, description, and image
class Section1(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    button = models.TextField()
    icon = models.CharField(max_length=255, default="mbri-right")
    image = models.ImageField(upload_to='images', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Section 1"


# Section 10: Contact information with phone, email, address, and working hours
class Section10(models.Model):
    title = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    working_hours = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Section 10"


# Section 11: Company links and social media with footer text
class Section11(models.Model):
    company_link_title = models.CharField(max_length=255)
    company_link = models.URLField()
    company_text = models.CharField(max_length=255, default="")
    features_title = models.CharField(max_length=255)
    features_link = models.URLField()
    features_text = models.CharField(max_length=255, default="")
    support_title = models.CharField(max_length=255)
    support_link = models.URLField()
    support_text = models.CharField(max_length=255, default="")
    about_title = models.CharField(max_length=255)
    about_link = models.URLField()
    about_text = models.CharField(max_length=255, default="")
    button1_text = models.CharField(max_length=255)
    button1_icon = models.CharField(max_length=255)
    button1_link = models.URLField(max_length=255, default="")
    button2_text = models.CharField(max_length=255)
    button2_icon = models.CharField(max_length=255)
    button2_link = models.URLField(max_length=255, default="")
    facebook_social_media_links = models.CharField(max_length=255, default="")
    twitter_social_media_links = models.CharField(max_length=255, default="")
    instagram_social_media_links = models.CharField(max_length=255, default="")
    linkedin_social_media_links = models.CharField(max_length=255, default="")
    footer_text = models.TextField()

    def __str__(self):
        return self.company_link_title

    class Meta:
        verbose_name_plural = "Section 11"


# Section 13:
class Section13(models.Model):
    name = models.CharField(max_length=255)  # Title field renamed to name
    google_map = models.TextField()  # Field for storing Google Map data

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Location"


class Subscription(models.Model):
    email = models.EmailField(unique=True)  # Email field for the subscriber
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return self.email


class Messages(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.name


class Website(models.Model):
    image = models.ImageField(upload_to='images', null=True, blank=True)
    website_title = models.CharField(max_length=200)
    menu1 = models.CharField(max_length=100)
    menu2 = models.CharField(max_length=100)
    menu3 = models.CharField(max_length=100)
    menu4 = models.CharField(max_length=100)
    button_text = models.CharField(max_length=100)
    button_link = models.URLField(null=True, blank=True)
    footer_image = models.ImageField(upload_to='images', null=True, blank=True)

    class Meta:
        verbose_name_plural = "NavBar"

    def __str__(self):
        return self.website_title


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.message[:20]}..."

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ProfilePicture(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
    updated_at = models.DateTimeField(auto_now=True)  # Track updates

    class Meta:
        verbose_name = "Profile Picture"
        verbose_name_plural = "Profile Pictures"

    def __str__(self):
        return f"{self.user.username}'s Profile Picture"


class ForgotPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)  # Token for the password reset
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Forgot Password"
        verbose_name_plural = "Forgot Password"

    def __str__(self):
        return f"Password reset request for {self.user.username}"


class Email(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"

    def __str__(self):
        return f"Email to {self.recipient} - Subject: {self.subject}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = "Phone Number"
        verbose_name_plural = "Phone Numbers"


# About model
class About(models.Model):
    title_mission = models.CharField(max_length=255)
    mission_description = models.TextField(null=False)
    title_vision = models.CharField(max_length=255)
    vision_description = models.TextField(null=False)
    title_terms = models.CharField(max_length=255)
    terms_description = models.TextField(null=False)
    title_privacy = models.CharField(max_length=255)
    privacy_description = models.TextField(null=False)
    button_text = models.CharField(max_length=255)
    button_icon = models.CharField(max_length=255)
    button_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title_mission or "About Page"

    class Meta:
        verbose_name_plural = "About"


# Business Category Model
class BusinessCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name  # Display the category name

    class Meta:
        verbose_name_plural = "Business Category"

# Business Subcategory Model
class BusinessSubCategory(models.Model):
    category = models.ForeignKey(BusinessCategory, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name  # Display the subcategory name

    class Meta:
        verbose_name_plural = "Business SubCategory"

# Company Profile Model
class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    company_email = models.EmailField()
    company_phone = models.CharField(max_length=20)
    company_address = models.TextField()

    # Many-to-many relationship with BusinessCategory
    business_categories = models.ManyToManyField(BusinessCategory, blank=True)

    # Many-to-many relationship with BusinessSubCategory
    business_subcategories = models.ManyToManyField(BusinessSubCategory, blank=True)

    def __str__(self):
        return self.company_name  # Display company name

    class Meta:
        verbose_name_plural = "Company Profile"

class BookmakerSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(BusinessSubCategory, on_delete=models.CASCADE)
    date = models.DateField()
    sales = models.DecimalField(max_digits=10, decimal_places=2)
    payout = models.DecimalField(max_digits=10, decimal_places=2)
    win_loss = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bookmaker Form - {self.user.username} - {self.date}"

class OnlineGamingSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(BusinessSubCategory, on_delete=models.CASCADE)
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_payout = models.DecimalField(max_digits=10, decimal_places=2)
    ggr = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Online Gaming Form - {self.user.username} - {self.date}"

class PhysicalCasinoSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('BusinessCategory', on_delete=models.CASCADE)
    subcategory = models.ForeignKey('BusinessSubCategory', on_delete=models.CASCADE)
    date = models.DateField()
    amount_totals = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Physical Casino Form - {self.user.username} - {self.date}"

class LotterySubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(BusinessSubCategory, on_delete=models.CASCADE)
    sales = models.DecimalField(max_digits=10, decimal_places=2)
    payout = models.DecimalField(max_digits=10, decimal_places=2)
    win_loss = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()  # Add date field to store the date

    def __str__(self):
        return f"Lottery Form - {self.user.username} - {self.date}"