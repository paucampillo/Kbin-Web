"""
    This module contains the views for the Threads app
"""

from django.http import Http404, HttpResponseRedirect
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Thread, Magazine, Vote, User, Boost, Comment, CommentReply
from .forms import (
    ThreadForm,
    LinkForm,
    UpdateThreadLinkForm,
    CommentForm,
    UpdateCommentForm,
    ReplyCommentForm,
    UpdateReplyCommentForm,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.

"""
Thread
"""


class ThreadListView(ListView):
    """
    View for displaying the list of threads
    """

    model = Thread
    template_name = "threads/thread_list.html"
    context_object_name = "threads"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Get the query param "filter" from the HTTP request
        # If no query param, the default value is "all"
        filter_option = self.request.GET.get("filter", "all")

        # Filter the queryset based on the query param
        if filter_option == "threads":
            queryset = queryset.filter(url__isnull=True)
        elif filter_option == "links":
            queryset = queryset.exclude(url__isnull=True)

        # Query param
        order_by = self.request.GET.get("order_by", "created_at")

        # Order the queryset based on the query param
        if order_by == "points":
            queryset = queryset.order_by("-num_points")
        elif order_by == "num_comments":
            queryset = queryset.order_by("-num_comments")
        else:
            queryset = queryset.order_by("-created_at")  # Order by most recent

        # Save the filter and order_by values in the user session
        self.request.session["filter"] = filter_option
        self.request.session["order_by"] = order_by

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # If no query param, the default value is "all"
        # Otherwise, the value could be "threads" or "links"
        filter_option = self.request.session.get("filter", "all")
        order_by = self.request.session.get("order_by", "created_at")

        context["active_filter"] = filter_option
        context["active_order"] = order_by

        return context


class ThreadDetailView(DetailView):
    """
    View for displaying the details of a specific thread
    """

    model = Thread
    template_name = "threads/specific_thread.html"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Query param
        order_by = self.request.GET.get("order_by", "newest")

        if order_by == "points":
            queryset = queryset.order_by("-num_likes", "-created_at")
        elif order_by == "newest":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("created_at")

        # Order the queryset based on the query param
        self.request.session["order_by"] = order_by

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = self.get_object()
        thread_id = self.kwargs["pk"]
        order_by = self.request.GET.get("order_by", "newest")

        comments = Comment.objects.filter(thread_id=thread_id)
        if order_by == "points":
            comments = comments.order_by("-num_likes", "-created_at")
        elif order_by == "newest":
            comments = comments.order_by("-created_at")
        else:
            comments = comments.order_by("created_at")

        context["comments"] = comments
        context["magazine"] = thread.magazine
        context["active_order"] = order_by

        return context


@method_decorator(login_required, name="dispatch")
class CreateThread(CreateView):
    """
    View for creating a new thread (thread without URL)
    """

    model = Thread
    form_class = ThreadForm
    template_name = "threads/add_thread.html"

    def form_valid(self, form):
        thread = form.save(commit=False)
        thread.is_link = False  # By default it is false, but just to be explicit
        thread.author = self.request.user
        thread.save()

        # Get the filter and order_by values from the user session
        filter_option = self.request.session.get("filter", "all")
        order_by = self.request.session.get("order_by", "created_at")

        # Build the redirect URL based on the filter and order_by values
        redirect_url = reverse("thread_list")
        params = {}
        if filter_option != "all":
            params["filter"] = filter_option
        if order_by:
            params["order_by"] = order_by
        if params:
            redirect_url += "?" + "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )

        return HttpResponseRedirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["magazines"] = Magazine.objects.all()  # pylint: disable=no-member
        return context


@method_decorator(login_required, name="dispatch")
class CreateLink(CreateView):
    """
    View for creating a new link (thread with URL)
    """

    model = Thread
    form_class = LinkForm
    template_name = "threads/add_link.html"

    def form_valid(self, form):
        thread = form.save(commit=False)  # Save the form but don't save to the database
        thread.is_link = True
        thread.author = self.request.user
        thread.save()

        # Get the filter and order_by values from the user session
        filter_option = self.request.session.get("filter", "all")
        order_by = self.request.session.get("order_by", "created_at")

        # Build the redirect URL based on the filter and order_by values
        redirect_url = reverse("thread_list")
        params = {}
        if filter_option != "all":
            params["filter"] = filter_option
        if order_by:
            params["order_by"] = order_by
        if params:
            redirect_url += "?" + "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )

        return HttpResponseRedirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["magazines"] = Magazine.objects.all()  # pylint: disable=no-member
        return context


class UpdateThreadAndLink(UpdateView):
    """
    View for updating a thread
    """

    model = Thread
    form_class = UpdateThreadLinkForm  # If is thread, the HTML excludes the URL field
    template_name = "threads/edit_thread_and_link.html"
    success_url = "/threads/"  # Redirection URL after successful update

    def dispatch(self, request, *args, **kwargs):
        thread = self.get_object()
        # Verificar si el usuario actual es el autor del hilo
        if thread.author != request.user:
            raise Http404("You are not allowed to edit this thread.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = self.get_object()
        context["magazine"] = thread.magazine
        if self.object.url:
            context["is_link"] = True
        else:
            context["is_link"] = False
        return context

    def form_valid(self, form):
        thread = form.save(commit=False)
        thread.save()

        # Get the filter and order_by values from the user session
        filter_option = self.request.session.get("filter", "all")
        order_by = self.request.session.get("order_by", "created_at")

        # Build the redirect URL based on the filter and order_by values
        redirect_url = reverse("thread_list")
        params = {}
        if filter_option != "all":
            params["filter"] = filter_option
        if order_by:
            params["order_by"] = order_by
        if params:
            redirect_url += "?" + "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )

        return HttpResponseRedirect(redirect_url)


class DeleteThreadOrLink(DeleteView):
    """
    View for deleting a specific thread
    """

    model = Thread
    success_url = reverse_lazy("thread_list")  # Redirect URL after successful deletion

    def get_success_url(self):
        # Get the filter and order_by values from the user session
        filter_option = self.request.session.get("filter", "all")
        order_by = self.request.session.get("order_by")

        # Build the redirect URL based on the filter and order_by values
        redirect_url = reverse_lazy("thread_list")
        params = {}
        if filter_option != "all":
            params["filter"] = filter_option
        if order_by:
            params["order_by"] = order_by
        if params:
            redirect_url += "?" + "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )

        return redirect_url


@login_required
def vote_thread(request, pk):  # pylint: disable=unused-argument
    """
    View for voting a specific thread
    """
    if request.method == "POST":
        thread_id = request.POST.get("thread_id")
        vote_type = request.POST.get("vote_type")
        user = User.objects.get(
            id=request.user.id
        )  # request.user (Add this when login is implemented)
        thread = Thread.objects.get(id=thread_id)  # pylint: disable=no-member

        # Check if the user has already voted this thread
        existing_vote = None
        try:
            existing_vote = Vote.objects.get(  # pylint: disable=no-member
                user=user, thread=thread
            )
        except ObjectDoesNotExist:
            # If the user has not voted previously, create a new vote
            Vote.objects.create(  # pylint: disable=no-member
                user=user, thread=thread, vote_type=vote_type
            )

        if existing_vote:  # Any object is considered True
            if existing_vote.vote_type == vote_type:
                # If the user votes the same as their previous vote, delete the vote
                existing_vote.delete()
            else:
                # If the user changes their vote, update the existing vote
                existing_vote.vote_type = vote_type
                existing_vote.save()

        # Update likes and dislikes counts
        likes = Vote.objects.filter(  # pylint: disable=no-member
            thread=thread, vote_type="like"
        ).count()
        dislikes = Vote.objects.filter(  # pylint: disable=no-member
            thread=thread, vote_type="dislike"
        ).count()

        # Update thread with the num_likes and num_dislikes without updating the updated_at field
        Thread.objects.filter(id=thread_id).update(  # pylint: disable=no-member
            num_likes=likes,
            num_dislikes=dislikes,
        )

        # Redirect back to the previous page it comes from or to a default page ("thread_list")
        return redirect(request.META.get("HTTP_REFERER", "thread_list"))


@login_required
def boost_thread(request, pk):  # pylint: disable=unused-argument
    """
    View for boosting a specific thread
    """
    if request.method == "POST":
        thread_id = request.POST.get("thread_id")
        user = User.objects.get(id=request.user.id)  # pylint: disable=no-member
        thread = Thread.objects.get(id=thread_id)  # pylint: disable=no-member

        # Check if the user has already boosted this thread
        existing_boost = None
        try:
            existing_boost = Boost.objects.get(  # pylint: disable=no-member
                user=user, thread=thread
            )
        except ObjectDoesNotExist:
            # If the user has not boosted previously, create a new Boost
            Boost.objects.create(  # pylint: disable=no-member
                user=user,
                thread=thread,
            )
            # Update the thread with the num_likes without updating the updated_at field
            Thread.objects.filter(id=thread_id).update(  # pylint: disable=no-member
                num_points=thread.num_points + 1,
            )

        if existing_boost:  # Any object is considered True
            # If the user has already boosted the thread, delete the Boost
            existing_boost.delete()
            # Update the thread with the num_likes without updating the updated_at field
            Thread.objects.filter(id=thread_id).update(  # pylint: disable=no-member
                num_points=thread.num_points - 1,
            )

        # Redirect back to the previous page it comes from or to a default page ("thread_list")
        return redirect(request.META.get("HTTP_REFERER", "thread_list"))


"""
Comment
"""


class CommentListView(ListView):
    """
    View for displaying the list of comments
    """

    model = Comment
    template_name = "threads/specific_thread.html"
    context_object_name = "comments"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Query param
        order_by = self.request.GET.get("order_by", "created_at")

        if order_by == "points":
            queryset = queryset.order_by("-num_likes", "-created_at")
        elif order_by == "newest":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("created_at")

        # Order the queryset based on the query param
        self.request.session["order_by"] = order_by

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If no query param, the default value is "all"
        # Otherwise, the value could be "threads" or "links"
        order_by = self.request.GET.get("order_by")
        context["active_order"] = order_by
        return context


@method_decorator(login_required, name="dispatch")
class CreateComment(CreateView):  # LoginRequiredMixin
    """
    View for creating a new comment
    """

    model = Comment
    form_class = CommentForm
    template_name = "threads/specific_thread.html"

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.thread_id = self.kwargs[
            "thread_id"
        ]  # Obtener el ID del thread de los parámetros de la URL
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread_id = self.kwargs[
            "thread_id"
        ]  # Obtener el ID del thread de los parámetros de la URL
        order_by = self.request.GET.get("order_by", "newest")
        comments = Comment.objects.filter(
            thread_id=thread_id
        )  # Obtén todos los comentarios

        for comment in comments:
            # Obtener todas las respuestas asociadas a este comentario
            replies = CommentReply.objects.filter(parent_comment=comment)
            comment.comment_replies.set(replies)
            for reply in replies:
                # Obtener las subrespuestas del comentario original
                subreplies = CommentReply.objects.filter(
                    parent_comment=comment, parent_reply=reply
                )
                reply.reply_replies.set(subreplies)

        if order_by == "points":
            comments = comments.order_by("-num_likes", "-created_at")
        elif order_by == "newest":
            comments = comments.order_by("-created_at")
        else:
            comments = comments.order_by("created_at")

        context["comments"] = comments
        context["thread"] = Thread.objects.get(id=thread_id)
        context["active_order"] = order_by
        return context

    def get_queryset(self):
        queryset = super().get_queryset()   

        # Query param
        order_by = self.request.GET.get("order_by", "newest")

        if order_by == "points":
            queryset = queryset.order_by("-num_likes", "-created_at")
        elif order_by == "newest":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("created_at")

        # Order the queryset based on the query param
        self.request.session["order_by"] = order_by

        return queryset

    def get_success_url(self):
        return reverse_lazy("thread_detail", kwargs={"pk": self.kwargs["thread_id"]})


class UpdateComment(UpdateView):
    """
    View for updating a comment
    """

    model = Comment
    form_class = UpdateCommentForm
    template_name = "threads/edit_comment.html"

    def dispatch(self, request, *args, **kwargs):
        thread = self.get_object()
        # Verificar si el usuario actual es el autor del hilo
        if thread.author != request.user:
            raise Http404("You are not allowed to edit this thread.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = self.get_object()
        context["magazine"] = comment.magazine
        comment.save()
        return context

    def get_success_url(self):
        # Aquí defines la URL a la que quieres redirigir
        return reverse_lazy("thread_detail", kwargs={"pk": self.object.thread_id})


class DeleteComment(DeleteView):
    """
    View for deleting a specific comment
    """

    model = Comment

    def get_success_url(self):
        thread_id = self.kwargs["thread_id"]
        return reverse_lazy("thread_detail", kwargs={"pk": thread_id})


@login_required
def vote_comment(request, pk):  # pylint: disable=unused-argument
    """
    View for voting a specific comment
    """
    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        vote_type = request.POST.get("vote_type")
        user = User.objects.get(
            id=request.user.id
        )  # request.user (Add this when login is implemented)
        comment = Comment.objects.get(id=comment_id)

        # Check if the user has already voted this comment
        existing_vote = None
        try:
            existing_vote = Vote.objects.get(user=user, comment=comment)
        except ObjectDoesNotExist:
            # If the user has not voted previously, create a new vote
            Vote.objects.create(  # pylint: disable=no-member
                user=user, comment=comment, vote_type=vote_type
            )

        if existing_vote:  # Any object is considered True
            if existing_vote.vote_type == vote_type:
                # If the user votes the same as their previous vote, delete the vote
                existing_vote.delete()
            else:
                # If the user changes their vote, update the existing vote
                existing_vote.vote_type = vote_type
                existing_vote.save()

        # Update likes and dislikes counts
        likes = Vote.objects.filter(comment=comment, vote_type="like").count()
        dislikes = Vote.objects.filter(comment=comment, vote_type="dislike").count()

        # Update comment with the num_likes and num_dislikes without updating the updated_at field
        Comment.objects.filter(id=comment_id).update(
            num_likes=likes,
            num_dislikes=dislikes,
        )

        # Redirect back to the previous page it comes from or to a default page ("thread_list")
        return redirect(request.META.get("HTTP_REFERER", "specific_thread"))


@method_decorator(login_required, name="dispatch")
class ReplyCommentView(CreateView):

    model = CommentReply
    form_class = ReplyCommentForm
    template_name = "threads/reply_comment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_id = self.kwargs.get("pk")  # Aquí se corrige 'comment_id' por 'pk'
        parent_comment = get_object_or_404(Comment, pk=comment_id)
        context["parent_comment"] = parent_comment
        replies = CommentReply.objects.filter(parent_comment=parent_comment)
        context["replies"] = replies
        context["comment"] = comment_id
        return context

    def form_valid(self, form):
        reply = form.save(commit=False)
        parent_comment_id = self.kwargs.get(
            "pk"
        )  # Aquí se corrige 'comment_id' por 'pk'

        parent_reply_id = self.kwargs.get("parent_reply_id")  # Nuevo

        parent_comment = get_object_or_404(Comment, pk=parent_comment_id)

        if parent_reply_id:
            parent_reply = get_object_or_404(CommentReply, pk=parent_reply_id)
            reply.parent_reply = parent_reply
            reply.reply_level = (
                parent_reply.reply_level + 1
            )  # Establecer el nivel correcto
        else:
            reply.reply_level = 1  # Nivel 1 si es una respuesta directa al comentario

        reply.parent_comment = parent_comment
        reply.author = self.request.user
        reply.thread = parent_comment.thread
        reply.save()
        return super().form_valid(form)

    def get_success_url(self):
        thread_id = self.kwargs["thread_id"]
        return reverse_lazy("thread_detail", kwargs={"pk": thread_id})


class UpdateReply(UpdateView):
    """
    View for updating a reply
    """

    model = CommentReply
    form_class = UpdateReplyCommentForm
    template_name = "threads/edit_comment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reply = self.get_object()
        context["magazine"] = reply.magazine
        return context

    def get_success_url(self):
        thread_id = self.kwargs["thread_id"]
        return reverse_lazy("thread_detail", kwargs={"pk": thread_id})


class DeleteReply(DeleteView):
    """
    View for deleting a specific reply
    """

    model = CommentReply

    def get_success_url(self):
        thread_id = self.kwargs["thread_id"]
        return reverse_lazy("thread_detail", kwargs={"pk": thread_id})


@login_required
def vote_reply(request, pk):  # pylint: disable=unused-argument
    """
    View for voting a specific reply
    """
    if request.method == "POST":
        reply_id = request.POST.get("reply_id")
        vote_type = request.POST.get("vote_type")
        user = User.objects.get(
            id=request.user.id
        )  # request.user (Add this when login is implemented)
        reply = CommentReply.objects.get(id=reply_id)  # pylint: disable=no-member

        # Check if the user has already voted this reply
        existing_vote = None
        try:
            existing_vote = Vote.objects.get(  # pylint: disable=no-member
                user=user, reply=reply
            )
        except ObjectDoesNotExist:
            # If the user has not voted previously, create a new vote
            Vote.objects.create(  # pylint: disable=no-member
                user=user, reply=reply, vote_type=vote_type
            )

        if existing_vote:  # Any object is considered True
            if existing_vote.vote_type == vote_type:
                # If the user votes the same as their previous vote, delete the vote
                existing_vote.delete()
            else:
                # If the user changes their vote, update the existing vote
                existing_vote.vote_type = vote_type
                existing_vote.save()

        # Update likes and dislikes counts
        likes = Vote.objects.filter(  # pylint: disable=no-member
            reply=reply, vote_type="like"
        ).count()
        dislikes = Vote.objects.filter(  # pylint: disable=no-member
            reply=reply, vote_type="dislike"
        ).count()

        # Update reply with the num_likes and num_dislikes without updating the updated_at field
        CommentReply.objects.filter(id=reply_id).update(  # pylint: disable=no-member
            num_likes=likes,
            num_dislikes=dislikes,
        )

        # Redirect back to the previous page it comes from or to a default page
        return redirect(request.META.get("HTTP_REFERER", "specific_thread"))


class SearchView(ListView):
    """
    View for searching threads
    """

    model = Thread
    template_name = "threads/search.html"
    content_object_name = "threads"


class SearchResultsView(ListView):
    """
    View for displaying search results
    """

    model = Thread
    template_name = "threads/search_results.html"
    context_object_name = "threads"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if not query.strip():
            return Thread.objects.none()
        else:
            threads = Thread.objects.filter(
                title__icontains=query
            ) | Thread.objects.filter(body__icontains=query)
            return threads

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class MagazineThreadsListView(ListView):
    """
    View for displaying the list of threads in a magazine
    """

    template_name = "thread_list.html"
    context_object_name = "threads"

    def get_queryset(self):
        # Get the magazine ID from the URL
        magazine_id = self.kwargs.get("magazine_id")

        queryset = Thread.objects.filter(magazine_id=magazine_id)

        return queryset
