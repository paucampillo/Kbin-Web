"""
This file is used to register the models in the admin interface.
"""

from django.contrib import admin

# Register your models here to handle in the admin interface
from .models import Thread, Comment

admin.site.register(Thread)

admin.site.register(Comment)
