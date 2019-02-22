from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Issue, Response, Category, Document
from django.utils import timezone
from .forms import IssueForm, ResponseForm, IssueNewForm
from django.core.files.storage import default_storage
from os import path
from django.db.models import Count
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .decorators import group_required
from django.contrib.auth.models import User, Group
from django.utils.html import escape
from django.db.models import Q

@login_required
def index(request):
    is_manager=request.user.is_staff | request.user.is_superuser | request.user.groups.filter(name="engineers").exists()

    #If manager the ngo to dashboard
    if is_manager:
        return HttpResponseRedirect(reverse('issues:dashboard'))
    else:
        #if non manager go to the list of the logged in user
        return HttpResponseRedirect(reverse('issues:list'))

    return render(request,'issues/index.html')

@group_required('engineer')
def test(request):
    is_engineer = request.user.groups.filter(name='engineers').exists()
    msg=f'is_engineer={is_engineer}'
    return render(request,'issues/test.html', {'is_engineer':is_engineer})

@login_required
def dashboard(request):
    sql="select i.id, i.category_id,c.name,count(*) from issues_issue i left join issues_category c on i.category_id=c.id where not i.completed group by c.name"

    my_issues=Issue.objects.filter(Q(assigned_to=request.user.id)|Q(submitted_by=request.user.id)&Q(completed=False)).count()
    open_issues=Issue.objects.filter(completed=False).count()
    open_issues_by_category = Issue.objects.filter(completed=False).values('category__name').annotate(total=Count('category'))
    unassigned_issues=Issue.objects.filter(completed=False).filter(assigned_to=None).count()

    return render(request, 'issues/dashboard.html', {'my_issues':my_issues,'open_issues':open_issues,'unassigned_issues':unassigned_issues})

@login_required
def issues_list(request):
    title="Open Issues"
    f=request.GET.get('f',None)

    is_manager=request.user.is_staff | request.user.is_superuser | request.user.groups.filter(name="engineers").exists()

    filter = ""

    if is_manager:

        if not f:
            f='mine'

        if f=='mine':   #show issues assigned to user
            filter+=f'assigned_to={request.user.id}&submitted_by={request.user.id}'
            title="My Issues"

        if f=='ua':
            filter+=f'assigned_to=0&completed=0'
            title="Unassigned Issues"

        if f=='oi':
            filter+=f'completed=0'
            title="Open Issues"

        #Default for manager is to only show not completed
        # if f=='completed':
        # if len(filter) > 0:
        #     filter="&"
        # #filter+="{}={}".format('completed', 0)
        #title="Completed Issues"

    else:
        filter += f"submitted_by={request.user.id}"
        title = "My Issues"

    if len(filter)>0:
        filter="?"+filter

    template_name = 'issues/list.html'
    headers=['Issue#','Short_Desc','Category','Created','Submitted By','Assigned To','Completed']
    #s='{}{}{}'.format(request.META['HTTP_HOST'],reverse('issues-list-data'),filter,)
    s = '{}{}'.format(reverse('issues:list-data'), filter, )
    extra_context={'headers': headers,'ajax_url':s, 'title':title, 'is_manager':is_manager}

    #print(filter)

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
        return Issue.objects.all()

    def filter_queryset(self, qs):
        # simple example:
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(short_desc__istartswith=search)

        q0=Q()

        #submitted_by
        filter_submitted_by = self.request.GET.get('submitted_by', None)
        if filter_submitted_by:
            q0=q0|Q(submitted_by=filter_submitted_by)

        #assigned_to
        filter_assigned_to = self.request.GET.get('assigned_to', None)
        if filter_assigned_to:
            if filter_assigned_to == '0':
                filter_assigned_to=None
            q0=q0|Q(assigned_to__exact=filter_assigned_to)

        filter_completed = self.request.GET.get('completed', None)
        if filter_completed:
            if filter_completed == '1': #only completed
                q0 = q0 & Q(completed=True)
            else: #only not completed
                q0 = q0 & Q(completed=False)
            #otherwise it will show both

        # filter_submitted_by = self.request.GET.__contains__('submitted_by')
        # if filter_submitted_by:
        #     submitter=self.request.GET.get('submitted_by')
        #     if not submitter:
        #         submitter=self.request.user.id
        #     qs = qs.filter(submitted_by__exact=submitter)

        return qs.filter(q0)

    def render_column(self, row, column):
        """ Renders a column on a row. column can be given in a module notation eg. document.invoice.type
        """
        # try to find rightmost object
        obj = row
        parts = column.split('.')
        for part in parts[:-1]:
            if obj is None:
                break
            obj = getattr(obj, part)

        # try using get_OBJECT_display for choice fields
        if hasattr(obj, 'get_%s_display' % parts[-1]):
            value = getattr(obj, 'get_%s_display' % parts[-1])()
        else:
            value = getattr(obj, parts[-1], None)

        if value is None:
            value = self.none_string

        if self.escape_values:
            value = escape(value)

        # if value and hasattr(obj, 'get_absolute_url'):
        #     return '<a href="%s">%s</a>' % (obj.get_absolute_url(), value)
        return value




