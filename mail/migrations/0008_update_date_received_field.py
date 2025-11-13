# Generated manually to update date_received field

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0007_add_password_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailmessage',
            name='date_received',
            field=models.DateTimeField(help_text='Date when email was received (from email header or server)'),
        ),
    ]

