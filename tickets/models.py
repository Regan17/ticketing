# tickets/models.py
from django.db import models

class Ticket(models.Model):
    incident_details = models.TextField()
    user_information = models.CharField(max_length=255)
    ticket_id = models.CharField(max_length=20, null=True, blank=True)
    # jira_access_token = models.CharField(max_length=255, null=True, blank=True)