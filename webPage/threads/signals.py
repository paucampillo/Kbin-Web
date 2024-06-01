"""
Signals for the threads app
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment, Thread, CommentReply
from magazine.models import Magazine

def count_total_comments_and_replies(thread):
    """
    Function to count the total number of comments and replies in a thread
    """
    total_comments = thread.comments.count()  # Count the main comments
    total_replies = CommentReply.objects.filter(thread=thread).count()  # Count the replies
    return total_comments + total_replies



@receiver([post_save, post_delete], sender=Comment)
def update_thread_comment_count_on_comment_change(
    sender, instance, **kwargs
):
    """
    Update the comment count on the thread when a comment is created or deleted
    """
    thread = instance.thread
    thread.num_comments = count_total_comments_and_replies(thread)
    thread.save(update_fields=["num_comments"])

@receiver([post_save, post_delete], sender=CommentReply)
def update_thread_comment_count_on_reply_change(
    sender, instance, **kwargs
):
    """
    Update the comment count on the thread when a reply is created or deleted
    """
    thread = instance.thread
    thread.num_comments = count_total_comments_and_replies(thread)
    thread.save(update_fields=["num_comments"])


@receiver([post_save, post_delete], sender=Thread)
def update_magazine_count(
    sender, instance, **kwargs
):  # pylint: disable=unused-argument
    """
    Update the comment count on the thread after a comment is created or deleted
    """
    magazine = instance.magazine
    magazine.threads_count = magazine.threads.count()
    magazine.comments_count = sum(
        thread.num_comments for thread in magazine.threads.all()
    )
    magazine.save(update_fields=["threads_count", "comments_count"])