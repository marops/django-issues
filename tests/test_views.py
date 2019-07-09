from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from issues.models import Issue, Category, Response, Location
from issues.forms import IssueForm, ResponseForm
from django.core import mail

class IssueTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Category(id=1,name="general").save()
        Category(id=2,name="LIDAR sensor").save()
        Category(id=3,name="EO sensor").save()
        u=User.objects.create_superuser(username="todd",email="murphyrt@leidos.com", password="Lidar")
        Group(name="engineers").save()
        g=Group.objects.get(name='engineers')
        u.groups.add(g)

        #add another user into engineers group
        u=User.objects.create_user(username="ernie",email="ernie@hr3d.leidos.com", password="Lidar")
        u.groups.add(g)

        #add another user into regular account. ie no group
        u=User.objects.create_user(username="oscar",email="oscar.@hr3d.leidos.com", password="Lidar")

        #Add a location
        Location(lid="Other",name="Other").save()


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
        loc=Location.objects.get(lid="Other")

        login = self.client.login(username='todd', password='Lidar')
        data={'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id, 'location':loc.lid}
        form = IssueForm(data)
        self.assertTrue(form.is_valid(),form.errors.as_json())

        response = self.client.post('/issues/new/', data)
        #must be in engineers group or is_staff or is_superuser

        self.assertRegex(response.url,r"^\/issues\/\d*\/")

        issue=Issue.objects.get(short_desc="Test1")

        self.assertEqual(len(mail.outbox), 1)

        #add a response
        data={'author':u.id,'issue':issue.id,'text':'Test1.1'}
        form=ResponseForm(data)
        self.assertTrue(form.is_valid(),form.errors.as_json())
        response = self.client.post(f'/issues/{issue.id}/', data)
        #print(f'RESPONSE:(IssueID {issue.id}, {response}')
        self.assertEqual(issue.response_set.all().count(),1)
        #print(f'ISSUE RESPONSE: {issue.response_set.all()}')

        self.assertEqual(len(mail.outbox),2)

        mc=[]
        for m in mail.outbox:
            mc.append(f'{m.to}, {m.subject}')

        #print(f'EMAILS: (Issue ID {issue.id}), (Response Count {issue.response_set.all().count()}), (Mail count {len(mc)}), {mc}')


    def test_new_issue_lidar(self):
        """
        Tests entering a new issue with a category of LIDAR

        Requirements:
            * restricted to logged in
            * subset of model fields
            * custom email for LIDAR

        :return:
        """
        c=Category.objects.get(name="LIDAR sensor")
        u=User.objects.get(username="todd")
        loc=Location.objects.get(lid="Other")

        login = self.client.login(username='todd', password='Lidar')
        data={'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id,'location':loc.lid}
        form = IssueForm(data)
        self.assertTrue(form.is_valid(),form.errors.as_json())

        response = self.client.post('/issues/new/', data)
        #must be in engineers group or is_staff or is_superuser

        self.assertRegex(response.url,r"^\/issues\/\d*\/")

        issue=Issue.objects.get(short_desc="Test1")

        self.assertEqual(len(mail.outbox), 1)
        # for m in mail.outbox:
        #     print(m.__dict__)
        #     print(f"EMAIL To:{m.to}\n Subject: {m.subject}\n{m.body}")


    def test_operater_new_issue(self):

        c = Category.objects.get(name="general")
        u = User.objects.get(username="oscar")
        loc=Location.objects.get(lid="Other")

        #login as oscar
        login = self.client.login(username='oscar', password='Lidar')

        #new issue
        data = {'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id, 'location':loc.lid}
        form = IssueForm(data)
        self.assertTrue(form.is_valid(),form.errors.as_json())

        response=self.client.post('/issues/new/',data)

        #print(f'TEST_OPERATOR RESPONSE:{response}')
        self.assertRegex(response.url,r"^\/issues\/\d*\/")
        issue=Issue.objects.get(short_desc="Test1")

        #check mail, addressed to oscar (submitted_by) and all in engineer group
        self.assertEqual(len(mail.outbox), 1)
        mc=[]
        for m in mail.outbox:
            mc.append(f'{m.to}, {m.subject}')
        #print(f'TEST_OPERATOR EMAILS: (Issue ID {issue.id}), (Submitted_by {issue.submitted_by}), {mc}')

        #assign to ernie
        issue.assigned_to=User.objects.get(username="ernie")
        issue.save()
        issue=Issue.objects.get(short_desc="Test1")
        #print(f'TEST OPERATOR SHOULD BE ERNIE {issue.assigned_to}')

        #add response
        #check mail should be addressed ro oscar and ernie


    def _test_view_issues_list(self):
        """
        This test the /issues/list view.

        1. Non managers (is_staff, is_superuser, in engineers group) list view should only show
        those items submitted by the logged in non manager.

        2. If manager is logged in /issues/list should show list of all open issues

        :return:
        """
        c = Category.objects.get(name="general")
        u = User.objects.get(username="oscar")

        #login as oscar
        login = self.client.login(username='oscar', password='Lidar')

        #new issue
        data = {'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id}
        form = IssueForm(data)
        form.save()

        #Non Manger logged in
        response=self.client.get('/issues/list/')
        #print(f'VIEW ISSUES (NON MGR): {response.content}')
        self.assertContains(response,'<h2>My Issues</h2>',html=True)
        self.assertContains(response, f'ajax": "/issues/list/data/?submitted_by={u.id}"')

        response=self.client.get(f'/issues/list/data/?assigned_to=2&submitted_by={u.id}')
        self.assertContains(response, '"recordsTotal": 1, "recordsFiltered": 1')

        #Manager Logged in
        u = User.objects.get(username="ernie")
        login = self.client.login(username='ernie', password='Lidar')

        #check My Issues which is default
        response=self.client.get('/issues/list/')
        #print(f'VIEW ISSUES (MGR): {response.content}')
        self.assertContains(response,'<h2>My Issues</h2>',html=True)
        self.assertContains(response, f'"ajax": "/issues/list/data/?assigned_to=2&amp;submitted_by={u.id}"')

        #Check unassigned issues
        response=self.client.get('/issues/list/?f=ua')
        self.assertContains(response,'<h2>Unassigned Issues</h2>',html=True)
        self.assertContains(response, f'"ajax": "/issues/list/data/?assigned_to=0&amp;completed=0"')

        #Check open issues
        response=self.client.get('/issues/list/?f=oi')
        self.assertContains(response,'<h2>Open Issues</h2>',html=True)
        self.assertContains(response, f'"ajax": "/issues/list/data/?completed=0"')

    def test_view_index(self):
        """
        Tests index

        1. Manger redirects to dashboard.
        2. Non Manager redirects to list. Lists logged in users submitted issues
        """

        #manager redirects to dashboard
        login = self.client.login(username='ernie', password='Lidar')
        response=self.client.get('/issues/')
        #print(f'VIEW INDEX (MGR): {response}')
        self.assertRedirects(response,"/issues/dashboard/")

        #non manager redirects to list of logged in submitted issues
        login = self.client.login(username='oscar', password='Lidar')
        response=self.client.get('/issues/')
        #print(f'VIEW INDEX (MGR): {response}')
        self.assertRedirects(response,"/issues/list/")


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



    def test_redirect_if_not_logged_in(self):
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


    def test_update_issue_completed(self):
        """
        Tests entering a new issue

        Requirements:
            * restricted to logged in
            * subset of model fields

        :return:
        """
        c=Category.objects.get(name="general")
        u=User.objects.get(username="todd")
        loc=Location.objects.get(lid="Other")

        login = self.client.login(username='todd', password='Lidar')
        data={'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id, 'location':loc.lid}
        form = IssueForm(data)
        self.assertTrue(form.is_valid(),form.errors.as_json())

        response = self.client.post('/issues/new/', data)
        #must be in engineers group or is_staff or is_superuser

        self.assertRegex(response.url,r"^\/issues\/\d*\/")

        issue=Issue.objects.get(short_desc="Test1")

        self.assertEqual(len(mail.outbox), 1)

        #mark record completed
        data = {'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id,'location': loc.lid,'completed':True}
        response = self.client.post(f'/issues/{issue.id}/edit/', data)

        self.assertEqual(len(mail.outbox),2)

        mc=[]
        for m in mail.outbox:
            mc.append(f'{m.to}, {m.subject}')

        # print(f'EMAILS: {mc[1]}')

