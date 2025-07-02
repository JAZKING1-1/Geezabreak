from django.db import models

class Comment(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)  # Optionally add moderation

    def __str__(self):
        return f"{self.name}: {self.message[:30]}..."
