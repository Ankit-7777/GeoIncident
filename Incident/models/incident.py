from django.db import models
import random
from datetime import datetime

class Incident(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed'),
    ]
    ENTITY_CHOICES = [
        ('Individual', 'Individual'),
        ('Enterprise', 'Enterprise'),
        ('Government', 'Government'),
    ]
    id = models.AutoField(primary_key=True,  unique=True)
    incident_id = models.CharField(max_length=12, unique=True)
    reporter = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    details = models.TextField()
    reported_date = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Open')
    entity_type = models.CharField(max_length=10, choices=ENTITY_CHOICES)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.incident_id:
            self.incident_id = self.generate_incident_id()
            self.save()

    def generate_incident_id(self):
        year = datetime.now().year
        random_part = f"{random.randint(10000, 99999):05d}"
        incident_id = f"RMG{random_part[:-len(str(self.id))]}{self.id}{year}"
        return incident_id


    def __str__(self):
        return self.incident_id
    


