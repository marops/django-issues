from django.contrib import admin
from .models import Issue, Response, Category, Document

class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_desc', 'created_date', 'submitted_by','assigned_to')

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'snippet')


admin.site.register(Issue, IssueAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Category)
admin.site.register(Document)