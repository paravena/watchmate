from django.test import TestCase
import django


class DjangoVersionTest(TestCase):
    def test_django_is_lts_42(self):
        # Ensure we are running on Django 4.2.x LTS
        self.assertTrue(
            django.__version__.startswith("4.2"),
            msg=f"Expected Django 4.2.x LTS, found {django.__version__}",
        )
