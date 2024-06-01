"""
    This module contains the models for the Threads app
"""

from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince
from magazine.models import Magazine
from django.contrib.auth.models import User  # Importar el modelo User


#### Thread ####


class Thread(models.Model):
    """
    Threads Model
    """

    title = models.TextField(max_length=255)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,  # Temporary it lets null
        related_name="threads"
    )
    url = models.URLField(null=True)
    body = models.TextField(blank=True, null=True, default="")
    # If delete the magazine, automatically delete the thread
    magazine = models.ForeignKey(
        Magazine,
        on_delete=models.CASCADE,
        null=True,  # Temporary it lets null
        related_name="threads"
    )

    # Update only once at creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Update after each save
    updated_at = models.DateTimeField(auto_now=True)
    # To manage the type of thread in HTML
    is_link = models.BooleanField(default=False)  # True if URL is present
    num_likes = models.IntegerField(default=0)
    num_dislikes = models.IntegerField(default=0)
    num_points = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)

    def __str__(self):
        return str(self.title)

    @property
    def time_since_creation(self):
        """
        Return the time since the thread was created as a model attribute
        """
        # Time since the thread was created
        time_since = timesince(self.created_at, timezone.now())
        # If "4 hours, 30 minutes" -> ["4", "hours,"]
        time_parts = time_since.split()[:2]

        # If last character of the second word is ",", remove it
        if len(time_parts) > 1 and time_parts[1][-1] == ",":
            time_parts[1] = time_parts[1][:-1]  # Last character excluded

        # ["4", "hours,"] -> "4 hours"
        return " ".join(time_parts)

    @property
    def time_since_update(self):
        """
        Return the time since the thread was updated as a model attribute
        """
        # Time since the thread was created
        time_since = timesince(self.updated_at, timezone.now())
        # If "4 hours, 30 minutes" -> ["4", "hours,"]
        time_parts = time_since.split()[:2]

        # If last character of the second word is ",", remove it
        if len(time_parts) > 1 and time_parts[1][-1] == ",":
            time_parts[1] = time_parts[1][:-1]  # Last character excluded

        # ["4", "hours,"] -> "4 hours"
        return " ".join(time_parts)



#### Comment ####


class Comment(models.Model):
    """
    Comment Model
    """
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,  # Temporary it lets null
    )
    body = models.TextField(max_length=5000)
    # If delete the magazine, automatically delete the thread
    magazine = models.ForeignKey(
        Magazine,
        on_delete=models.CASCADE,
        null=True,  # Temporary it lets null
    )

    # Update only once at creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Update after each save
    updated_at = models.DateTimeField(auto_now=True)
    # To manage the type of thread in HTML
    num_likes = models.IntegerField(default=0)
    num_dislikes = models.IntegerField(default=0)
    num_replies = models.IntegerField(default=0)

    def __str__(self):
        return str(self.body)

    @property
    def time_since_creation(self):
        """
        Return the time since the comment was created as a model attribute
        """
        # Time since the comment was created
        time_since = timesince(self.created_at, timezone.now())
        # If "4 hours, 30 minutes" -> ["4", "hours,"]
        time_parts = time_since.split()[:2]

        # If last character of the second word is ",", remove it
        if len(time_parts) > 1 and time_parts[1][-1] == ",":
            time_parts[1] = time_parts[1][:-1]  # Last character excluded

        # ["4", "hours,"] -> "4 hours"
        return " ".join(time_parts)
    
    @property
    def time_since_update(self):
        """
        Return the time since the comment was updated as a model attribute
        """
        # Time since the comment was created
        time_since = timesince(self.updated_at, timezone.now())
        # If "4 hours, 30 minutes" -> ["4", "hours,"]
        time_parts = time_since.split()[:2]

        # If last character of the second word is ",", remove it
        if len(time_parts) > 1 and time_parts[1][-1] == ",":
            time_parts[1] = time_parts[1][:-1]  # Last character excluded

        # ["4", "hours,"] -> "4 hours"
        return " ".join(time_parts)
    
class CommentReply(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,  # Temporary it lets null
    )
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="thread_replies")
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="comment_replies")
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="reply_replies")
    body = models.TextField(max_length=5000)
    # If delete the magazine, automatically delete the thread
    magazine = models.ForeignKey(
        Magazine,
        on_delete=models.CASCADE,
        null=True,  # Temporary it lets null
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Update after each save
    updated_at = models.DateTimeField(auto_now=True)
    # To manage the type of thread in HTML
    num_likes = models.IntegerField(default=0)
    num_dislikes = models.IntegerField(default=0)
    num_replies = models.IntegerField(default=0)

    reply_level = models.PositiveIntegerField(default=1)


    def __str__(self):
        return str(self.body)

    @property
    def time_since_creation(self):
        """
        Return the time since the comment was created as a model attribute
        """
        # Time since the comment was created
        time_since = timesince(self.created_at, timezone.now())
        # If "4 hours, 30 minutes" -> ["4", "hours,"]
        time_parts = time_since.split()[:2]

        # If last character of the second word is ",", remove it
        if len(time_parts) > 1 and time_parts[1][-1] == ",":
            time_parts[1] = time_parts[1][:-1]  # Last character excluded

        # ["4", "hours,"] -> "4 hours"
        return " ".join(time_parts)
    
    @property
    def time_since_update(self):
        """
        Return the time since the comment was updated as a model attribute
        """
        # Time since the comment was created
        time_since = timesince(self.updated_at, timezone.now())
        # If "4 hours, 30 minutes" -> ["4", "hours,"]
        time_parts = time_since.split()[:2]

        # If last character of the second word is ",", remove it
        if len(time_parts) > 1 and time_parts[1][-1] == ",":
            time_parts[1] = time_parts[1][:-1]  # Last character excluded

        # ["4", "hours,"] -> "4 hours"
        return " ".join(time_parts)
 

"""
Other
"""

class Vote(models.Model):
    """
    Vote Model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey(CommentReply, on_delete=models.CASCADE, null=True, blank=True)

    vote_type = models.CharField(
        max_length=10, choices=[("like", "like"), ("dislike", "dislike")]
    )


class Boost(models.Model):
    """
    Boost Model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)