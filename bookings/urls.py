from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RoleViewSet, AccommodationViewSet,
    BookingViewSet, BookingGuestViewSet, BlockedPeriodViewSet,
    BlockedWeekdayViewSet, BookingAuditViewSet,
    check_availability, booking_statistics
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'accommodations', AccommodationViewSet, basename='accommodation')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'booking-guests', BookingGuestViewSet, basename='booking-guest')
router.register(r'blocked-periods', BlockedPeriodViewSet, basename='blocked-period')
router.register(r'blocked-weekdays', BlockedWeekdayViewSet, basename='blocked-weekday')
router.register(r'booking-audit', BookingAuditViewSet, basename='booking-audit')

urlpatterns = [
    path('', include(router.urls)),
    path('check-availability/', check_availability, name='check-availability'),
    path('statistics/', booking_statistics, name='statistics'),
]

