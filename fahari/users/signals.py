import logging

from allauth.account.signals import email_confirmed
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template

LOGGER = logging.getLogger(__name__)

User = get_user_model()


@receiver(email_confirmed)
def email_confirmed_hander(request, email_address, **kwargs):
    """When an user's email is confirmed...

    1. If their account is NOT confirmed, send them an email informing them that they
    will be able to log in after the account is confirmed. Also send an email to admins.
    2. If their account is confirmed, do nothing.
    """
    LOGGER.debug("handling email confirmed signal for email %s", email_address)
    try:
        user = User.objects.get(email=email_address)
        if user.is_approved:
            return False  # do nothing

        send_admin_awaiting_approval_email(user)
        send_user_awaiting_approval_email(user)
        return True
    except User.DoesNotExist as e:
        LOGGER.debug("no user with email %s: %s", email_address, e)
        return False


@receiver(post_save, sender=User)
def account_confirmed_handler(sender, instance, created, **kwargs):
    if created:
        return  # ignore newly saved models...account confirmation is an update

    if not instance.is_approved:
        return  # ignore accounts that are not yet approved

    if instance.approval_notified:
        return  # do not re-send approval emails

    send_user_account_approved_email(instance)
    return True


def send_admin_awaiting_approval_email(user):
    context = {"user": user, "support_email": settings.SERVER_EMAIL}
    message = get_template("emails/account_pending_approval_admin.html").render(context)
    mail = EmailMessage(
        subject="New Fahari System Account Pending Approval",
        body=message,
        from_email=settings.SERVER_EMAIL,
        to=[user.email],
        reply_to=[settings.SERVER_EMAIL],
    )
    mail.content_subtype = "html"
    mail.send()


def send_user_awaiting_approval_email(user):
    context = {"user": user, "support_email": settings.SERVER_EMAIL}
    message = get_template("emails/account_pending_approval_user.html").render(context)
    mail = EmailMessage(
        subject="Fahari System Account Pending Approval",
        body=message,
        from_email=settings.SERVER_EMAIL,
        to=[user.email],
        reply_to=[settings.SERVER_EMAIL],
    )
    mail.content_subtype = "html"
    mail.send()


@transaction.atomic
def send_user_account_approved_email(user):
    context = {"user": user, "support_email": settings.SERVER_EMAIL}
    message = get_template("emails/account_approved.html").render(context)
    mail = EmailMessage(
        subject="Fahari System Account Approved",
        body=message,
        from_email=settings.SERVER_EMAIL,
        to=[user.email],
        reply_to=[settings.SERVER_EMAIL],
    )
    mail.content_subtype = "html"
    mail.send()

    # record the notification so that we do not re-send it
    user.approval_notified = True
    user.save()
