from django.db import models

class Ticket(models.Model):
    text = models.TextField()
    category = models.CharField(max_length=50)
    confidence = models.CharField(max_length=20)
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.text[:30]}"
