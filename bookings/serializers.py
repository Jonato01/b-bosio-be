from rest_framework import serializers
from .models import (
    User, Role, Accommodation, Booking, BookingGuest,
    BlockedPeriod, BlockedWeekday, BookingAudit
)
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


class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ['id', 'slug', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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
                  'created_at', 'updated_at', 'guests_details']
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
                  'num_guests', 'notes', 'guests_data']

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


class AvailabilityCheckSerializer(serializers.Serializer):
    accommodation_id = serializers.IntegerField()
    check_in = serializers.DateTimeField()
    check_out = serializers.DateTimeField()

    def validate(self, attrs):
        if attrs['check_out'] <= attrs['check_in']:
            raise serializers.ValidationError("Check-out must be after check-in")
        return attrs

