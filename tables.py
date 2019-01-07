# tutorial/tables.py
import django_tables2 as tables
from .models import Issue

class IssueTable(tables.Table):
    class Meta:
        model = Issue
        template_name = 'django_tables2/bootstrap.html'
        fields = ('id','short_desc','created_date','submitted_by','assigned_to','due_date','completed_date')