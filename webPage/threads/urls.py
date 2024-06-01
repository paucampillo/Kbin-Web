"""
URL configuration for webPage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from threads import views, apis
from django.urls import path, re_path
from magazine import views as Magazine_views

urlpatterns = [
    path("", views.ThreadListView.as_view(), name="home"),
    path("threads/", views.ThreadListView.as_view(), name="thread_list"),
    path("new_link/", views.CreateLink.as_view(), name="link_create"),
    path("new_thread/", views.CreateThread.as_view(), name="thread_create"),
    path(
        "threads_links/<int:pk>/edit/",
        views.UpdateThreadAndLink.as_view(),
        name="thread_link_edit",
    ),
    path(
        "thread/<int:pk>/delete/",
        views.DeleteThreadOrLink.as_view(),
        name="thread_link_delete",
    ),
    path("thread/<int:pk>/vote/", views.vote_thread, name="thread_vote"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("search/results/", views.SearchResultsView.as_view(), name="search_results"),
    path("thread/<int:pk>/boost/", views.boost_thread, name="thread_boost"),
    path("thread/<int:pk>/", views.ThreadDetailView.as_view(), name="thread_detail"),
    path(
        "thread/<int:thread_id>/comment/create/",
        views.CreateComment.as_view(),
        name="create_comment",
    ),
    path("comment/<int:pk>/vote/", views.vote_comment, name="comment_vote"),
    path(
        "threads/<int:thread_id>/comment/<int:pk>/edit/",
        views.UpdateComment.as_view(),
        name="comment_edit",
    ),
    path(
        "comment/<int:pk>/delete/<int:thread_id>/",
        views.DeleteComment.as_view(),
        name="comment_delete",
    ),
    re_path(
        r"^threads/(?P<thread_id>\d+)/comment/(?P<pk>\d+)/reply/(?:(?P<parent_reply_id>\d+)/)?$",
        views.ReplyCommentView.as_view(),
        name="reply_comment",
    ),
    path("reply/<int:pk>/vote/", views.vote_reply, name="reply_vote"),
    path(
        "threads/<int:thread_id>/comment/<int:pk>/reply/<int:parent_reply_id>/edit/",
        views.UpdateReply.as_view(),
        name="reply_edit",
    ),
    path(
        "threads/<int:thread_id>/comment/<int:pk>/reply/<int:parent_reply_id>/delete/",
        views.DeleteReply.as_view(),
        name="reply_delete",
    ),
    path(
        "magazine/<int:magazine_id>/",
        Magazine_views.magazine_threads,
        name="magazine_threads_list",
    ),
]

urlpatterns += [
    path("api/threads/", apis.ThreadsAPIView.as_view(), name="threads_api"),
    path(
        "api/threads/<int:thread_id>/",
        apis.ThreadDetailAPIView.as_view(),
        name="thread_detail_api",
    ),
    path(
        "api/threads/<int:thread_id>/boosts/",
        apis.BoostAPIView.as_view(),
        name="thread_boost_api",
    ),
    path(
        "api/threads/<int:thread_id>/likes/",
        apis.LikeAPIView.as_view(),
        name="thread_like_api",
    ),
    path(
        "api/threads/<int:thread_id>/dislikes/",
        apis.DislikeAPIView.as_view(),
        name="thread_dislike_api",
    ),
    
    path("api/comments/", apis.CommentsAPIView.as_view(), name="comments_api"),
    path(
        "api/comments/<int:comment_id>/",
        apis.CommentDetailAPIView.as_view(),
        name="comment_detail_api",
    ),
    path(
        "api/comments/<int:comment_id>/likes/",
        apis.LikeCommentAPIView.as_view(),
        name="comment_like_api",
    ),
    path(
        "api/comments/<int:comment_id>/dislikes/",
        apis.DislikeCommentAPIView.as_view(),
        name="comment_dislike_api",
    ),

    path(
        "api/replies/<int:commentreply_id>/",
        apis.CommentReplyDetailAPIView.as_view(),
        name="replies_detail_api"
    ),
    path(
        "api/replies/<int:commentreply_id>/likes/",
        apis.LikeCommentReplyAPIView.as_view(),
        name="reply_like_api",
    ),
    path(
        "api/replies/<int:commentreply_id>/dislikes/",
        apis.DislikeCommentReplyAPIView.as_view(),
        name="reply_dislike_api",
    ),
        
    path("api/search/", apis.SearchResultsAPIView.as_view(), name="search_results_api"),

]