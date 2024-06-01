"""
    This file contains the form for the Thread model
"""

from django import forms
from .models import Thread, Comment, CommentReply


####### Thread #######

class ThreadForm(forms.ModelForm):
    """
    Form for the Thread model excluding the URL
    """

    class Meta:
        """
        Meta class for the Thread form
        """

        model = Thread
        fields = ["title", "body", "magazine"]


class LinkForm(forms.ModelForm):
    """
    Form for the Thread model including the URL
    """

    class Meta:
        """
        Meta class for the Link form
        """

        model = Thread
        fields = ["title", "url", "body", "magazine"]


class UpdateThreadLinkForm(forms.ModelForm):
    """
    Form for the Thread model including the URL
    """

    class Meta:
        """
        Meta class for the Link form
        """

        model = Thread
        fields = ["title", "url", "body", "magazine"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # In edition, we can not edit the URL and Magazine fields
        self.fields["url"].disabled = True
        self.fields["magazine"].disabled = True
        # If the thread is not a link, the URL field is not required
        if self.instance.is_link is False:
            self.fields["url"].required = False



######## Comment ########


class CommentForm(forms.ModelForm):
    """
    Form for the Comment model 
    """

    class Meta:
        """
        Meta class for the Comment form
        """

        model = Comment
        fields = ["body"]

class UpdateCommentForm(forms.ModelForm):
    """
    Form for the Comment model 
    """

    class Meta:
        """
        Meta class for the Comment form
        """

        model = Comment
        fields = ["body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ReplyCommentForm(forms.ModelForm):
    """
    Form for the Reply model 
    """

    class Meta:
        """
        Meta class for the Reply form
        """

        model = CommentReply
        fields = ["body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UpdateReplyCommentForm(forms.ModelForm):
    """
    Form for the Comment model 
    """

    class Meta:
        """
        Meta class for the Comment form
        """

        model = CommentReply
        fields = ["body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)