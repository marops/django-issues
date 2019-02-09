from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from issues.models import Issue, Category

class IssueListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Category(name="general").save()
        User.objects.create(username="todd", password='pbkdf2_sha256$120000$XRhV7iZHkSdX$7NnAeauvHMIrXHORGf08Y5yOHQBnzh0rPeU7wN7xn6U=')
        c=Category.objects.get(name="general")
        u=User.objects.get(username="todd")

        number_of_issues = 3

        for issue_id in range(number_of_issues):
            Issue.objects.create(
                short_desc=f'Test {issue_id}',
                category=c,
                submitted_by=u
            )

    def setUp(self):
        #login = self.client.login(username='todd', password='todd06')
        pass

    def test_redirect_if_not_logged_in(self):
        response = self.client.get('/issues/')
        self.assertRedirects(response, '/accounts/login/?next=/issues/')

    def test_url_exists(self):
        login = self.client.login(username='todd', password='todd06')
        response = self.client.get('/issues/')

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'todd')
        #Check the page was returned
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'issues/dashboard.html')