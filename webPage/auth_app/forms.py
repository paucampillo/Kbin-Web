"""
    This file contains the form for the Thread model
"""

from django import forms
from .models import Profile
from django.contrib.auth.models import User
from betterforms.multiform import MultiModelForm
from django.forms import ImageField, FileInput


class userForm(forms.ModelForm):
    
    class Meta:
    
        model = User
        fields = ["username"]

class profileForm(forms.ModelForm):
    avatar = ImageField(widget=FileInput)
    cover = ImageField(widget=FileInput)    
    def __init__(self, *args, **kwargs):
        super(profileForm, self).__init__(*args, **kwargs)
        self.fields['cover'].required = False
        
    class Meta:
      
        model = Profile
        fields = ["bio", "avatar", "cover"]

        

class UserCreationMultiForm(MultiModelForm):
    form_classes = {
        'user': userForm,
        'profile': profileForm,
    }

    def save(self, commit=True):
        objects = super(UserCreationMultiForm, self).save(commit=False)

        if commit:
            user = objects['user']
            user.save()
            profile = objects['profile']
            profile.user = user
            profile.save()

        return objects
    
    
    def __init__(self, *args, **kwargs):
        super(UserCreationMultiForm, self).__init__(*args, **kwargs)
        self.fields['cover'].required = False

class UserMultiForm(MultiModelForm):
    form_classes = {
        'user': userForm,
        'profile': profileForm,
    }

    #def __init__(self, *args, **kwargs):
     #   super(UserMultiForm, self).__init__(*args, **kwargs)
      #  self.fields['cover'].required = False
