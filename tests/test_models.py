from django.test import TestCase
from django.contrib.auth.models import User
from issues.models import Issue, Category, Response, Document
from django.conf import settings

class IssueTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Category(name="general").save()
        User.objects.create(username="todd")
        c=Category.objects.get(name="general")
        u=User.objects.get(username="todd")
        Issue.objects.create(category=c, short_desc="Short Desc", submitted_by=u)
        #print("TESTING MODELS")


    def setUp(self):
        #print("setUp: Run once for every test method to setup clean data.")
        login = self.client.login(username='todd', password='todd06')
        pass

    def test_instance(self):
        issue = Issue.objects.get(id=1)

        self.assertTrue(issue.created_date)
        self.assertTrue(issue.modified_date)
        self.assertEqual(issue.get_absolute_url(),'/issues/1/')

    def test_names(self):
        issue = Issue.objects.get(id=1)
        field_label = issue._meta.get_field('assigned_to').verbose_name
        self.assertEquals(field_label, 'assigned to')

    def test_reponse(self):
        """Create a response to Issue(id=1) and add a Document attachment"""
        issue = Issue.objects.get(id=1)
        Response(author=issue.submitted_by, issue=issue, text="R1.1").save()
        response=Response.objects.get(pk=1)
        self.assertEqual(response.id,1)
        self.assertEqual(response.issue.id,1)
        self.assertEqual(response.text,'R1.1')
        self.assertEqual(response.issue.submitted_by.username,'todd')
        Document(file="manage.py",response_id=response).save()
        document=Document.objects.get(response_id=response)
        self.assertEqual(document.id,1)
        self.assertEqual(document.file,'manage.py')


    # Store configuration file values






    # def test_false_is_false(self):
    #     print("Method: test_false_is_false.")
    #     self.assertFalse(False)
    #
    # def test_false_is_true(self):
    #     print("Method: test_false_is_true.")
    #     self.assertTrue(True)
    #
    # def test_one_plus_one_equals_two(self):
    #     print("Method: test_one_plus_one_equals_two.")
    #     self.assertEqual(1 + 1, 2)