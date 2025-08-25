from django import forms
from .models import Archives

class BaseArchiveForm(forms.ModelForm):
    """Formulaire de base pour Archives avec bootstrap intégré"""

    class Meta:
        model = Archives
        fields = ['titre', 'file', 'description']
        labels = {
            'file':'Televerser '
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ArchiveDocumentForm(BaseArchiveForm):
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 6 * 1024 * 1024:  # 6 Mo
                raise forms.ValidationError("Le fichier ne doit pas dépasser 6 Mo.")
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Le fichier doit être au format PDF.")
        return file

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = "document"
        if commit:
            instance.save()
        return instance


class ArchiveImagesForm(BaseArchiveForm):
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 3 * 1024 * 1024:  # 3 Mo
                raise forms.ValidationError("L'image ne doit pas dépasser 3 Mo.")
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Le fichier doit être une image (JPG, JPEG, PNG ou GIF).")
        return file

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = "image"
        if commit:
            instance.save()
        return instance


class ArchiveVideosForm(BaseArchiveForm):
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 100 * 1024 * 1024:  # 100 Mo
                raise forms.ValidationError("La vidéo ne doit pas dépasser 100 Mo.")
            valid_extensions = ['.mp4', '.avi', '.mov', '.mkv']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("Le fichier doit être une vidéo (MP4, AVI, MOV, MKV).")
        return file

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = "video"
        if commit:
            instance.save()
        return instance
