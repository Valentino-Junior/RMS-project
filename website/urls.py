from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from website.views import send_email_view, secure_email_read, trigger_error
from website import views  # Import once for all views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, generate_pdf

# Assign custom error handlers
handler403 = views.forbidden
handler404 = views.error
handler500 = views.server_error

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('account/signup/', views.signup, name='signup'),
    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),
    path('account/signin/', views.signin, name='signin'),
    path('account/forgot/', views.forgot, name='forgot'),
    path('account/dashboard/', views.dashboard, name='dashboard'),
    path('account/profile/', views.profile_view, name='profile'),
    path('account/notification/', views.notifications, name='notification'),
    path('signout/', views.signout, name='signout'),
    path('sentry-debug/', trigger_error),
    path('send-email/', send_email_view, name='send_email'),
    path('account/activate/<uidb64>/<token>/', views.activate, name='activate_account'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('account/admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-generate-pdf/', views.generate_admin_pdf_report, name='generate_admin_pdf_report'),
    # Email tracking URL
    path('secure-email-read/<int:email_id>/', secure_email_read, name='secure_email_read'),
    # Password reset URLs
    path('account/password_reset/', auth_views.PasswordResetView.as_view(template_name='account/forgot.html'), name='password_reset'),
    path('account/password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)