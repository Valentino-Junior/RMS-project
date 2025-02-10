from datetime import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Email
from django.urls import reverse

class EmailService:
    @staticmethod
    def send_email(recipient, subject, body):
        # Create and save the email instance
        email = Email(recipient=recipient, subject=subject, body=body)
        email.save()

        # Generate a unique tracking URL
        tracking_url = reverse('secure_email_read', args=[email.id])
        tracking_pixel = f'''
    Dear {recipient},

    We hope this message finds you well. To ensure the security and confidentiality of your information, we have provided a secure link for you to read your email. Please click the link below to access your email securely:

    <a href="{settings.SITE_URL}{tracking_url}">Read your email securely</a>

    Thank you for your attention. If you have any questions, feel free to reach out.

    Best regards,
    The Team
    '''

        # Include the tracking pixel in the email body
        email_body_with_tracking = f"{tracking_pixel}"

        # Send the email using Django's email framework
        send_mail(
            subject,
            email_body_with_tracking,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )

        return email

    @staticmethod
    def mark_as_read(email_id):
        try:
            email = Email.objects.get(id=email_id)
            email.is_read = True
            email.read_at = timezone.now()
            email.save()
            return True
        except Email.DoesNotExist:
            return False