"""
This module contains the views for the magazine app.
"""

from django.shortcuts import render, get_object_or_404, redirect
from .models import Magazine
from .forms import CreateMagazineForm
from threads.models import Thread
from django.contrib.auth.decorators import login_required
# Views handle HTTP requests and return appropriate responses
from .models import Subscription

# View for displaying the list of magazines
def magazines(request):
    """
    This view displays the list of magazines. It allows the user to order the magazines by the number of threads or comments.
    """
    if request.user.is_authenticated:
        user_subscriptions = Subscription.objects.filter(user=request.user).values_list('magazine_id', flat=True)
    else:
        user_subscriptions = []
    # Get the 'orderby' parameter from the URL
    orderby_param = request.GET.get("orderby")

    # Get all the magazines
    magazines = Magazine.objects.all()  # pylint: disable=no-member

    # Order the magazines by subscription count by default
    magazines = magazines.order_by("-subscriptions_count")

    # If the 'orderby' parameter is provided in the URL, reorder the magazines according to the given parameter
    if orderby_param == "threads":
        magazines = magazines.order_by("-threads_count")
    elif orderby_param == "comments":
        magazines = magazines.order_by("-comments_count")

    # Render the 'magazines.html' template with the list of magazines
    return render(request, "magazines.html", {"magazines": magazines, "user_subscriptions": user_subscriptions})


@login_required
def create_magazine(request):
    if request.method == "POST":
        # If the request is POST, try to process the form
        form = CreateMagazineForm(request.POST)
        if form.is_valid():
            # If the form is valid, save the new magazine to the database
            magazine = form.save(commit=False)
            magazine.author = request.user
            magazine.save()
            
            # Redirect to a specific view after saving the magazine
            return redirect("magazines")
    else:
        # If the request is GET, show an empty form to create a new magazine
        form = CreateMagazineForm()
    return render(request, "create_magazine.html", {"form": form})


@login_required
def subscribe_to_magazine(request, magazine_id):
    # Obtener la revista correspondiente según el ID proporcionado
    magazine = get_object_or_404(Magazine, id=magazine_id)
    
    # Verificar si el usuario ya está suscrito a la revista
    subscription_exists = Subscription.objects.filter(user=request.user, magazine=magazine).exists()
    
    # Si el usuario no está suscrito a la revista, crear una suscripción
    if not subscription_exists:
        subscription = Subscription(user=request.user, magazine=magazine)
        subscription.save()
        
        # Incrementar el contador de suscripciones de la revista y guardarlo
        magazine.subscriptions_count += 1
        magazine.save()
    
    # Obtener la URL actual desde el formulario de suscripción
    current_url = request.POST.get("current_url", "/")
    
    # Redirigir a la URL actual después de procesar la suscripción
    return redirect(current_url)


@login_required
def unsubscribe_from_magazine(request, magazine_id):
    # Get the corresponding magazine based on the provided ID
    magazine = get_object_or_404(Magazine, id=magazine_id)
    
    # Buscar la suscripción del usuario a esta revista
    
    subscription = Subscription.objects.filter(user=request.user, magazine=magazine).first()
    
    # Si el usuario está suscrito a la revista, eliminar la suscripción
    if subscription:
        subscription.delete()
        # Decrementar el contador de suscripciones de la revista y guardarlo
        magazine.subscriptions_count = magazine.subscriptions_count - 1
        magazine.save()
    
    # Obtener la URL actual del formulario de desuscripción
    current_url = request.POST.get("current_url", "/")
    
    # Redireccionar a la URL actual después de procesar la desuscripción
    return redirect(current_url)

def get_filtered_queryset(request, magazine):
    queryset = Thread.objects.filter(magazine=magazine)

    filter_option = request.GET.get("filter", "all")
    order_by = request.GET.get("order_by", "created_at")

    if filter_option == "threads":
        queryset = queryset.filter(url__isnull=True)
    elif filter_option == "links":
        queryset = queryset.exclude(url__isnull=True)

    if order_by == "points":
        queryset = queryset.order_by("-num_points")
    elif order_by == "num_comments":
        queryset = queryset.order_by("-num_comments")
    else:
        queryset = queryset.order_by("-created_at")

    # Guardar los valores de filtro y orden en la sesión del usuario
    request.session["filter"] = filter_option
    request.session["order_by"] = order_by

    return queryset

def magazine_threads(request,magazine_id):

    magazine = get_object_or_404(Magazine, id=magazine_id)

    threads = get_filtered_queryset(request,magazine)
    if request.user.is_authenticated:
        user_subscriptions = Subscription.objects.filter(user=request.user).values_list('magazine_id', flat=True)
    else:
        user_subscriptions = []
    
    filter_option = request.session.get("filter", "all")
    order_by = request.session.get("order_by", "created_at")
    
    return render(request, "magazine_threads.html", {"magazine": magazine, 'threads': threads, 'active_filter': filter_option, 'active_order': order_by, "user_subscriptions": user_subscriptions})