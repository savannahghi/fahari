# Generated by Django 3.2.5 on 2021-07-19 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_is_approved"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "permissions": [
                    ("can_view_dashboard", "Can View Dashboard"),
                    ("can_view_about", "Can View About Page"),
                ],
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
        ),
    ]
