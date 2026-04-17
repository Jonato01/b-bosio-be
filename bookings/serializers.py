from rest_framework import serializers
from .models import (
    User, Role, Accommodation, Booking, BookingGuest,
    BlockedPeriod, BlockedWeekday, BookingAudit,
    PaidService, Photo, Review
)
from django.db.models import Avg
from django.contrib.auth.hashers import make_password


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'display_name', 'role', 'role_name',
                  'created_at', 'updated_at', 'password']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.password_hash = make_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password_hash = make_password(password)
        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'display_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.password_hash = make_password(password)
        user.save()
        return user


class PaidServiceSerializer(serializers.ModelSerializer):
    accommodation_title = serializers.CharField(source='accommodation.title', read_only=True)

    class Meta:
        model = PaidService
        fields = ['id', 'accommodation', 'accommodation_title', 'name',
                  'description', 'price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PhotoSerializer(serializers.ModelSerializer):
    accommodation_title = serializers.CharField(source='accommodation.title', read_only=True)
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True, default=None)

    class Meta:
        model = Photo
        fields = ['id', 'accommodation', 'accommodation_title', 'uploaded_by',
                  'uploaded_by_email', 'url', 'upload_type', 'caption', 'created_at']
        read_only_fields = ['id', 'url', 'uploaded_by', 'created_at']


class PhotoUploadSerializer(serializers.Serializer):
    accommodation = serializers.IntegerField()
    upload_type = serializers.ChoiceField(choices=['accommodation', 'review'], default='accommodation')
    caption = serializers.CharField(max_length=255, required=False, allow_blank=True)
    file = serializers.ImageField()


