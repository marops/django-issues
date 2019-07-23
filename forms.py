from django.forms import ModelForm
from .models import Document, Response
from django import forms
from django.conf import settings
from django.db import models


### ModelForms
from .models import Issue
from django.contrib.auth.models import User

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return f"{obj.last_name}, {obj.first_name} ({obj.username})"

class IssueForm(forms.ModelForm):
    #due_date=forms.DateField(required=False,widget=forms.TextInput(attrs={'type':'date'}))
    #completed_date=forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'type':'date'}))
    submitted_by = UserModelChoiceField(User.objects.all().order_by('last_name'))
    assigned_to = UserModelChoiceField(User.objects.all().order_by('last_name'), required=False)

    class Meta:
        model=Issue
        #fields=['headline','pub_date','content','reporter']
        exclude=['modified_date']

        widgets = {
            'metadata': forms.Textarea(attrs={'cols': '40', 'rows': '2'})
            #'metadata': JSONEditorWidget(attrs={'cols': '40', 'rows': '2'}, height="100%")
        }



class IssueNewForm(forms.ModelForm):
    #due_date=forms.DateField(required=False,widget=forms.TextInput(attrs={'type':'date'}))
    #completed_date=forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'type':'date'}))
    submitted_by = UserModelChoiceField(User.objects.all().order_by('last_name'))

    class Meta:
        model=Issue
        fields=['short_desc','category','desc','location','submitted_by']



class ResponseForm(ModelForm):
    #file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = Response
        exclude= []
        widgets = {
            'author': forms.HiddenInput(),
            'issue': forms.HiddenInput(),
            'date': forms.HiddenInput(),
        }


class DocumentForm(ModelForm):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = Document
        fields= ['title','file']

