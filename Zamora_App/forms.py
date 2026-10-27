from django import forms
from decimal import Decimal
from .models import Movie


RATING_CHOICES = [
    (f'{Decimal(value) / 2:.1f}', f'{Decimal(value) / 2:g}')
    for value in range(2, 21)
]


class MovieForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=Decimal,
        required=False,
        widget=forms.Select(),
    )

    class Meta:
        model = Movie
        fields = [
            'title',
            'type',
            'genre',
            'country',
            'release_year',
            'status',
            'rating',
            'episodes',
            'description',
        ]

        widgets = {
            'title': forms.TextInput(),
            'type': forms.Select(),
            'genre': forms.TextInput(),
            'country': forms.TextInput(),
            'release_year': forms.NumberInput(),
            'status': forms.Select(),
            'episodes': forms.NumberInput(),
            'description': forms.Textarea(),
        } 

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('type') == 'Movie':
            cleaned_data['episodes'] = 0

        if cleaned_data.get('status') == 'Plan to Watch':
            cleaned_data['rating'] = None
        elif cleaned_data.get('rating') is None:
            self.add_error('rating', 'Enter a rating for a title you have watched.')

        return cleaned_data


class MovieEditForm(MovieForm):
    class Meta(MovieForm.Meta):
        fields = ['title', 'status', 'rating']