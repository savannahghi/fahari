import logging

from allauth.account.signals import email_confirmed
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template

LOGGER = logging.getLogger(__name__)
BASIC_PERMISSIONS = [
    "users.can_view_dashboard",
    "users.can_view_about",
]
WHITELIST_PERMISSIONS = BASIC_PERMISSIONS + [
    "common.view_system",
    "common.view_facility",
    "ops.view_facilitysystem",
    "ops.view_facilitysystemticket",
    "ops.view_timesheet",
    "ops.view_stockreceiptverification",
    "ops.view_activitylog",
    "ops.view_sitementorship",
    "ops.view_dailyupdate",
    "ops.add_timesheet",
]

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
        if user.is_approved or user.approval_notified:
            return False  # do nothing

        send_admin_awaiting_approval_email(user)
        send_user_awaiting_approval_email(user)
        return True
    except User.DoesNotExist as e:
        LOGGER.debug("no user with email %s: %s", email_address, e)
        return False


def assign_basic_permissions(user):
    for perm_string in BASIC_PERMISSIONS:
        content_type_app_label, perm_code_name = perm_string.split(".")
        perm = Permission.objects.get(
            content_type__app_label=content_type_app_label, codename=perm_code_name
        )
        user.user_permissions.add(perm)

    user.save()


def assign_whitelist_permissions(user):
    for perm_string in WHITELIST_PERMISSIONS:
        content_type_app_label, perm_code_name = perm_string.split(".")
        perm = Permission.objects.get(
            content_type__app_label=content_type_app_label, codename=perm_code_name
        )
        user.user_permissions.add(perm)

    user.save()


def is_from_whitelist_domain(user_email):
    email = user_email.strip().lower()
    for domain in settings.WHITELISTED_DOMAINS:
        if email.endswith(domain):
            return True

    return False


@receiver(post_save, sender=User)
def account_confirmed_handler(sender, instance, created, **kwargs):
    if created:
        assign_basic_permissions(instance)
        if is_from_whitelist_domain(instance.email):
            assign_whitelist_permissions(instance)
            instance.is_approved = True
            instance.save()

        return

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
