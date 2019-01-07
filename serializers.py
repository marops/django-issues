from .models import Issue, Response, Document, Category
from rest_framework import serializers
from django.contrib.auth.models import User, Group

class IssueSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(many=False)
    #submitted_by = serializers.StringRelatedField(many=False)
    submitted_by = serializers.CharField(source='submitted_by.username',read_only=True)
    assigned_to = serializers.StringRelatedField(many=False)

    class Meta:
        model = Issue
        fields = ('url','id','category','short_desc','created_date','due_date','completed_date','submitted_by','assigned_to')
        #exclude = ('category',)

class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Response
        fields = ('url', 'author','issue','date','text')

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name','last_name','email', 'groups')
        #exclude = ('permissions',)

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')