from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.emails import send_checkin_reminder, send_review_reminder
from bookings.models import Booking, Review


class Command(BaseCommand):
    help = 'Send check-in reminders (1 day before) and review reminders (after checkout)'

    def handle(self, *args, **options):
        now = timezone.now()
        tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow_start + timedelta(days=1)
        yesterday_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = yesterday_end - timedelta(days=1)

        # Check-in reminders: confirmed bookings with check-in tomorrow
        checkin_bookings = Booking.objects.filter(
            status='confirmed',
            check_in__gte=tomorrow_start,
            check_in__lt=tomorrow_end,
            reminder_sent=False,
        ).select_related('user', 'accommodation')

        checkin_count = 0
        for booking in checkin_bookings:
            if send_checkin_reminder(booking):
                booking.reminder_sent = True
                booking.save(update_fields=['reminder_sent'])
                checkin_count += 1

        self.stdout.write(f'Check-in reminders sent: {checkin_count}')

        # Review reminders: confirmed bookings with checkout yesterday, no review yet
        review_bookings = Booking.objects.filter(
            status='confirmed',
            check_out__gte=yesterday_start,
            check_out__lt=yesterday_end,
            review_reminder_sent=False,
        ).select_related('user', 'accommodation')

        review_count = 0
        for booking in review_bookings:
            if Review.objects.filter(booking=booking).exists():
                continue
            if send_review_reminder(booking):
                booking.review_reminder_sent = True
                booking.save(update_fields=['review_reminder_sent'])
                review_count += 1

        self.stdout.write(f'Review reminders sent: {review_count}')
        self.stdout.write(self.style.SUCCESS('Done.'))
