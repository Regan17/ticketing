# tickets/models.py
from django.db import models

class Ticket(models.Model):
    summary = models.TextField()  # Assuming a CharField for summary, adjust if needed
    description = models.TextField()  # Assuming a CharField for issue_type, adjust if needed
    ticket_id = models.CharField(max_length=20, null=True, blank=True)
    jira_access_token = models.CharField(max_length=255, null=True, blank=True)