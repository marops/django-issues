from django.contrib import admin
from .models import Issue, Response, Category, Document, Location

class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0

class ResponseInline(admin.StackedInline):
    model = Response
    extra = 0

class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_desc', 'created_date', 'submitted_by','assigned_to')
    inlines = [DocumentInline,ResponseInline]

class ResponseAdmin(admin.ModelAdmin):
    list_display = ('issue', 'author', 'date' )
    inlines=[DocumentInline]

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'lid', 'name')

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file','issue','response')
    search_fields = ['file']


admin.site.register(Issue, IssueAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Category)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Location, LocationAdmin)
