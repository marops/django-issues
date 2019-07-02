from django.test import TestCase
from django.contrib.auth.models import User, Group
from issues.models import Issue, Category, Response, Document, Location
from django.conf import settings
from issues.forms import IssueForm

class IssueTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Category(id=1,name="general").save()
        u=User.objects.create_superuser(username="todd",email="murphyrt@leidos.com", password="Lidar")
        Group(name="engineers").save()
        g=Group.objects.get(name='engineers')
        u.groups.add(g)

        #add another user into engineers group
        u=User.objects.create_user(username="ernie",email="ernie@hr3d.leidos.com", password="Lidar")
        u.groups.add(g)

        #add another user into regular account. ie no group
        u=User.objects.create_user(username="oscar",email="oscar.@hr3d.leidos.com", password="Lidar")

        #if using rest it will add the following to get_absolute_url, otherwise set to blank
        cls.rest="data/issues/"

        #Add a location
        Location(lid="Other",name="Other").save()

    def setUp(self):
        #print("setUp: Run once for every test method to setup clean data.")
        login = self.client.login(username='todd', password='Lidar')
        pass

    def test_instance(self):
        """
        Test for data returned by restframework

        :return:
        """
        u=User.objects.get(username="ernie")
        c=Category.objects.get(name="general")
        loc=Location.objects.get(lid="Other")

        #Create an issue
        data={'short_desc': 'Test1', 'desc': 'Test 1 desc', 'submitted_by': u.id, 'category': c.id, 'location':loc.lid}
        form = IssueForm(data)
        self.assertTrue(form.is_valid(),form.errors.as_json())
        form.save()

        issue = Issue.objects.get(short_desc="Test1")

        self.assertTrue(issue.created_date)
        self.assertTrue(issue.modified_date)

        self.assertEqual(issue.get_absolute_url(),f'/issues/{issue.id}/')


    # def test_reponse(self):
    #     """Create a response to Issue(id=1) and add a Document attachment"""
    #     issue = Issue.objects.get(id=1)
    #     Response(author=issue.submitted_by, issue=issue, text="R1.1").save()
    #     response=Response.objects.get(pk=1)
    #     self.assertEqual(response.id,1)
    #     self.assertEqual(response.issue.id,1)
    #     self.assertEqual(response.text,'R1.1')
    #     self.assertEqual(response.issue.submitted_by.username,'todd')
    #     Document(file="manage.py",response_id=response).save()
    #     document=Document.objects.get(response_id=response)
    #     self.assertEqual(document.id,1)
    #     self.assertEqual(document.file,'manage.py')

