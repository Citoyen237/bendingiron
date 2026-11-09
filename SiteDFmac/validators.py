"""Contrôle du CONTENU des fichiers envoyés (l'extension seule ne suffit pas)."""
from django import forms


def verifier_pdf(fichier, taille_max_mo):
    if fichier.size > taille_max_mo * 1024 * 1024:
        raise forms.ValidationError(f"Le fichier ne doit pas dépasser {taille_max_mo} Mo.")
    if not fichier.name.lower().endswith('.pdf'):
        raise forms.ValidationError("Le fichier doit être au format PDF.")
    debut = fichier.read(5)
    fichier.seek(0)
    if debut != b'%PDF-':
        raise forms.ValidationError("Ce fichier n'est pas un vrai PDF.")
    return fichier


def verifier_image(fichier, taille_max_mo):
    if fichier.size > taille_max_mo * 1024 * 1024:
        raise forms.ValidationError(f"L'image ne doit pas dépasser {taille_max_mo} Mo.")
    from PIL import Image
    try:
        Image.open(fichier).verify()
    except Exception:
        raise forms.ValidationError("Ce fichier n'est pas une image valide.")
    finally:
        fichier.seek(0)
    return fichier