# class DTIssueListView(TemplateView):
#     template_name = 'issues/list3.html'
#     headers=['Issue#','Short_Desc','Category','Created','Submitted By','Assigned To','Completed']
#     extra_context={'headers': headers,'ajax_url':'/issues/list3/data'}

from .mail import new_issue_mail, new_issue_response_mail

@login_required
def issue_new(request):

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = IssueForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as requfrom django.core.mail import send_mailired
            rc=form.save()

            # mail to submitted_by and engineers
            new_issue_mail(request,rc)
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('issues:issue-detail',args=[rc.pk]))
    else:
        form = IssueNewForm(initial={'submitted_by': request.user})

    return render(request, 'issues/issue_new.html', {'form': form})


@group_required('engineers')
def issue_view(request,pk,action=None):
    """
    New, Edit or Delete an Issue

    :param request:
    :param pk: Issue primary key. If 0 then creates new Issue
    :param action: default None. ['new | delete' | None]
    :return: IssueForm, pk
    """

    success_url="/issues"
    pk=int(pk)

    is_engineer = request.user.groups.filter(name='engineers').exists()

    if(pk>0):
        instance = Issue.objects.get(pk=pk)
        success_url+=f'/{pk}'
    else:
        #instance = None
        return HttpResponseRedirect(reverse('issues:issue-new'))

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
            rc=form.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('issues:issue-detail', args=[rc.pk]))

    # if a GET (or any other method) we'll create a blank form
    else:
        if (action=="delete"):
            #instance = Person.objects.get(pk=pk)
            return render(request, 'ticket/confirm_delete.html', {'object': instance,'success_url':success_url})

        form = IssueForm(instance=instance)

    return render(request, 'issues/issue.html', {'form': form, 'rid':pk, 'action':action, 'is_engineer':is_engineer})

@login_required
def issue_detail(request, pk):
    """
    View an Issue, and able to add a new Response

    :param request:
    :param pk: primary key for the Issue
    :return:
    """
    can_edit = request.user.groups.filter(name='engineers').exists()

    issue = Issue.objects.get(pk=pk)

    #If there is POST data then a new Response was submitted
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

            #send email to author and (assigned_to or engineer group)
            new_issue_response_mail(request, issue, rs)

            #s='/issues/{}'.format(pk,)
            return HttpResponseRedirect(request.path)
        else:
            #TODO Form Validation Error Page
            return HttpResponseRedirect('/')
    else:
        issue_responses=issue.response_set.all()
        response_form=ResponseForm(initial={'author': request.user, 'issue':issue.id})

    return render(request, 'issues/detail.html', { 'object': issue, 'rid': pk,'issue_responses':issue_responses,'response_form':response_form, 'can_edit':can_edit })




#Other list possibilities - not currently used
def rest(request):
    # View code here...
    return render(request, 'issues/list2.html', {})
#
# from .tables import IssueTable
# from django_tables2 import RequestConfig
#
# def list3(request):
#     table = IssueTable(Issue.objects.all())
#     RequestConfig(request).configure(table)
#     return render(request, 'issues/list3.html', {'table': table})
#     #return render(request, 'issues/list3.html',  {'issues': Issue.objects.all()})

# class IssuesListView(ListView):
#
#     template_name = 'issues/list.html'
#     model = Issue
#     queryset= Issue.objects.all()
#     context_object_name = 'issues'
#     #paginate_by=10


# class IssueDetailView(DetailView):
#
#     model = Issue
#     template_name = 'issues/detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['now'] = timezone.now()
#         return context
#

from rest_framework import viewsets
#from .serializers import  IssueSerializer, ResponseSerializer, UserSerializer, GroupSerializer
from .serializers import  IssueSerializer, GroupSerializer

class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Issue.objects.all().order_by('-created_date')
    serializer_class = IssueSerializer

# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#
#
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer