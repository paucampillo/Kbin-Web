from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.views import APIView
from .models import Thread, Boost, Vote, Comment, CommentReply
from .serializers import (
    ThreadSerializer,
    CreateThreadSerializer,
    EditThreadSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    EditCommentSerializer,
    CommentReplySerializer,
    CreateCommentReplySerializer,
    EditCommentReplySerializer,
    CommentReplyReplySerializer,
    CreateCommentReplyReplySerializer,
    EditCommentReplyReplySerializer,
    BoostSerializer,
    VoteSerializer,
    SearchSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import F




class ThreadsAPIView(ListCreateAPIView):
    serializer_class = ThreadSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "filter",
                openapi.IN_QUERY,
                description="Filter threads by 'all', 'threads', or 'links'",
                type=openapi.TYPE_STRING,
                default="all",
            ),
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                description="Order threads by 'created_at', 'points', or 'num_comments'",
                type=openapi.TYPE_STRING,
                default="created_at",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateThreadSerializer
        return ThreadSerializer

    def get_queryset(self):
        queryset = Thread.objects.all()

        # Get the query param "filter" from the HTTP request
        # If no query param, the default value is "all"
        filter_option = self.request.query_params.get("filter", "all")

        # Filter the queryset based on the query param
        if filter_option == "threads":
            queryset = queryset.filter(url__isnull=True)
        elif filter_option == "links":
            queryset = queryset.exclude(url__isnull=True)

        # Query param
        order_by = self.request.query_params.get("order_by", "created_at")

        # Order the queryset based on the query param
        if order_by == "points":
            queryset = queryset.order_by("-num_points")
        elif order_by == "num_comments":
            queryset = queryset.order_by("-num_comments")
        else:
            queryset = queryset.order_by("-created_at")  # Order by most recent

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context

class ThreadDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    lookup_field = "id"  # No se utiliza, se ha sobreescrito el método get_object
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return EditThreadSerializer
        return super().get_serializer_class()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs["thread_id"])
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user requesting the action is the same as the user object being retrieved
        if instance.author.id != request.user.id:
            return Response(
                data={"error": "You can only delete a tweet created by you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().delete(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user requesting the action is the same as the user object being retrieved
        if instance.author.id != request.user.id:
            return Response(
                data={"error": "You can only update a tweet created by you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context


class BoostAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        thread_id = self.kwargs.get("thread_id")
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response(
                {"message": "Thread does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already boosted this thread
        boost, created = Boost.objects.get_or_create(user=user, thread=thread)

        if created:
            # Update the thread with the num_likes without updating the updated_at field
            Thread.objects.filter(id=thread_id).update(num_points=thread.num_points + 1)
            # Serialize the boost data
            boost_data = BoostSerializer(boost).data
            return Response(boost_data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": "The user has already boosted this thread"},
                status=status.HTTP_409_CONFLICT,
            )

    def delete(self, request, *args, **kwargs):
        thread_id = self.kwargs.get("thread_id")
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response(
                {"message": "Thread does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already boosted this thread
        try:
            boost = Boost.objects.get(user=user, thread=thread)
        except Boost.DoesNotExist:
            return Response(
                {"message": "The user has not boosted this thread"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if boost:
            # If the user has already boosted the thread, delete the Boost
            boost.delete()
            # Update the thread with the num_likes without updating the updated_at field
            Thread.objects.filter(id=thread_id).update(num_points=thread.num_points - 1)
            return Response(status=status.HTTP_204_NO_CONTENT)


class LikeAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        thread_id = self.kwargs.get("thread_id")
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response(
                {"message": "Thread does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already liked this thread
        vote, created = Vote.objects.get_or_create(
            user=user, thread=thread, vote_type="like"
        )

        if not created:
            # If the user had already liked the thread, return a 409 Conflict response
            return Response(
                {"message": "The user has already liked this thread"},
                status=status.HTTP_409_CONFLICT,
            )

        # If the user had previously disliked this thread, delete the dislike
        existing_dislike = Vote.objects.filter(
            user=user, thread=thread, vote_type="dislike"
        ).first()
        if existing_dislike:
            existing_dislike.delete()

        # Update the thread with the num_likes without updating the updated_at field
        likes = Vote.objects.filter(thread=thread, vote_type="like").count()
        dislikes = Vote.objects.filter(thread=thread, vote_type="dislike").count()
        Thread.objects.filter(id=thread_id).update(
            num_likes=likes, num_dislikes=dislikes
        )

        # Serialize the like data
        like_data = {
            "id": vote.id,
            "user": vote.user.id,
            "thread": vote.thread.id,
            "vote_type": vote.vote_type,
        }
        return Response(like_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        thread_id = self.kwargs.get("thread_id")
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response(
                {"message": "Thread does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already liked this thread
        try:
            like = Vote.objects.get(user=user, thread=thread, vote_type="like")
        except Vote.DoesNotExist:
            return Response(
                {"message": "The user has not liked this thread"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if like:
            # If the user has already liked the thread, delete the Like
            like.delete()
            # Update the thread with the num_likes without updating the updated_at field
            likes = Vote.objects.filter(thread=thread, vote_type="like").count()
            Thread.objects.filter(id=thread_id).update(num_likes=likes)
            return Response(status=status.HTTP_204_NO_CONTENT)


class DislikeAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        thread_id = self.kwargs.get("thread_id")
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response(
                {"message": "Thread does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already disliked this thread
        vote, created = Vote.objects.get_or_create(
            user=user, thread=thread, vote_type="dislike"
        )

        if not created:
            # If the user had already disliked the thread, return a 409 Conflict response
            return Response(
                {"message": "The user has already disliked this thread"},
                status=status.HTTP_409_CONFLICT,
            )

        # If the user had previously liked this thread, delete the like
        existing_like = Vote.objects.filter(
            user=user, thread=thread, vote_type="like"
        ).first()
        if existing_like:
            existing_like.delete()

        # Update the thread with the num_likes without updating the updated_at field
        dislikes = Vote.objects.filter(thread=thread, vote_type="dislike").count()
        likes = Vote.objects.filter(thread=thread, vote_type="like").count()
        Thread.objects.filter(id=thread_id).update(
            num_dislikes=dislikes, num_likes=likes
        )

        # Serialize the dislike data
        dislike_data = {
            "id": vote.id,
            "user": vote.user.id,
            "thread": vote.thread.id,
            "vote_type": vote.vote_type,
        }
        return Response(dislike_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        thread_id = self.kwargs.get("thread_id")
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response(
                {"message": "Thread does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already disliked this thread
        try:
            dislike = Vote.objects.get(user=user, thread=thread, vote_type="dislike")
        except Vote.DoesNotExist:
            return Response(
                {"message": "The user has not disliked this thread"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if dislike:
            # If the user has already disliked the thread, delete the Dislike
            dislike.delete()
            # Update the thread with the num_likes without updating the updated_at field
            dislikes = Vote.objects.filter(thread=thread, vote_type="dislike").count()
            Thread.objects.filter(id=thread_id).update(num_dislikes=dislikes)
            return Response(status=status.HTTP_204_NO_CONTENT)


class CommentDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = "comment_id"
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return EditCommentSerializer
        return super().get_serializer_class()

    def get_object(self):        
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs["comment_id"])
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user requesting the action is the same as the user object being retrieved
        if instance.author.id != request.user.id:
            return Response(
                data={"error": "You can only delete a comment created by you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().delete(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user requesting the action is the same as the user object being retrieved
        if instance.author.id != request.user.id:
            return Response(
                data={"error": "You can only update a comment created by you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context
    


class CommentsAPIView(ListCreateAPIView):
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description="Get comments and replies for a thread",
        manual_parameters=[
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                description="Order comments by 'newest', 'likes', or 'oldest'",
                type=openapi.TYPE_STRING,
                default="newest",
            ),
            openapi.Parameter(
                "thread_id",
                openapi.IN_QUERY,
                description="Filter comments by thread_id",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Create a comment or a reply of a comment for a thread",
        request_body=CreateCommentSerializer
    )
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCommentSerializer
        return CommentSerializer
    
    @swagger_auto_schema(
        operation_description="Create a comment for a thread",
        request_body=CreateCommentSerializer
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_queryset(self):
        try:
            thread = Thread.objects.get(id=self.request.query_params.get("thread_id"))
        except Thread.DoesNotExist:
            raise Http404("Thread does not exist")

        queryset = Comment.objects.filter(thread=thread)
        # Query param
         # Query param
        order_by = self.request.query_params.get("order_by", "created_at")
        # Order the queryset based on the query param
        if order_by == "likes":
            queryset = queryset.annotate(
            net_likes=F('num_likes') - F('num_dislikes')
            ).order_by('-net_likes', '-created_at')
        elif order_by == "newest":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("created_at")  # Order by most recent

        for comment in queryset:
            comment.replies = CommentReply.objects.filter(parent_comment=comment.id, thread=comment.thread.id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context

class DislikeCommentAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already disliked this comment
        vote, created = Vote.objects.get_or_create(
            user=user, comment=comment, vote_type="dislike"
        )

        if not created:
            # If the user had already disliked the comment, return a 409 Conflict response
            return Response(
                {"message": "The user has already disliked this comment"},
                status=status.HTTP_409_CONFLICT,
            )

        # If the user had previously liked this comment, delete the like
        existing_like = Vote.objects.filter(
            user=user, comment=comment, vote_type="like"
        ).first()
        if existing_like:
            existing_like.delete()

        # Update the comment with the num_likes without updating the updated_at field
        dislikes = Vote.objects.filter(comment=comment, vote_type="dislike").count()
        likes = Vote.objects.filter(comment=comment, vote_type="like").count()
        Comment.objects.filter(id=comment_id).update(
            num_dislikes=dislikes, num_likes=likes
        )

        # Serialize the dislike data
        dislike_data = {
            "id": vote.id,
            "user": vote.user.id,
            "comment": vote.comment.id,
            "vote_type": vote.vote_type,
        }
        return Response(dislike_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already disliked this comment
        try:
            dislike = Vote.objects.get(user=user, comment=comment, vote_type="dislike")
        except Vote.DoesNotExist:
            return Response(
                {"message": "The user has not disliked this comment"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if dislike:
            # If the user has already disliked the comment, delete the Dislike
            dislike.delete()
            # Update the comment with the num_likes without updating the updated_at field
            dislikes = Vote.objects.filter(comment=comment, vote_type="dislike").count()
            Comment.objects.filter(id=comment_id).update(num_dislikes=dislikes)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        
class LikeCommentAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already liked this comment
        vote, created = Vote.objects.get_or_create(
            user=user, comment=comment, vote_type="like"
        )

        if not created:
            # If the user had already liked the comment, return a 409 Conflict response
            return Response(
                {"message": "The user has already liked this comment"},
                status=status.HTTP_409_CONFLICT,
            )

        # If the user had previously disliked this comment, delete the dislike
        existing_dislike = Vote.objects.filter(
            user=user, comment=comment, vote_type="dislike"
        ).first()
        if existing_dislike:
            existing_dislike.delete()

        # Update the comment with the num_likes without updating the updated_at field
        likes = Vote.objects.filter(comment=comment, vote_type="like").count()
        dislikes = Vote.objects.filter(comment=comment, vote_type="dislike").count()
        Comment.objects.filter(id=comment_id).update(
            num_likes=likes, num_dislikes=dislikes
        )

        # Serialize the like data
        like_data = {
            "id": vote.id,
            "user": vote.user.id,
            "comment": vote.comment.id,
            "vote_type": vote.vote_type,
        }
        return Response(like_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already liked this comment
        try:
            like = Vote.objects.get(user=user, comment=comment, vote_type="like")
        except Vote.DoesNotExist:
            return Response(
                {"message": "The user has not liked this comment"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if like:
            # If the user has already liked the comment, delete the Like
            like.delete()
            # Update the comment with the num_likes without updating the updated_at field
            likes = Vote.objects.filter(comment=comment, vote_type="like").count()
            Comment.objects.filter(id=comment_id).update(num_likes=likes)
            return Response(status=status.HTTP_204_NO_CONTENT)


class CommentReplyDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = CommentReply.objects.all()
    serializer_class = CommentReplySerializer
    #lookup_field = "thread_id"
    #lookup_field = "comment_id"
    lookup_field = "commentreply_id"
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return EditCommentReplySerializer
        return super().get_serializer_class()
    
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs["commentreply_id"])
        return obj
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user requesting the action is the same as the user object being retrieved
        if instance.author.id != request.user.id:
            return Response(
                data={"error": "You can only delete a reply created by you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().delete(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user requesting the action is the same as the user object being retrieved
        if instance.author.id != request.user.id:
            return Response(
                data={"error": "You can only update a reply created by you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


class LikeCommentReplyAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        commentreply_id = self.kwargs.get("commentreply_id")
        try:
            commentreply = CommentReply.objects.get(id=commentreply_id)
        except CommentReply.DoesNotExist:
            return Response(
                {"message": "Comment reply does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already liked this comment reply
        vote, created = Vote.objects.get_or_create(
            user=user, reply=commentreply, vote_type="like"
        )

        if not created:
            # If the user had already liked the comment reply, return a 409 Conflict response
            return Response(
                {"message": "The user has already liked this comment reply"},
                status=status.HTTP_409_CONFLICT,
            )

        # If the user had previously disliked this comment reply, delete the dislike
        existing_dislike = Vote.objects.filter(
            user=user, reply=commentreply, vote_type="dislike"
        ).first()
        if existing_dislike:
            existing_dislike.delete()

        # Update the comment reply with the num_likes without updating the updated_at field
        likes = Vote.objects.filter(reply=commentreply, vote_type="like").count()
        dislikes = Vote.objects.filter(reply=commentreply, vote_type="dislike").count()
        CommentReply.objects.filter(id=commentreply_id).update(
            num_likes=likes, num_dislikes=dislikes
        )

        # Serialize the like data
        like_data = {
            "id": vote.id,
            "user": vote.user.id,
            "reply": vote.reply.id,
            "vote_type": vote.vote_type,
        }
        return Response(like_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        commentreply_id = self.kwargs.get("commentreply_id")
        try:
            commentreply = CommentReply.objects.get(id=commentreply_id)
        except CommentReply.DoesNotExist:
            return Response(
                {"message": "Comment reply does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already liked this comment reply
        try:
            like = Vote.objects.get(user=user, reply=commentreply, vote_type="like")
        except Vote.DoesNotExist:
            return Response(
                {"message": "The user has not liked this comment reply"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if like:
            # If the user has already liked the comment reply, delete the Like
            like.delete()
            # Update the comment reply with the num_likes without updating the updated_at field
            likes = Vote.objects.filter(reply=commentreply, vote_type="like").count()
            CommentReply.objects.filter(id=commentreply_id).update(num_likes=likes)
            return Response(status=status.HTTP_204_NO_CONTENT)


class DislikeCommentReplyAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        commentreply_id = self.kwargs.get("commentreply_id")
        try:
            commentreply = CommentReply.objects.get(id=commentreply_id)
        except CommentReply.DoesNotExist:
            return Response(
                {"message": "Comment reply does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already disliked this comment reply
        vote, created = Vote.objects.get_or_create(
            user=user, reply=commentreply, vote_type="dislike"
        )

        if not created:
            # If the user had already disliked the comment reply, return a 409 Conflict response
            return Response(
                {"message": "The user has already disliked this comment reply"},
                status=status.HTTP_409_CONFLICT,
            )

        # If the user had previously liked this comment reply, delete the like
        existing_like = Vote.objects.filter(
            user=user, reply=commentreply, vote_type="like"
        ).first()
        if existing_like:
            existing_like.delete()

        # Update the comment reply with the num_likes without updating the updated_at field
        dislikes = Vote.objects.filter(reply=commentreply, vote_type="dislike").count()
        likes = Vote.objects.filter(reply=commentreply, vote_type="like").count()
        CommentReply.objects.filter(id=commentreply_id).update(
            num_dislikes=dislikes, num_likes=likes
        )

        # Serialize the dislike data
        dislike_data = {
            "id": vote.id,
            "user": vote.user.id,
            "reply": vote.reply.id,
            "vote_type": vote.vote_type,
        }
        return Response(dislike_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        commentreply_id = self.kwargs.get("commentreply_id")
        try:
            commentreply = CommentReply.objects.get(id=commentreply_id)
        except CommentReply.DoesNotExist:
            return Response(
                {"message": "Comment reply does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        user = request.user

        # Check if the user has already disliked this comment reply
        try:
            dislike = Vote.objects.get(user=user, reply=commentreply, vote_type="dislike")
        except Vote.DoesNotExist:
            return Response(
                {"message": "The user has not disliked this comment reply"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if dislike:
            # If the user has already disliked the comment reply, delete the Dislike
            dislike.delete()
            # Update the comment reply with the num_likes without updating the updated_at field
            dislikes = Vote.objects.filter(reply=commentreply, vote_type="dislike").count()
            CommentReply.objects.filter(id=commentreply_id).update(num_dislikes=dislikes)
            return Response(status=status.HTTP_204_NO_CONTENT)


class SearchResultsAPIView(ListAPIView):
    serializer_class = SearchSerializer
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="query",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search threads and links by title and body",
                required=True
            ),
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                description="Order threads by 'created_at', 'points', or 'num_comments'",
                type=openapi.TYPE_STRING,
                default="created_at",
            )
        ],
        responses={
            200: SearchSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        query = self.request.GET.get("query", "").strip()
        if not query:
            return Thread.objects.none()
        
        # Realiza la búsqueda
        threads = Thread.objects.filter(
            title__icontains=query
        ) | Thread.objects.filter(body__icontains=query)
        
        # Obtén la opción de ordenación de los parámetros de la solicitud
        order_by = self.request.query_params.get("order_by", "created_at")
        
        # Aplica la ordenación basada en el parámetro order_by
        if order_by == "points":
            threads = threads.order_by("-num_points")
        elif order_by == "num_comments":
            threads = threads.order_by("-num_comments")
        else:
            threads = threads.order_by("-created_at")  # Ordenar por lo más reciente por defecto
        
        return threads
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user if self.request.user.is_authenticated else None
        return context