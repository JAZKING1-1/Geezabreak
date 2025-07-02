from django.db import models

# Create your models here.

class Feedback(models.Model):
    SERVICE_CHOICES = [
        ('respite', 'Respite Care'),
        ('wellbeing', 'Wellbeing Support'),
        ('parenting', 'Parenting Workshops'),
        ('kinship', 'Kinship Care'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    service_used = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.name} - {self.service_used}"
