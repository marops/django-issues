from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Issue, Response, Category, Document, Location
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
from taggit.models import Tag
from django.db import connection
from django.views.generic.base import TemplateView
import json
from django.utils.decorators import method_decorator


@login_required
def index(request):
    is_manager=request.user.is_staff | request.user.is_superuser | request.user.groups.filter(name="engineers").exists()

    #If manager the ngo to dashboard
    if is_manager:
        return HttpResponseRedirect(reverse('issues:dashboard'))
    else:
        #if non manager go to the list of the logged in user
        return HttpResponseRedirect(reverse('issues:list'))

    #return render(request,'issues/index.html')

@group_required('engineer')
def test(request):
    is_engineer = request.user.groups.filter(name='engineers').exists()
    msg=f'is_engineer={is_engineer}'
    return render(request,'issues/test.html', {'is_engineer':is_engineer})

@login_required
def dashboard(request):
    sql="select i.id, i.category_id,c.name,count(*) from issues_issue i left join issues_category c on i.category_id=c.id where not i.completed group by c.name"

    my_issues=Issue.objects.filter(Q(assigned_to=request.user.id)|Q(submitted_by=request.user.id)).filter(Q(completed=False)).count()
    open_issues=Issue.objects.filter(completed=False).count()
    open_issues_by_category = Issue.objects.filter(completed=False).values('category__name').annotate(total=Count('category'))
    unassigned_issues=Issue.objects.filter(completed=False).filter(assigned_to=None).count()
    completed_issues = Issue.objects.filter(completed=True).count()

    return render(request, 'issues/dashboard.html', {'my_issues':my_issues,'open_issues':open_issues,'unassigned_issues':unassigned_issues})

@login_required
def issues_list(request):
    title="Open Issues"
    f=request.GET.get('f',None)

    is_manager=request.user.is_staff | request.user.is_superuser | request.user.groups.filter(name="engineers").exists()

    filter = ""

    if not f:
        f='mine'

    if f=='mine':   #show issues assigned to user
        filter+=f'assigned_to={request.user.id}&submitted_by={request.user.id}'
        title="My Issues"

    if f=='ua':
        if(is_manager):
            filter+=f'assigned_to=0&completed=0'
            title="Unassigned Issues"
        else:
            f='all'

    if f=='oi':
        filter+=f'completed=0'
        title="Open Issues"

    if f=='completed':
        filter+=f'completed=1'
        title="Completed Issues"

    if f=='all':
        title="All Issues"

    if len(filter)>0:
        filter="?"+filter

    template_name = 'issues/list.html'
    #Differences between Postgres and SQLite on how to order null values and that Datatables does final ordering
    #we include the header Completed=completed_date and IsCompleted=completes so we can order by completed,created_date
    #IsCompleted is hidden in the table
    headers=['Issue#','Short_Desc','Category','Location','Created','Submitted By','Assigned To','Completed','IsCompleted']
    #s='{}{}{}'.format(request.META['HTTP_HOST'],reverse('issues-list-data'),filter,)
    s = '{}{}'.format(reverse('issues:list-data'), filter, )
    extra_context={'headers': headers,'ajax_url':s, 'title':title, 'is_manager':is_manager}

    #print(filter)

    return render(request,template_name,extra_context)


### Datatables
from django_datatables_view.base_datatable_view import BaseDatatableView

class DTIssueListViewData(BaseDatatableView):
    """
    Returns JSON format of data for Datatables

    Column sorting is overridden by what is defined in the Datatable config in the HTML file
    """
    model = Issue
    columns = ['id','short_desc','category','location','created_date','submitted_by','assigned_to','completed_date','completed']
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
            #qs = qs.filter(short_desc__istartswith=search)
            qs = qs.filter(Q(short_desc__icontains=search)|Q(desc__icontains=search))

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

        # NOTE - column ordering is overridden by datatables in HTML file
        #qs.order_by('completed','created_date')
        return qs.filter(q0)

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        url = '/issues'
        date_format = "%Y-%m-%d"
        for i in qs:
            if i.category:
                category=i.category.name
            else:
                category=""
            if i.submitted_by:
                submitted_by=i.submitted_by.username
            else:
                submitted_by=""

            if i.assigned_to == None:
                assigned_to = ""
            else:
                assigned_to = i.assigned_to.username
            if i.location:
                location = i.location.lid
            else:
                location = ""

            created_date = i.created_date.strftime(date_format)
            if i.completed_date:
                completed_date = i.completed_date.strftime(date_format)
            else:
                completed_date = ""

            json_data.append([
                f'<a href="{url}/{i.id}">{i.id}</a>', f'<a href="{url}/{i.id}">{i.short_desc}</a>', category,
                location, created_date, submitted_by, assigned_to, completed_date,i.completed
            ])

        return json_data



