from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from issues.models import Issue, Category, Response
from issues.forms import IssueForm, ResponseForm
from django.core import mail

class IssueTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Category(id=1,name="general").save()
        u=User.objects.create_superuser(username="todd",email="murphyrt@leidos.com", password="Lidar")
        Group(name="engineers").save()
        g=Group.objects.get(name='engineers')
        u.groups.add(g)

        #add another user into engineers group
        u=User.objects.create_user(username="ernie",email="hr3dt@leidos.com", password="Lidar")
        u.groups.add(g)

        #print(f'ENGINEERS GROUP:{g.user_set.all()}')

        # c=Category.objects.get(name="general")
        # u=User.objects.get(username="todd")
        # #print(f'USER:{u.id},{u.is_staff}')
        # number_of_issues = 3
        #
        # for issue_id in range(number_of_issues):
        #     Issue.objects.create(
        #         id=issue_id+1,
        #         short_desc=f'Test {issue_id}',
        #         category=c,
        #         submitted_by=u
        #     )

    def setUp(self):
        #login = self.client.login(username='todd', password='Lidar')
        pass

    def test_new_issue(self):
        """
        Tests entering a new issue

        Requirements:
            * restricted to logged in
            * subset of model fields

        :return:
        """
        c=Category.objects.get(name="general")
        u=User.objects.get(username="todd")

        login = self.client.login(username='todd', password='Lidar')
        data={'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id}
        form = IssueForm(data)
        self.assertTrue(form.is_valid(),form.errors.as_json())

        response = self.client.post('/issues/new/', data)
        #must be in engineers group or is_staff or is_superuser

        self.assertRegex(response.url,r"^\/issues\/\d*\/")
        issue=Issue.objects.get(short_desc="Test1")


        # data={'author':u.id,'issue':issue.id,'text':'Test1.1'}
        # form=ResponseForm(data)
        # self.assertTrue(form.is_valid(),form.errors.as_json())
        #
        # response = self.client.post(f'/issues/{issue.pk}/',data)
        # issue_response=Response.objects.get(text='Test1.1')
        # self.assertRedirects(response, f'/issues/{issue.pk}/')
        #
        # response = self.client.get(f'/issues/{issue.pk}/')
        # print(f'RESPONSE2:{response}')
        #
        # #check email sent, should be

        self.assertEqual(len(mail.outbox), 1)
        mc=[]
        for m in mail.outbox:
            mc.append(f'{m.to}, {m.subject}')
            
        print(f'EMAILS: (Issue ID {issue.id}) {mc}')


    def test_issue_editing_is_restricted(self):
        """
        This tests that an issue can only be edited by one group engineers, is_staff, or is_superuser
        """
        u=User.objects.create(username="guest",email="guest@leidos.com", password="Lidar")
        c=Category.objects.get(name="general")
        login = self.client.login(username='guest', password='Lidar')
        data={'short_desc': 'Guest1', 'desc': 'Guest 1 desc', 'submitted_by': u.id, 'category': c.id}
        issue = Issue.objects.create(short_desc='Guest1',submitted_by=u,category=c)
        response = self.client.post(f'/issues/{issue.pk}/')
        self.assertEquals(response.status_code,302, 'View should only be editable by group engineers, is_staff or is_superuser')



    def _test_redirect_if_not_logged_in(self):
        response = self.client.get('/issues/')
        self.assertRedirects(response, '/accounts/login/?next=/issues/')

    def _test_url_exists(self):
        login = self.client.login(username='todd', password='Lidar')
        response = self.client.get('/issues/')
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'todd')
        #Check the page was returned
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'issues/dashboard.html')


