from django.db import models

class Ticket(models.Model):
    objects = models.Manager()
    text = models.TextField()
    translation = models.TextField(blank=True, default="")
    source_lang = models.CharField(max_length=10, blank=True, default="")
    target_lang = models.CharField(max_length=10, blank=True, default="en")
    category = models.CharField(max_length=50)
    confidence = models.CharField(max_length=20)
    urgency = models.CharField(max_length=20, default="Medium")
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.urgency}] {self.category} - {str(self.text)[:30]}"
