from django.db import models
from django.conf import settings
from os import path
from django.core.files.storage import default_storage
import datetime

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
import pytz


# Create your models here.
class Category(models.Model): # The Category table name that inherits models.Model
	name = models.CharField(max_length=100, unique=True) #Like a varchar

	class Meta:
		verbose_name = ("Category")
		verbose_name_plural = ("Categories")

	def __str__(self):
		return self.name #name to be shown when called


class Issue(models.Model):
    short_desc = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    desc = models.TextField(blank=True, null=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='todo_created_by', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='issues_assigned_to', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True, )
    completed_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    modified_date = models.DateTimeField(blank=True, null=True)
    priority = models.PositiveIntegerField(default=1)
    resolution = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255,blank=True, null=True)

    # Has due date for an instance of this object passed?
    def overdue_status(self):
        "Returns whether the Tasks's due date has passed or not."
        if self.due_date and datetime.date.today() > self.due_date:
            return True

    def __str__(self):
        return self.short_desc

    # def get_absolute_url(self):
    #     return reverse('todo:task_detail', kwargs={'task_id': self.id, })

    # Auto-set the Task creation / completed date
    def save(self, **kwargs):
        # If Task is being marked complete, set the completed_date
        if self.completed:
            self.completed_date = datetime.datetime.now()

        self.modified_date = datetime.datetime.now(pytz.utc)
        super(Issue, self).save()

    def get_absolute_url(self):
        return reverse('issues:issue-detail', args=[str(self.id)])

    #class Meta:
        #ordering = ["created_date"]


class Response(models.Model):
    """
    Not using Django's built-in comments because we want to be able to save
    a comment and change task details at the same time. Rolling our own since it's easy.
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='response_author', on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    text = models.TextField(blank=True)

    def snippet(self):
        # Define here rather than in __str__ so we can use it in the admin list_display
        return "{date}: {author} - {snippet}...".format(date=self.date,author=self.author, snippet=self.text[:55])

    def __str__(self):
        return "{author} - {snippet}...".format(author=self.author, snippet=self.text[:55])


class Document(models.Model):
    """
    Model for files. These are uploaded files attached to an issue/response
    """
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    response_id = models.ForeignKey(Response, on_delete=models.CASCADE, blank=True, null=True)

    def snippet(self):
        # Define here rather than in __str__ so we can use it in the admin list_display
        fn=path.basename(self.file.path)
        return "{}".format(path.basename(self.file.path),)

    def __str__(self):
        return "{}".format(self.file,)

    def delete(self):
        super().delete()
        default_storage.delete(self.file)