class AccommodationSerializer(serializers.ModelSerializer):
    paid_services = PaidServiceSerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = ['id', 'slug', 'title', 'description', 'created_at', 'updated_at',
                  'paid_services', 'photos', 'average_rating', 'review_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_average_rating(self, obj):
        result = Review.objects.filter(accommodation=obj).aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else None

    def get_review_count(self, obj):
        return Review.objects.filter(accommodation=obj).count()


class BookingGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingGuest
        fields = ['id', 'booking', 'full_name', 'email', 'phone', 'birth_date',
                  'document_type', 'document_number', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'booking', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    accommodation_title = serializers.CharField(source='accommodation.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    guests_details = BookingGuestSerializer(source='guests', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'accommodation', 'accommodation_title', 'user', 'user_email',
                  'check_in', 'check_out', 'num_guests', 'status', 'notes',
                  'selected_services', 'created_at', 'updated_at', 'guests_details']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        if attrs['check_out'] <= attrs['check_in']:
            raise serializers.ValidationError("Check-out must be after check-in")

        # Check for overlapping bookings
        accommodation = attrs['accommodation']
        check_in = attrs['check_in']
        check_out = attrs['check_out']

        overlapping = Booking.objects.filter(
            accommodation=accommodation,
            status__in=['pending', 'confirmed']
        ).filter(
            check_in__lt=check_out,
            check_out__gt=check_in
        )

        # Exclude current booking if updating
        if self.instance:
            overlapping = overlapping.exclude(id=self.instance.id)

        if overlapping.exists():
            raise serializers.ValidationError("This period overlaps with an existing booking")

        # Check for blocked periods
        blocked_periods = BlockedPeriod.objects.filter(
            accommodation=accommodation,
            start_date__lt=check_out,
            end_date__gt=check_in
        )

        if blocked_periods.exists():
            raise serializers.ValidationError("This period is blocked for bookings")

        return attrs


class BookingCreateSerializer(serializers.ModelSerializer):
    guests_data = BookingGuestSerializer(many=True, required=False)

    class Meta:
        model = Booking
        fields = ['accommodation', 'user', 'check_in', 'check_out',
                  'num_guests', 'notes', 'selected_services', 'guests_data']

    def validate(self, attrs):
        if attrs['check_out'] <= attrs['check_in']:
            raise serializers.ValidationError("Check-out must be after check-in")

        # Check for overlapping bookings
        accommodation = attrs['accommodation']
        check_in = attrs['check_in']
        check_out = attrs['check_out']

        overlapping = Booking.objects.filter(
            accommodation=accommodation,
            status__in=['pending', 'confirmed']
        ).filter(
            check_in__lt=check_out,
            check_out__gt=check_in
        )

        if overlapping.exists():
            raise serializers.ValidationError("This period overlaps with an existing booking")

        # Check for blocked periods
        blocked_periods = BlockedPeriod.objects.filter(
            accommodation=accommodation,
            start_date__lt=check_out,
            end_date__gt=check_in
        )

        if blocked_periods.exists():
            raise serializers.ValidationError("This period is blocked for bookings")

        return attrs

    def create(self, validated_data):
        guests_data = validated_data.pop('guests_data', [])
        booking = Booking.objects.create(**validated_data)

        # Create audit log
        BookingAudit.objects.create(
            booking=booking,
            action='created',
            actor_user=self.context.get('request').user if self.context.get('request') else None,
            data_json={'status': booking.status}
        )

        # Create guests
        for guest_data in guests_data:
            BookingGuest.objects.create(booking=booking, **guest_data)

        return booking


class BlockedPeriodSerializer(serializers.ModelSerializer):
    accommodation_title = serializers.CharField(source='accommodation.title', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = BlockedPeriod
        fields = ['id', 'accommodation', 'accommodation_title', 'start_date', 'end_date',
                  'reason', 'created_by', 'created_by_email', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        if attrs['end_date'] <= attrs['start_date']:
            raise serializers.ValidationError("End date must be after start date")
        return attrs


class BlockedWeekdaySerializer(serializers.ModelSerializer):
    accommodation_title = serializers.CharField(source='accommodation.title', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = BlockedWeekday
        fields = ['id', 'accommodation', 'accommodation_title', 'weekday',
                  'start_time', 'end_time', 'reason', 'created_by', 'created_by_email', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_weekday(self, value):
        if value < 0 or value > 6:
            raise serializers.ValidationError("Weekday must be between 0 (Monday) and 6 (Sunday)")
        return value


class BookingAuditSerializer(serializers.ModelSerializer):
    actor_user_email = serializers.CharField(source='actor_user.email', read_only=True)

    class Meta:
        model = BookingAudit
        fields = ['id', 'booking', 'action', 'actor_user', 'actor_user_email',
                  'data_json', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    accommodation_title = serializers.CharField(source='accommodation.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True, default=None)
    user_display_name = serializers.CharField(source='user.display_name', read_only=True, default=None)
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'accommodation', 'accommodation_title', 'booking',
                  'user', 'user_email', 'user_display_name', 'rating',
                  'comment', 'photos', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'accommodation', 'created_at', 'updated_at']

    def get_photos(self, obj):
        photos = Photo.objects.filter(
            accommodation=obj.accommodation,
            uploaded_by=obj.user,
            upload_type='review'
        )
        return PhotoSerializer(photos, many=True).data


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'rating', 'comment']

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Il voto deve essere tra 0 e 5")
        return value

    def validate_booking(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("Puoi recensire solo le tue prenotazioni")
        if value.status != 'confirmed':
            raise serializers.ValidationError("Solo prenotazioni confermate possono essere recensite")
        from django.utils import timezone
        if value.check_out > timezone.now():
            raise serializers.ValidationError("Puoi recensire solo dopo il check-out")
        if Review.objects.filter(booking=value).exists():
            raise serializers.ValidationError("Hai già recensito questa prenotazione")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['accommodation'] = validated_data['booking'].accommodation
        return super().create(validated_data)


class AvailabilityCheckSerializer(serializers.Serializer):
    accommodation_id = serializers.IntegerField()
    check_in = serializers.DateTimeField()
    check_out = serializers.DateTimeField()

    def validate(self, attrs):
        if attrs['check_out'] <= attrs['check_in']:
            raise serializers.ValidationError("Check-out must be after check-in")
        return attrs

