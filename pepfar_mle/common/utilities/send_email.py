"""Email sending utility."""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader


def send_email(
    context,
    email,
    plain_text,
    html_temp,
    subject,
    org_name=None,
):
    """Send an email."""
    html_email_template = loader.get_template(html_temp)
    plain_text = loader.get_template(plain_text)
    plain_text_content = plain_text.render(context)
    html_content = html_email_template.render(context)
    sender = settings.DEFAULT_FROM_EMAIL
    email_user = settings.DEFAULT_FROM_EMAIL
    if org_name:
        email_user = "{} <{}>".format(org_name, sender)
    msg = EmailMultiAlternatives(subject, plain_text_content, email_user, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return True
