from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Movie
from .forms import MovieEditForm, MovieForm


def _home_context(request, form):
    movies = Movie.objects.filter(user=request.user)

    return {
        'movies': movies,
        'form': form,
        'total_titles': movies.count(),
        'completed_count': movies.filter(status='Completed').count(),
        'watching_count': movies.filter(status='Watching').count(),
        'plan_count': movies.filter(status='Plan to Watch').count(),
    }


@login_required
def index(request):
    return render(
        request,
        'Inventory/home.html',
        _home_context(request, MovieForm()),
    )


@login_required
def add(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)

        if form.is_valid():
            movie = form.save(commit=False)
            movie.user = request.user
            movie.save()

            return redirect('index')

    else:
        form = MovieForm()

    return render(
        request,
        'Inventory/home.html',
        _home_context(request, form),
    )


@login_required
def edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MovieEditForm(request.POST, instance=movie)

        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = MovieEditForm(instance=movie)

    return render(
        request,
        'Inventory/edit_title.html',
        {'form': form, 'movie': movie},
    )


@login_required
@require_POST
def delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk, user=request.user)
    movie.delete()
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('index')

    else:
        form = UserCreationForm()

    return render(request, 'Inventory/signup.html', {'form': form})