from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class Role(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = 'roles'
        managed = False

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255, db_column='password_hash')
    display_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, db_column='role_id', default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Required for admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        managed = False
        indexes = [
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['role'], name='idx_users_role'),
        ]

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt', 'argon2')):
            self.password_hash = self.password
        super().save(*args, **kwargs)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value):
        self.password_hash = value

    def __str__(self):
        return self.email


class Accommodation(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accommodations'
        managed = False

    def __str__(self):
        return self.title


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    id = models.BigAutoField(primary_key=True)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.PROTECT, db_column='accommodation_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='user_id')
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    num_guests = models.SmallIntegerField(default=1, db_column='guests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'bookings'
        managed = False
        indexes = [
            models.Index(fields=['accommodation', 'check_in', 'check_out'], name='idx_bookings_accom_dates'),
            models.Index(fields=['status'], name='idx_bookings_status'),
            models.Index(fields=['user'], name='idx_bookings_user'),
        ]

    def __str__(self):
        return f"Booking {self.id} - {self.accommodation.title}"


class BookingGuest(models.Model):
    id = models.BigAutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='guests', db_column='booking_id')
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    document_type = models.CharField(max_length=50, null=True, blank=True)
    document_number = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'booking_guests'
        managed = False
        indexes = [
            models.Index(fields=['booking'], name='idx_booking_guests_booking'),
        ]

    def __str__(self):
        return f"{self.full_name} - Booking {self.booking.id}"


class BlockedPeriod(models.Model):
    id = models.BigAutoField(primary_key=True)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, db_column='accommodation_id')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='created_by')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'blocked_periods'
        managed = False
        indexes = [
            models.Index(fields=['accommodation', 'start_date', 'end_date'], name='idx_blocked_accom_dates'),
            models.Index(fields=['created_by'], name='idx_blocked_period_creator'),
        ]

    def __str__(self):
        return f"Blocked: {self.accommodation.title} ({self.start_date} - {self.end_date})"


class BlockedWeekday(models.Model):
    id = models.AutoField(primary_key=True)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, db_column='accommodation_id')
    weekday = models.SmallIntegerField()  # 0=Monday, 6=Sunday
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='created_by')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'blocked_weekdays'
        managed = False
        indexes = [
            models.Index(fields=['accommodation', 'weekday'], name='idx_blocked_weekdays_accom'),
            models.Index(fields=['created_by'], name='idx_blocked_weekday_creator'),
        ]

    def __str__(self):
        return f"Blocked weekday {self.weekday}: {self.accommodation.title}"


class BookingAudit(models.Model):
    id = models.BigAutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, db_column='booking_id')
    action = models.CharField(max_length=64)
    actor_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='actor_user_id')
    data_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'booking_audit'
        managed = False
        indexes = [
            models.Index(fields=['booking'], name='idx_audit_booking'),
            models.Index(fields=['actor_user'], name='idx_audit_actor'),
        ]

    def __str__(self):
        return f"Audit: {self.action} - Booking {self.booking.id if self.booking else 'N/A'}"
