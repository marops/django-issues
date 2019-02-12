from django.forms import ModelForm
from .models import Document, Response
from django import forms

### ModelForms
from .models import Issue


class IssueForm(forms.ModelForm):
    #due_date=forms.DateField(required=False,widget=forms.TextInput(attrs={'type':'date'}))
    #completed_date=forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'type':'date'}))
    class Meta:
        model=Issue
        #fields=['headline','pub_date','content','reporter']
        exclude=['modified_date']


class IssueNewForm(forms.ModelForm):
    #due_date=forms.DateField(required=False,widget=forms.TextInput(attrs={'type':'date'}))
    #completed_date=forms.DateTimeField(required=False, widget=forms.TextInput(attrs={'type':'date'}))
    class Meta:
        model=Issue
        fields=['short_desc','category','desc','submitted_by']



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

