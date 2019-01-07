from django.contrib import admin
from .models import Issue, Response, Category, Document

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'snippet')


admin.site.register(Issue)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Category)
admin.site.register(Document)