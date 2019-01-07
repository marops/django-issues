from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DeleteView, DetailView
from .models import Issue, Response, Category, Document
from django.utils import timezone
from .forms import IssueForm, ResponseForm
from django.core.files.storage import default_storage
from os import path
from django.contrib.auth.models import User, Group
from django.views.generic.base import TemplateView
from django.db.models import Count
from django.urls import reverse


def index(request):
    return render(request,'issues/index.html')

def test(request):
    return render(request,'issues/test.html')

def dashboard(request):
    sql="select i.id, i.category_id,c.name,count(*) from issues_issue i left join issues_category c on i.category_id=c.id where not i.completed group by c.name"

    my_open_issues=Issue.objects.filter(completed=False).filter(assigned_to=request.user.id).count()
    open_issues=Issue.objects.filter(completed=False).count()
    open_issues_by_category = Issue.objects.filter(completed=False).values('category__name').annotate(total=Count('category'))
    unassigned_open_issues=Issue.objects.filter(completed=False).filter(assigned_to=None).count()

    return render(request, 'issues/dashboard.html', {'my_open_issues':my_open_issues,'open_issues':open_issues,'unassigned_open_issues':unassigned_open_issues})

def issues_list(request):
    title="Open Issues"
    f=request.GET.get('f',None)

    filter = ""
    if f=='mine':   #show issues assigned to user
        filter+="{}={}".format('assigned_to', request.user.id)
        title="My Open Issues"

    if f=='ua':
        filter+="{}={}".format('assigned_to', 0)
        title="Unassigned Issues"

    if f=='completed':
        filter+="{}={}".format('completed', 1)
        title="Completed Issues"

    if len(filter)>0:
        filter="?"+filter

    template_name = 'issues/list.html'
    headers=['Issue#','Short_Desc','Category','Created','Submitted By','Assigned To','Completed']
    #s='{}{}{}'.format(request.META['HTTP_HOST'],reverse('issues-list-data'),filter,)
    s = '{}{}'.format(reverse('issues:list-data'), filter, )
    extra_context={'headers': headers,'ajax_url':s, 'title':title}
    return render(request,template_name,extra_context)


### Datatables
from django_datatables_view.base_datatable_view import BaseDatatableView

class DTIssueListViewData(BaseDatatableView):
    model = Issue
    columns = ['id','short_desc','category','created_date','submitted_by','assigned_to','completed_date']
    #order_columns = ['id','category','created_date']
    max_display_length = 500
    #template_name = "myapp/datatableview.html"

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        return Issue.objects.filter(completed=False)

    def filter_queryset(self, qs):
        # simple example:
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(short_desc__istartswith=search)

        filter_assigned_to = self.request.GET.get('assigned_to', None)
        if filter_assigned_to:
            if filter_assigned_to == '0':
                filter_assigned_to=None
            qs = qs.filter(assigned_to__exact=filter_assigned_to)

        filter_completed = self.request.GET.get('completed', None)
        if filter_completed:
            qs = qs.filter(completed=True)
        else:
            qs = qs.filter(completed=False)


        return qs

# class DTIssueListView(TemplateView):
#     template_name = 'issues/list3.html'
#     headers=['Issue#','Short_Desc','Category','Created','Submitted By','Assigned To','Completed']
#     extra_context={'headers': headers,'ajax_url':'/issues/list3/data'}


def issue_view(request,pk,action=None):
    """

    :param request:
    :param pk: Issue primary key. If 0 then creates new Issue
    :param action: default None. ['delete' | None]
    :return: IssueForm, pk
    """

    success_url="/issues"
    pk=int(pk)

    if(pk>0):
        instance = Issue.objects.get(pk=pk)
    else:
        instance = None

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        if(action=='delete'):
            instance.delete()
            return HttpResponseRedirect(success_url)

        # create a form instance and populate it with data from the request:
        form = IssueForm(request.POST,instance=instance)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()

            # redirect to a new URL:
            return HttpResponseRedirect(success_url)

    # if a GET (or any other method) we'll create a blank form
    else:
        if(action=="delete"):
            #instance = Person.objects.get(pk=pk)
            return render(request, 'ticket/confirm_delete.html', {'object': instance,'success_url':success_url})

        form = IssueForm(initial={'submitted_by': request.user}, instance=instance)

    return render(request, 'issues/issue.html', {'form': form, 'rid':pk})

def issue_detail(request, pk):

    if request.method == 'POST':
        form = ResponseForm(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            rs=form.save()
            files=request.FILES.getlist('file')
            for f in files:
                #handle_uploaded_file(f,'files/')
                fn=path.join('docs',str(pk),f.name)
                fn=default_storage.save(fn,f)
                d = Document(file=fn,response_id=rs)
                d.save()

            #s='/issues/{}'.format(pk,)
            return HttpResponseRedirect(request.path)
        else:
            #TODO Form Validation Error Page
            return HttpResponseRedirect('/')
    else:
        issue=Issue.objects.get(pk=pk)
        issue_responses=issue.response_set.all()
        response_form=ResponseForm(initial={'author': request.user, 'issue':issue.id})

    return render(request, 'issues/detail.html', { 'object': issue, 'rid': pk,'issue_responses':issue_responses,'response_form':response_form })




#Other list possibilities - not currently used
def rest(request):
    # View code here...
    return render(request, 'issues/list2.html', {})

from .tables import IssueTable
from django_tables2 import RequestConfig

def list3(request):
    table = IssueTable(Issue.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'issues/list3.html', {'table': table})
    #return render(request, 'issues/list3.html',  {'issues': Issue.objects.all()})

# class IssuesListView(ListView):
#
#     template_name = 'issues/list.html'
#     model = Issue
#     queryset= Issue.objects.all()
#     context_object_name = 'issues'
#     #paginate_by=10


class IssueDetailView(DetailView):

    model = Issue
    template_name = 'issues/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


# from rest_framework import viewsets
# from .serializers import  IssueSerializer, ResponseSerializer, UserSerializer, GroupSerializer
#
# class IssueViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = models.Issue.objects.all().order_by('-created_date')
#     serializer_class = IssueSerializer
#
# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer