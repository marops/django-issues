import datetime

from django.test import TestCase
from django.utils import timezone

from issues.forms import IssueForm


class IssueFormTest(TestCase):
    def test_initial(self):
        form = IssueForm()
        # self.assertTrue(
        #     form.fields['renewal_date'].label == None or form.fields['renewal_date'].label == 'renewal date')
