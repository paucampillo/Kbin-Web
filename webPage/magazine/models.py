from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Magazine(models.Model):
    name = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=200)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,  # Temporary it lets null
    )

    description = models.TextField(blank=True, null=True)
    rules = models.TextField(blank=True, null=True)
    publish_date = models.DateField(
        verbose_name="Fecha de Publicación", auto_now_add=True
    )
    subscriptions_count = models.IntegerField(default=0)
    threads_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Revista"
        verbose_name_plural = "Revistas"
        ordering = ["-publish_date"]

    def __str__(self):
        return self.name

    def count_threads(self):
        return self.threads.count()

    def count_comments(self):
        # Esto asume que cada Thread tiene un conjunto de Comments relacionados
        return sum([thread.comments.count() for thread in self.threads.all()])

    def count_subscriptions(self):
        return self.subscriptions.count()


class Subscription(models.Model):
    magazine = models.ForeignKey(
        Magazine, on_delete=models.CASCADE, related_name="subscriptions"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    # Campos adicionales para tu modelo Subscription
