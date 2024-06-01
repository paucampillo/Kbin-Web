from django.contrib import admin
from .models import Magazine



# En admin.py
from django.contrib import admin
from .models import Magazine

class MagazineAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Si es una nueva instancia, establecer el creador
            obj.creator = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Magazine, MagazineAdmin)


# Register your models here.
