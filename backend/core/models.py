from django.db import models

class Ticket(models.Model):
    objects = models.Manager()
    text = models.TextField()
    translated_text = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50)
    confidence = models.CharField(max_length=20)
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {str(self.text)[:30]}"
