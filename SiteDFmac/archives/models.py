from django.db import models
from auth_app.models import CustomUser

# Create your models here.
class Archives(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    file = models.FileField(upload_to='archives/')  # accepte tous les fichiers
    description = models.TextField()
    type = models.CharField(max_length=20)  # exemple: "image", "video", "pdf"
    created_at = models.DateTimeField(auto_now_add=True)  # pour trier facilement
    
    def __str__(self):
        return f"{self.titre}"