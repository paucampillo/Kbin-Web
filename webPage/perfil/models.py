
from django.db import models

# Create your models here.
class ProfileUser(models.Model):
    name = models.CharField(max_length=200)
    cover = models.ImageField(upload_to='fotos_perfil/', blank=True,null=True)
    avatar = models.ImageField(upload_to='fotos_perfil/', blank=True,null=True)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name

    