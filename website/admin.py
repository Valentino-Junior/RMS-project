from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from import_export.admin import ExportMixin
from import_export.formats.base_formats import CSV

from .models import (
    GroupUsers, Section1, Section10, Section11,
    Subscription, Messages, Website, Notification, ProfilePicture, ForgotPassword, Email, Profile, Section13,
    About, BusinessCategory, BusinessSubCategory, CompanyProfile, BookmakerSubmission, OnlineGamingSubmission,
    PhysicalCasinoSubmission, LotterySubmission
)

# Define Admins for BookmakerSubmission, OnlineGamingSubmission, PhysicalCasinoSubmission, and LotterySubmission with Export
class BookmakerSubmissionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'category', 'subcategory', 'date', 'sales', 'payout', 'win_loss')
    search_fields = ('user__username', 'category__name', 'subcategory__name')
    list_filter = ('category', 'subcategory', 'date')
    list_per_page = 25
    ordering = ['date']  # Enable date sorting

    def get_export_formats(self):
        return [CSV]

class OnlineGamingSubmissionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'category', 'subcategory', 'date', 'total_sales', 'total_payout', 'ggr')
    search_fields = ('user__username', 'category__name', 'subcategory__name')
    list_filter = ('category', 'subcategory', 'date')
    list_per_page = 25
    ordering = ['date']  # Enable date sorting

    def get_export_formats(self):
        return [CSV]

class PhysicalCasinoSubmissionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'category', 'subcategory', 'date', 'amount_totals')
    search_fields = ('user__username', 'category__name', 'subcategory__name')
    list_filter = ('category', 'subcategory', 'date')
    list_per_page = 25
    ordering = ['date']  # Enable date sorting

    def get_export_formats(self):
        return [CSV]

class LotterySubmissionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'category', 'subcategory', 'sales', 'payout', 'win_loss', 'date')
    search_fields = ('user__username', 'category__name', 'subcategory__name')
    list_filter = ('category', 'subcategory', 'date')
    list_per_page = 25
    ordering = ['date']  # Enable date sorting

    def get_export_formats(self):
        return [CSV]

# Your existing model admins with ExportMixin added
class GroupUsersAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class Section1Admin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'description')
    search_fields = ('title', 'description')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class Section10Admin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'phone', 'email')
    search_fields = ('title', 'phone', 'email')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class Section11Admin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'company_link_title', 'company_link', 'footer_text')
    search_fields = ('company_link_title', 'company_link', 'footer_text')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class SubscriptionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class MessagesAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'message', 'phone')
    search_fields = ('name', 'email', 'message')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class WebsiteAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('website_title', 'menu1', 'menu2', 'menu3', 'menu4', 'button_text')
    search_fields = ('website_title', 'menu1', 'menu2', 'menu3')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class NotificationAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'title', 'message', 'created_at', 'read')
    search_fields = ('user__username', 'title', 'message')
    list_filter = ('read', 'created_at')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class ProfilePictureAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'image')
    search_fields = ('user__username',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class ForgotPasswordAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    list_filter = ('created_at',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class EmailAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('recipient', 'subject', 'sent_at', 'is_read', 'is_sent')
    search_fields = ('recipient', 'subject', 'body')
    list_filter = ('is_read', 'is_sent', 'sent_at')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class ProfileAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class Section13Admin(ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'google_map')
    search_fields = ('name',)
    list_filter = ('name',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class AboutAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'title_mission',
        'title_vision',
        'title_terms',
        'title_privacy',
        'button_text',
        'button_link',
    )
    search_fields = ('title_mission', 'title_vision', 'title_terms', 'title_privacy')
    list_filter = ('title_mission', 'title_vision', 'title_terms', 'title_privacy')
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class BusinessCategoryAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class BusinessSubCategoryAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'category', 'name')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

class CompanyProfileAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('user', 'company_name', 'license_number', 'company_email')
    search_fields = ('user__username', 'company_name', 'license_number', 'company_email')
    list_filter = ('business_categories',)
    list_per_page = 25

    def get_export_formats(self):
        return [CSV]

# Register your models and their admins with export functionality
admin.site = AdminSite()
admin.site.register(BusinessCategory, BusinessCategoryAdmin)
admin.site.register(BusinessSubCategory, BusinessSubCategoryAdmin)
admin.site.register(CompanyProfile, CompanyProfileAdmin)
admin.site.register(GroupUsers, GroupUsersAdmin)
admin.site.register(Section1, Section1Admin)
admin.site.register(Section10, Section10Admin)
admin.site.register(Section11, Section11Admin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(ProfilePicture, ProfilePictureAdmin)
admin.site.register(ForgotPassword, ForgotPasswordAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Section13, Section13Admin)
admin.site.register(About, AboutAdmin)
admin.site.register(BookmakerSubmission, BookmakerSubmissionAdmin)
admin.site.register(OnlineGamingSubmission, OnlineGamingSubmissionAdmin)
admin.site.register(PhysicalCasinoSubmission, PhysicalCasinoSubmissionAdmin)
admin.site.register(LotterySubmission, LotterySubmissionAdmin)