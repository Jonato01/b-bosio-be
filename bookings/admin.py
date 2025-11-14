from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Role, Accommodation, Booking, BookingGuest,
    BlockedPeriod, BlockedWeekday, BookingAudit
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'email', 'display_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'display_name']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'password_hash')}),
        ('Personal info', {'fields': ('display_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug', 'title', 'created_at']
    search_fields = ['title', 'slug', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'accommodation', 'user', 'check_in', 'check_out', 'num_guests', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'check_in']
    search_fields = ['accommodation__title', 'user__email', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'check_in'


@admin.register(BookingGuest)
class BookingGuestAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'full_name', 'email', 'phone', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'document_number']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BlockedPeriod)
class BlockedPeriodAdmin(admin.ModelAdmin):
    list_display = ['id', 'accommodation', 'start_date', 'end_date', 'reason', 'created_by']
    list_filter = ['accommodation', 'start_date']
    search_fields = ['accommodation__title', 'reason']
    readonly_fields = ['created_at']


@admin.register(BlockedWeekday)
class BlockedWeekdayAdmin(admin.ModelAdmin):
    list_display = ['id', 'accommodation', 'weekday', 'start_time', 'end_time', 'reason']
    list_filter = ['accommodation', 'weekday']
    search_fields = ['accommodation__title', 'reason']
    readonly_fields = ['created_at']


@admin.register(BookingAudit)
class BookingAuditAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'action', 'actor_user', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['booking__id', 'actor_user__email']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

