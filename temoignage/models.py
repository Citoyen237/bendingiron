from django.db import models

# Create your models here.
class Temoignage(models.Model):
    name=models.CharField(max_length=100)
    content=models.TextField()
    image=models.ImageField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content