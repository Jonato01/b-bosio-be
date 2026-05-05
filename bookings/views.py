from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from datetime import datetime
from .models import (
    User, Role, Accommodation, Booking, BookingGuest,
    BlockedPeriod, BlockedWeekday, BookingAudit,
    PaidService, Photo, Review
)
from .serializers import (
    UserSerializer, RoleSerializer, AccommodationSerializer,
    BookingSerializer, BookingGuestSerializer, BlockedPeriodSerializer,
    BlockedWeekdaySerializer, BookingAuditSerializer, UserRegistrationSerializer,
    BookingCreateSerializer, AvailabilityCheckSerializer,
    PaidServiceSerializer, PhotoSerializer, PhotoUploadSerializer,
    ReviewSerializer, ReviewCreateSerializer,
    ConciergeRequestSerializer, TravelerQuizSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .emails import (
    send_new_booking_admin, send_booking_confirmed, send_booking_rejected,
    send_surprise_itinerary,
)
from . import ai


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_bookings(self, request):
        """Get all bookings for the current user"""
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def availability(self, request, slug=None):
        """Check availability for a specific accommodation"""
        accommodation = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')

        if not check_in or not check_out:
            return Response(
                {'error': 'check_in and check_out parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            check_in_dt = datetime.fromisoformat(check_in.replace('Z', '+00:00'))
            check_out_dt = datetime.fromisoformat(check_out.replace('Z', '+00:00'))
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use ISO format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            accommodation=accommodation,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out_dt,
            check_out__gt=check_in_dt
        )

        # Check for blocked periods
        blocked_periods = BlockedPeriod.objects.filter(
            accommodation=accommodation,
            start_date__lt=check_out_dt,
            end_date__gt=check_in_dt
        )

        is_available = not overlapping_bookings.exists() and not blocked_periods.exists()

        return Response({
            'available': is_available,
            'accommodation': AccommodationSerializer(accommodation).data,
            'conflicting_bookings': BookingSerializer(overlapping_bookings, many=True).data,
            'blocked_periods': BlockedPeriodSerializer(blocked_periods, many=True).data
        })

    @action(detail=True, methods=['get'])
    def bookings(self, request, slug=None):
        """Get all bookings for this accommodation"""
        accommodation = self.get_object()
        bookings = Booking.objects.filter(accommodation=accommodation).order_by('-check_in')

        # Filter by status if provided
        booking_status = request.query_params.get('status')
        if booking_status:
            bookings = bookings.filter(status=booking_status)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def blocked_periods(self, request, slug=None):
        """Get all blocked periods for this accommodation"""
        accommodation = self.get_object()
        blocked = BlockedPeriod.objects.filter(accommodation=accommodation).order_by('start_date')
        serializer = BlockedPeriodSerializer(blocked, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def calendar(self, request, slug=None):
        """Return unavailable dates for a given month range."""
        accommodation = self.get_object()
        month_str = request.query_params.get('month')  # e.g. "2026-04"

        if not month_str:
            from django.utils import timezone as tz
            now = tz.now()
            month_str = now.strftime('%Y-%m')

        try:
            year, month = int(month_str[:4]), int(month_str[5:7])
        except (ValueError, IndexError):
            return Response({'error': 'Invalid month format. Use YYYY-MM'}, status=status.HTTP_400_BAD_REQUEST)

        import calendar as cal_mod
        from datetime import datetime as dt, timedelta, timezone as dt_tz

        first_day = dt(year, month, 1, tzinfo=dt_tz.utc)
        last_day_num = cal_mod.monthrange(year, month)[1]
        # Include next month too for better UX
        if month == 12:
            end_range = dt(year + 1, 2, 1, tzinfo=dt_tz.utc)
        else:
            next_next = month + 2 if month + 2 <= 12 else (month + 2 - 12)
            next_next_year = year if month + 2 <= 12 else year + 1
            end_range = dt(next_next_year, next_next, 1, tzinfo=dt_tz.utc)

        # Get booked dates
        bookings = Booking.objects.filter(
            accommodation=accommodation,
            status__in=['pending', 'confirmed'],
            check_in__lt=end_range,
            check_out__gt=first_day
        )

        booked_dates = set()
        for b in bookings:
            d = max(b.check_in.date(), first_day.date())
            end_d = min(b.check_out.date(), end_range.date())
            while d < end_d:
                booked_dates.add(d.isoformat())
                d += timedelta(days=1)

        # Get blocked dates
        blocked_periods = BlockedPeriod.objects.filter(
            accommodation=accommodation,
            start_date__lt=end_range,
            end_date__gt=first_day
        )

        blocked_dates = set()
        for bp in blocked_periods:
            d = max(bp.start_date.date(), first_day.date())
            end_d = min(bp.end_date.date(), end_range.date())
            while d < end_d:
                blocked_dates.add(d.isoformat())
                d += timedelta(days=1)

        # Get blocked weekdays
        blocked_weekdays = BlockedWeekday.objects.filter(accommodation=accommodation)
        blocked_weekday_nums = set(bw.weekday for bw in blocked_weekdays)

        # Add blocked weekdays to blocked_dates
        d = first_day.date()
        while d < end_range.date():
            if d.weekday() in blocked_weekday_nums:
                blocked_dates.add(d.isoformat())
            d += timedelta(days=1)

        return Response({
            'booked_dates': sorted(booked_dates),
            'blocked_dates': sorted(blocked_dates),
        })

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        accommodation = self.get_object()
        reviews = Review.objects.filter(accommodation=accommodation).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        queryset = Booking.objects.all().order_by('-created_at')

        # Filter by user if not admin
        user = self.request.user
        if not user.is_staff and hasattr(user, 'role'):
            if user.role.name != 'admin':
                queryset = queryset.filter(user=user)

        # Filter by status
        booking_status = self.request.query_params.get('status')
        if booking_status:
            queryset = queryset.filter(status=booking_status)

        # Filter by accommodation
        accommodation_id = self.request.query_params.get('accommodation')
        if accommodation_id:
            queryset = queryset.filter(accommodation_id=accommodation_id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(check_in__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_out__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        booking = serializer.save()

        # Create audit log
        BookingAudit.objects.create(
            booking=booking,
            action='created',
            actor_user=self.request.user,
            data_json={'status': booking.status, 'accommodation_id': booking.accommodation.id}
        )

        send_new_booking_admin(booking)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        """Confirm a pending booking"""
        booking = self.get_object()

        if booking.status != 'pending':
            return Response(
                {'error': 'Only pending bookings can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'confirmed'
        booking.save()

        # Create audit log
        BookingAudit.objects.create(
            booking=booking,
            action='confirmed',
            actor_user=request.user,
            data_json={'previous_status': 'pending', 'new_status': 'confirmed'}
        )

        send_booking_confirmed(booking)

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()

        if booking.status in ['cancelled', 'rejected']:
            return Response(
                {'error': 'Booking is already cancelled or rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        previous_status = booking.status
        booking.status = 'cancelled'
        booking.save()

        # Create audit log
        BookingAudit.objects.create(
            booking=booking,
            action='cancelled',
            actor_user=request.user,
            data_json={'previous_status': previous_status, 'new_status': 'cancelled'}
        )

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Reject a pending booking"""
        booking = self.get_object()

        if booking.status != 'pending':
            return Response(
                {'error': 'Only pending bookings can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'rejected'
        booking.save()

        # Create audit log
        BookingAudit.objects.create(
            booking=booking,
            action='rejected',
            actor_user=request.user,
            data_json={'previous_status': 'pending', 'new_status': 'rejected'}
        )

        send_booking_rejected(booking)

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def guests(self, request, pk=None):
        """Get all guests for this booking"""
        booking = self.get_object()
        guests = BookingGuest.objects.filter(booking=booking)
        serializer = BookingGuestSerializer(guests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_guest(self, request, pk=None):
        """Add a guest to this booking"""
        booking = self.get_object()
        data = request.data.copy()
        data['booking'] = booking.id

        serializer = BookingGuestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def audit_log(self, request, pk=None):
        """Get audit log for this booking"""
        booking = self.get_object()
        audit_entries = BookingAudit.objects.filter(booking=booking).order_by('-created_at')
        serializer = BookingAuditSerializer(audit_entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='traveler-type',
            permission_classes=[IsAuthenticated])
    def traveler_type(self, request, pk=None):
        """Feature C: classifica ospite con AI persona alluminio-IKEA."""
        booking = self.get_object()
        serializer = TravelerQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = ai.traveler_type(serializer.validated_data['answers'])
        if not result:
            return Response(
                {'error': 'AI non disponibile'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        BookingAudit.objects.create(
            booking=booking,
            action='traveler_quiz',
            actor_user=request.user if request.user.is_authenticated else None,
            data_json=result,
        )
        return Response(result)

    @action(detail=True, methods=['post'], url_path='surprise-itinerary',
            permission_classes=[IsAuthenticated])
    def surprise_itinerary(self, request, pk=None):
        """Feature D: itinerario sorpresa AI. Opzionale send_email=true."""
        booking = self.get_object()
        html = ai.surprise_itinerary(booking)
        if not html:
            return Response(
                {'error': 'AI non disponibile'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        BookingAudit.objects.create(
            booking=booking,
            action='surprise_itinerary',
            actor_user=request.user if request.user.is_authenticated else None,
            data_json={'html': html},
        )
        send_email = str(request.query_params.get('send_email', '')).lower() == 'true'
        emailed = False
        if send_email:
            emailed = bool(send_surprise_itinerary(booking, html))
        return Response({'html': html, 'emailed': emailed})


class ConciergeRateThrottle(AnonRateThrottle):
    """Throttle dedicato all'endpoint concierge. Rate da settings DEFAULT_THROTTLE_RATES['concierge']."""
    scope = 'concierge'


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([ConciergeRateThrottle])
def concierge_chat(request):
    """Feature B: concierge AI pubblico (throttled 10/min/IP)."""
    serializer = ConciergeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    reply = ai.concierge_reply(
        serializer.validated_data['question'],
        serializer.validated_data.get('history') or None,
    )
    if reply is None:
        return Response(
            {'error': 'AI non disponibile'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response({'reply': reply})


class BookingGuestViewSet(viewsets.ModelViewSet):
    queryset = BookingGuest.objects.all()
    serializer_class = BookingGuestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = BookingGuest.objects.all()
        booking_id = self.request.query_params.get('booking')
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        return queryset


class BlockedPeriodViewSet(viewsets.ModelViewSet):
    queryset = BlockedPeriod.objects.all()
    serializer_class = BlockedPeriodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = BlockedPeriod.objects.all().order_by('start_date')
        accommodation_id = self.request.query_params.get('accommodation')
        if accommodation_id:
            queryset = queryset.filter(accommodation_id=accommodation_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BlockedWeekdayViewSet(viewsets.ModelViewSet):
    queryset = BlockedWeekday.objects.all()
    serializer_class = BlockedWeekdaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = BlockedWeekday.objects.all()
        accommodation_id = self.request.query_params.get('accommodation')
        if accommodation_id:
            queryset = queryset.filter(accommodation_id=accommodation_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BookingAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookingAudit.objects.all()
    serializer_class = BookingAuditSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = BookingAudit.objects.all().order_by('-created_at')
        booking_id = self.request.query_params.get('booking')
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        return queryset


class PaidServiceViewSet(viewsets.ModelViewSet):
    queryset = PaidService.objects.all()
    serializer_class = PaidServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = PaidService.objects.all().order_by('accommodation', 'name')
        accommodation_id = self.request.query_params.get('accommodation')
        if accommodation_id:
            queryset = queryset.filter(accommodation_id=accommodation_id)
        return queryset


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Photo.objects.all().order_by('-created_at')
        accommodation_id = self.request.query_params.get('accommodation')
        upload_type = self.request.query_params.get('upload_type')
        if accommodation_id:
            queryset = queryset.filter(accommodation_id=accommodation_id)
        if upload_type:
            queryset = queryset.filter(upload_type=upload_type)
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload(self, request):
        serializer = PhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data['file']
        accommodation_id = serializer.validated_data['accommodation']
        upload_type = serializer.validated_data.get('upload_type', 'accommodation')
        caption = serializer.validated_data.get('caption', '')

        if upload_type == 'accommodation':
            if not (request.user.is_staff or
                    (hasattr(request.user, 'role') and request.user.role.name == 'admin')):
                return Response(
                    {'error': 'Solo gli admin possono caricare foto per gli alloggi'},
                    status=status.HTTP_403_FORBIDDEN
                )

        try:
            accommodation = Accommodation.objects.get(id=accommodation_id)
        except Accommodation.DoesNotExist:
            return Response({'error': 'Alloggio non trovato'}, status=status.HTTP_404_NOT_FOUND)

        from .storage import upload_to_supabase
        folder = f"{accommodation.slug}/{upload_type}"
        public_url = upload_to_supabase(file_obj, folder=folder)

        photo = Photo.objects.create(
            accommodation=accommodation,
            uploaded_by=request.user,
            url=public_url,
            upload_type=upload_type,
            caption=caption
        )

        return Response(PhotoSerializer(photo).data, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all().order_by('-created_at')
        accommodation_id = self.request.query_params.get('accommodation')
        if accommodation_id:
            queryset = queryset.filter(accommodation_id=accommodation_id)
        return queryset


@api_view(['POST'])
@permission_classes([AllowAny])
def check_availability(request):
    """Check availability for a booking"""
    serializer = AvailabilityCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    accommodation_id = serializer.validated_data['accommodation_id']
    check_in = serializer.validated_data['check_in']
    check_out = serializer.validated_data['check_out']

    try:
        accommodation = Accommodation.objects.get(id=accommodation_id)
    except Accommodation.DoesNotExist:
        return Response(
            {'error': 'Accommodation not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check for overlapping bookings
    overlapping_bookings = Booking.objects.filter(
        accommodation_id=accommodation_id,
        status__in=['pending', 'confirmed'],
        check_in__lt=check_out,
        check_out__gt=check_in
    )

    # Check for blocked periods
    blocked_periods = BlockedPeriod.objects.filter(
        accommodation_id=accommodation_id,
        start_date__lt=check_out,
        end_date__gt=check_in
    )

    is_available = not overlapping_bookings.exists() and not blocked_periods.exists()

    return Response({
        'available': is_available,
        'accommodation': AccommodationSerializer(accommodation).data,
        'check_in': check_in,
        'check_out': check_out,
        'conflicting_bookings_count': overlapping_bookings.count(),
        'blocked_periods_count': blocked_periods.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def booking_statistics(request):
    """Get booking statistics"""
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    rejected_bookings = Booking.objects.filter(status='rejected').count()

    return Response({
        'total_bookings': total_bookings,
        'pending': pending_bookings,
        'confirmed': confirmed_bookings,
        'cancelled': cancelled_bookings,
        'rejected': rejected_bookings,
        'total_accommodations': Accommodation.objects.count(),
        'total_users': User.objects.count()
    })

