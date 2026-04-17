import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _format_date(dt):
    """Format datetime to Italian locale string."""
    if dt is None:
        return ''
    return dt.strftime('%d/%m/%Y %H:%M')


def _send(subject, html_message, recipient_list):
    """Send email with error handling."""
    if not settings.EMAIL_HOST_USER:
        logger.warning('EMAIL_HOST_USER not configured, skipping email: %s', subject)
        return False
    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info('Email sent: %s to %s', subject, recipient_list)
        return True
    except Exception:
        logger.exception('Failed to send email: %s', subject)
        return False


def send_new_booking_admin(booking):
    """Notify admin about a new booking."""
    admin_email = settings.ADMIN_EMAIL
    if not admin_email:
        return False

    frontend_url = settings.FRONTEND_URL
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1e1e1e; color: #e0e0e0; padding: 24px; border-radius: 8px;">
        <h2 style="color: #80cbc4; margin-top: 0;">Nuova Prenotazione</h2>
        <p>È stata creata una nuova prenotazione che richiede la tua approvazione.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 8px 0; color: #999;">Alloggio:</td><td style="padding: 8px 0;"><strong>{booking.accommodation.title}</strong></td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Cliente:</td><td style="padding: 8px 0;">{booking.user.email if booking.user else 'N/A'}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-in:</td><td style="padding: 8px 0;">{_format_date(booking.check_in)}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-out:</td><td style="padding: 8px 0;">{_format_date(booking.check_out)}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Ospiti:</td><td style="padding: 8px 0;">{booking.num_guests}</td></tr>
        </table>
        <a href="{frontend_url}/admin" style="display: inline-block; padding: 12px 24px; background: #80cbc4; color: #121212; text-decoration: none; border-radius: 4px; font-weight: bold;">Vai alla Dashboard</a>
    </div>
    """
    return _send(
        f'Nuova prenotazione: {booking.accommodation.title}',
        html,
        [admin_email],
    )


def send_booking_confirmed(booking):
    """Notify customer that booking is confirmed."""
    if not booking.user or not booking.user.email:
        return False

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1e1e1e; color: #e0e0e0; padding: 24px; border-radius: 8px;">
        <h2 style="color: #80cbc4; margin-top: 0;">Prenotazione Confermata ✓</h2>
        <p>La tua prenotazione è stata confermata!</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 8px 0; color: #999;">Alloggio:</td><td style="padding: 8px 0;"><strong>{booking.accommodation.title}</strong></td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-in:</td><td style="padding: 8px 0;">{_format_date(booking.check_in)}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-out:</td><td style="padding: 8px 0;">{_format_date(booking.check_out)}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Ospiti:</td><td style="padding: 8px 0;">{booking.num_guests}</td></tr>
        </table>
        <p style="color: #999; font-size: 14px;">Ti aspettiamo! Se hai domande, contattaci.</p>
    </div>
    """
    return _send(
        f'Prenotazione confermata: {booking.accommodation.title}',
        html,
        [booking.user.email],
    )


def send_booking_rejected(booking):
    """Notify customer that booking was rejected."""
    if not booking.user or not booking.user.email:
        return False

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1e1e1e; color: #e0e0e0; padding: 24px; border-radius: 8px;">
        <h2 style="color: #ef9a9a; margin-top: 0;">Prenotazione Non Approvata</h2>
        <p>Siamo spiacenti, la tua prenotazione non è stata approvata.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 8px 0; color: #999;">Alloggio:</td><td style="padding: 8px 0;"><strong>{booking.accommodation.title}</strong></td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-in:</td><td style="padding: 8px 0;">{_format_date(booking.check_in)}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-out:</td><td style="padding: 8px 0;">{_format_date(booking.check_out)}</td></tr>
        </table>
        <p style="color: #999; font-size: 14px;">Ti invitiamo a provare con date diverse o contattarci per maggiori informazioni.</p>
    </div>
    """
    return _send(
        f'Prenotazione non approvata: {booking.accommodation.title}',
        html,
        [booking.user.email],
    )


def send_checkin_reminder(booking):
    """Remind customer about upcoming check-in (1 day before)."""
    if not booking.user or not booking.user.email:
        return False

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1e1e1e; color: #e0e0e0; padding: 24px; border-radius: 8px;">
        <h2 style="color: #80cbc4; margin-top: 0;">Promemoria Check-in Domani!</h2>
        <p>Ti ricordiamo che il tuo check-in è previsto per domani.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 8px 0; color: #999;">Alloggio:</td><td style="padding: 8px 0;"><strong>{booking.accommodation.title}</strong></td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-in:</td><td style="padding: 8px 0;">{_format_date(booking.check_in)}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Check-out:</td><td style="padding: 8px 0;">{_format_date(booking.check_out)}</td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Ospiti:</td><td style="padding: 8px 0;">{booking.num_guests}</td></tr>
        </table>
        <p style="color: #999; font-size: 14px;">Buon viaggio e a presto!</p>
    </div>
    """
    return _send(
        f'Promemoria: check-in domani a {booking.accommodation.title}',
        html,
        [booking.user.email],
    )


def send_review_reminder(booking):
    """Invite customer to leave a review after checkout."""
    if not booking.user or not booking.user.email:
        return False

    frontend_url = settings.FRONTEND_URL
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1e1e1e; color: #e0e0e0; padding: 24px; border-radius: 8px;">
        <h2 style="color: #80cbc4; margin-top: 0;">Com'è andata?</h2>
        <p>Speriamo che il tuo soggiorno sia stato piacevole! Ti invitiamo a lasciare una recensione.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr><td style="padding: 8px 0; color: #999;">Alloggio:</td><td style="padding: 8px 0;"><strong>{booking.accommodation.title}</strong></td></tr>
            <tr><td style="padding: 8px 0; color: #999;">Soggiorno:</td><td style="padding: 8px 0;">{_format_date(booking.check_in)} — {_format_date(booking.check_out)}</td></tr>
        </table>
        <a href="{frontend_url}/my-bookings" style="display: inline-block; padding: 12px 24px; background: #80cbc4; color: #121212; text-decoration: none; border-radius: 4px; font-weight: bold;">Lascia una Recensione</a>
        <p style="color: #999; font-size: 14px; margin-top: 16px;">La tua opinione ci aiuta a migliorare!</p>
    </div>
    """
    return _send(
        f'Lascia una recensione per {booking.accommodation.title}',
        html,
        [booking.user.email],
    )
