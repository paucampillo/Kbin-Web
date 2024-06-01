from django import forms
from .models import Magazine

class CreateMagazineForm(forms.ModelForm):
    class Meta:
        model = Magazine
        fields = ['name', 'title', 'description', 'rules']
        labels = {
            'name': 'Name',
            'title': 'Title',
            'description': 'Description of the Magazine',
            'rules': 'Rules',
        }
