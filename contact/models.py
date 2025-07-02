from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.
# class 
# type de la demande



    
class Contact(models.Model):
    TYPE_CHOICES = [
        ('devis_assemblage', "Devis d'assemblage"),
        ('devis_assemblage_pose', "Devis d'assemblage + pose"),
        ('renseignements', "Renseignements"),
        ('autre', "Autre"),
    ]
    email=models.EmailField()
    nom=models.CharField(max_length=250)
    telephone = models.CharField(max_length=250)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    file = models.FileField(upload_to='contacts/files/', null=True, blank=True)
    file_response = models.FileField(upload_to='contacts/files/', null=True, blank=True)
    reponse = models.TextField(null=True, blank=True)
    is_read=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
    
    @staticmethod
    def get_unread_messages():
        return Contact.objects.filter(is_read=False).order_by('-created_at').all()
    
    def preview_content(self):
        words = self.message.split()[:8]
        return ' '.join(words) + ('...' if len(words) == 8 else '')

def validate_pdf(file):
    if not file.name.lower().endswith('.pdf'):
        raise ValidationError("Le fichier doit être au format PDF.")
    if file.size > 3 * 1024 * 1024:  # 3 Mo
        raise ValidationError("Le fichier ne doit pas dépasser 3 Mo.")

def validate_pdf1(file_response):
    if not file_response.name.lower().endswith('.pdf'):
        raise ValidationError("Le fichier doit être au format PDF.")
    if file_response.size > 3 * 1024 * 1024:  # 3 Mo
        raise ValidationError("Le fichier ne doit pas dépasser 3 Mo.")
    
class ContactFile(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='contacts/files/', validators=[validate_pdf])

    def __str__(self):
        return f"Fichier pour {self.contact.email}"