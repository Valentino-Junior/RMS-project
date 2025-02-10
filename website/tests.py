import smtplib

try:
    with smtplib.SMTP('mail.kncmap.com', 587) as server:
        server.set_debuglevel(1)  # Enable debug output
        server.starttls()
        server.login('notification@kncmap.com', 'CHARLES13a.')
        server.sendmail('notification@kncmap.com', 'support@kncmap.com', 'Subject: Test\n\nThis is a test email.')
        print("Email sent successfully")
except Exception as e:
    print(f"Error sending email: {e}")