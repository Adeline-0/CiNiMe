from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):

    TYPE_CHOICES = [
        ('Movie', 'Movie'),
        ('Anime', 'Anime'),
        ('Series', 'Series'),
        ('Drama', 'Drama'),
    ]

    STATUS_CHOICES = [
        ('Plan to Watch', 'Plan to Watch'),
        ('Watching', 'Watching'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='movies',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    genre = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    release_year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    episodes = models.IntegerField(default=1)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title