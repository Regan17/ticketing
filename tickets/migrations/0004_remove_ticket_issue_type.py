# Generated by Django 5.0.1 on 2024-01-23 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_remove_ticket_incident_details_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='issue_type',
        ),
    ]