# class DTIssueListView(TemplateView):
#     template_name = 'issues/list3.html'
#     headers=['Issue#','Short_Desc','Category','Created','Submitted By','Assigned To','Completed']
#     extra_context={'headers': headers,'ajax_url':'/issues/list3/data'}

from .mail import new_issue_mail, new_issue_response_mail, updated_issue_mail

@login_required
def issue_new(request):
    """
    Create a new Issue

    :param request:
    :return: renders data with template
    """

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = IssueForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as requfrom django.core.mail import send_mailired
            rc=form.save()

            files=request.FILES.getlist('attachments')
            for f in files:
                #handle_uploaded_file(f,'files/')
                fn=path.join('docs',str(rc.id),f.name)
                fn=default_storage.save(fn,f)
                d = Document(file=fn,issue=rc)
                d.save()

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

            #handle attachments
            files=request.FILES.getlist('attachments')
            for f in files:
                #handle_uploaded_file(f,'files/')
                fn=path.join('docs',str(rc.id),f.name)
                fn=default_storage.save(fn,f)
                d = Document(file=fn,issue=rc)
                d.save()

            #if completed send notification email
            if ('completed' in form.changed_data) and (rc.completed):
                updated_issue_mail(request, rc, form.changed_data)

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('issues:issue-detail', args=[rc.pk]))

    # if a GET (or any other method) we'll create a blank form
    else:
        if (action=="delete"):
            #instance = Person.objects.get(pk=pk)
            return render(request, 'ticket/confirm_delete.html', {'object': instance,'success_url':success_url})

        form = IssueForm(instance=instance)
        tags_all=Tag.objects.all().order_by('name')
        attachments=instance.document_set.all()

    return render(request, 'issues/issue.html', {'form': form, 'rid':pk, 'tags_all': tags_all, 'action':action, 'is_engineer':is_engineer, 'attachments':attachments})

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
                d = Document(file=fn,response=rs)
                d.save()

            #send email to author and (assigned_to or engineer group)
            new_issue_response_mail(request, issue, rs)

            #s='/issues/{}'.format(pk,)
            return HttpResponseRedirect(request.path)
        else:
            #TODO Form Validation Error Page
            return HttpResponseRedirect('/')
    else:
        issue_responses=issue.response_set.all().order_by('date')
        response_form=ResponseForm(initial={'author': request.user, 'issue':issue.id})

    return render(request, 'issues/detail.html', { 'object': issue, 'rid': pk,'issue_responses':issue_responses,'response_form':response_form, 'can_edit':can_edit })


@method_decorator(login_required, name='dispatch')
class LocationView(TemplateView):
    """
    View of Issues by Location
    """

    template_name = "issues/location.html"

    def get_context_data(self, **kwargs):
        """
        Set context.
        If GET location then select that location else
        checks for a session['location'] else set location="".

        Whatever location is select will be saved in a session variable.

        :param kwargs:
        :return: context
        """
        context = super().get_context_data(**kwargs)
        #context['data'] = self.getJson()
        if (self.request.GET.get('location',False)):
            cur_location=self.request.GET.get('location','')
        else:
            cur_location=self.request.session._session.get('location','')

        self.request.session['location']=cur_location

        context['cur_location']=cur_location
        context['locations'] = Location.objects.all().order_by('name')
        context['issues'] = Issue.objects.all().filter(completed=False).filter(location_id=cur_location).order_by('location').order_by('id')
        context['title'] = f"Issues by Locations"
        return context

    # def render_to_response(self, context, **response_kwargs):
    #     response = super(TemplateView, self).render_to_response(context, **response_kwargs)
    #     #response.set_cookie('location', 'Aeroptic')
    #     return response

    def getJson(self):
        """
        Creates data for Issues by location

        :return:
        """

        locations = Location.objects.all().order_by('name')
        o=[]
        for i in locations:
            x = {"id": i.lid, "text": i.name, "li_attr":{"id2":''},"a_attr":{"href":"#"},"icon":"fas fa-map-marker-alt"}

            c=[]
            issues=Issue.objects.filter(location=i.lid).filter(completed=False).order_by('id')
            js_str=self.getIssueJson(issues)

            x['children'] = json.loads(js_str)

            o.append(x)

        js_str=json.dumps(o)
        return js_str

    def getIssueJson(self, issues):
        """
        Gets Issues as JSON

        :return: JSON string
        """
        maxWidth=50
        o=[]
        for i in issues:
            if (len(i.short_desc) > maxWidth):
                txt=i.short_desc[:maxWidth-3]+"..."
            else:
                txt=i.short_desc

            x = {"id": i.id, "text": f"{txt} ({i.id})", "li_attr":{"title":i.short_desc},"a_attr":{"href":"/issues/"+str(i.id)}}

            # c=[]
            # issues=Issue.objects.filter(location=i.lid)
            # js_str=self.getIssueJson(issues)
            #
            # x['children'] = json.loads(js_str)

            o.append(x)

        js_str=json.dumps(o)
        return js_str




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