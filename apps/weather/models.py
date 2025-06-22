from django.db import models

class SearchHistory(models.Model):
    city = models.CharField(max_length=100)
    search_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city} at {self.search_time}"

    class Meta:
        ordering = ['-search_time']
