from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .forms import MovieEditForm, MovieForm
from .models import Movie


class MovieCollectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-user',
            password='test-password',
        )
        self.client.login(username='test-user', password='test-password')

    def test_status_field_has_available_choices(self):
        form = MovieForm()

        self.assertEqual(
            list(form.fields['status'].choices)[1:],
            [
                ('Plan to Watch', 'Plan to Watch'),
                ('Watching', 'Watching'),
                ('Completed', 'Completed'),
            ],
        )

    def test_rating_is_a_clickable_choice_between_one_and_ten(self):
        form = MovieForm()

        self.assertEqual(
            form.fields['rating'].widget.__class__.__name__,
            'Select',
        )
        self.assertEqual(form.fields['rating'].choices[0], ('1.0', '1'))
        self.assertEqual(form.fields['rating'].choices[-1], ('10.0', '10'))
        self.assertNotIn('0.0', dict(form.fields['rating'].choices))
        self.assertNotIn('10.5', dict(form.fields['rating'].choices))

    def test_added_title_appears_in_both_collection_sections(self):
        response = self.client.post(
            reverse('add'),
            {
                'title': 'Example Title',
                'type': 'Movie',
                'genre': 'Drama',
                'country': 'Japan',
                'release_year': '2024',
                'status': 'Watching',
                'rating': '8.5',
                'episodes': '1',
                'description': '',
            },
        )

        self.assertRedirects(response, reverse('index'))
        self.assertTrue(
            Movie.objects.filter(
                user=self.user,
                title='Example Title',
                release_year=2024,
                status='Watching',
            ).exists()
        )

        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Example Title', count=2)

    def test_invalid_submission_keeps_add_form_visible(self):
        response = self.client.post(
            reverse('add'),
            {
                'title': 'Incomplete Title',
                'type': 'Movie',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'showAdd();')

    def test_plan_to_watch_title_can_be_saved_without_rating(self):
        response = self.client.post(
            reverse('add'),
            {
                'title': 'Upcoming Movie',
                'type': 'Movie',
                'genre': 'Adventure',
                'country': 'Japan',
                'release_year': '2025',
                'status': 'Plan to Watch',
                'episodes': '12',
                'description': '',
            },
        )

        self.assertRedirects(response, reverse('index'))
        movie = Movie.objects.get(title='Upcoming Movie', user=self.user)
        self.assertIsNone(movie.rating)
        self.assertEqual(movie.episodes, 0)

    def test_collection_title_opens_an_edit_form(self):
        movie = Movie.objects.create(
            user=self.user,
            title='Editable Title',
            type='Series',
            genre='Drama',
            country='Japan',
            release_year=2024,
            status='Watching',
            rating='8.0',
            episodes=12,
        )

        response = self.client.get(reverse('edit', args=[movie.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EDIT TITLE DETAILS')
        self.assertContains(response, 'Save Changes')
        self.assertContains(response, 'value="Editable Title"')
        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="rating"')
        self.assertContains(response, 'Delete this title?')
        self.assertContains(response, 'Yes, Delete')
        self.assertContains(response, 'Keep Title')
        self.assertContains(response, 'will be permanently removed from your collection.')
        self.assertEqual(
            list(MovieEditForm().fields),
            ['title', 'status', 'rating'],
        )

    def test_editing_a_title_updates_its_saved_values(self):
        movie = Movie.objects.create(
            user=self.user,
            title='Original Title',
            type='Series',
            genre='Drama',
            country='Japan',
            release_year=2024,
            status='Watching',
            rating='8.0',
            episodes=12,
        )

        response = self.client.post(
            reverse('edit', args=[movie.pk]),
            {
                'title': 'Updated Title',
                'status': 'Plan to Watch',
            },
        )

        self.assertRedirects(response, reverse('index'))
        movie.refresh_from_db()
        self.assertEqual(movie.title, 'Updated Title')
        self.assertEqual(movie.episodes, 12)
        self.assertEqual(movie.status, 'Plan to Watch')
        self.assertIsNone(movie.rating)

    def test_delete_removes_owned_title(self):
        movie = Movie.objects.create(
            user=self.user,
            title='Title to Delete',
            type='Movie',
            genre='Drama',
            country='Japan',
            release_year=2024,
            status='Completed',
            rating='8.0',
            episodes=0,
        )

        response = self.client.post(reverse('delete', args=[movie.pk]))

        self.assertRedirects(response, reverse('index'))
        self.assertFalse(Movie.objects.filter(pk=movie.pk).exists())

    def test_delete_cannot_remove_another_users_title(self):
        another_user = User.objects.create_user(
            username='another-user',
            password='test-password',
        )
        movie = Movie.objects.create(
            user=another_user,
            title='Another User Title',
            type='Movie',
            genre='Drama',
            country='Japan',
            release_year=2024,
            status='Completed',
            rating='8.0',
            episodes=0,
        )

        response = self.client.post(reverse('delete', args=[movie.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Movie.objects.filter(pk=movie.pk).exists())
