from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
#from user_profile.models import User

# Create your models here.

#https://docs.djangoproject.com/en/5.0/ref/contrib/auth/ documentation model User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    bio = models.TextField(max_length=500, blank=True, default="About myself")
    avatar = models.ImageField(upload_to="media/", default="default.png")
    cover = models.ImageField(upload_to="media/", null=True, blank=True, default="blank_cover.png")

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
    
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return self.user.username  # Utilizar el nombre de usuario asociado al perfil


