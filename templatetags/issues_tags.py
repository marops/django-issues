from django import template
from issues.models import Issue, Response
from django.db.models import Q
from datetime import datetime, timedelta, timezone
from django.db.models import Count

register = template.Library()

@register.inclusion_tag('issues/responses.html')
def show_responses(issue):
    issue_responses = issue.response_set.all()
    return {'issue_responses': issue_responses}

@register.inclusion_tag('issues/files.html')
def issues_response_files(issue_response):
    files = issue_response.document_set.all()
    return {'response_files': files}

@register.inclusion_tag('issues/activity.html')
def activity(days):
    dt = datetime.now(timezone.utc) - timedelta(days=days)
    if days == 1:
        time_period='24 Hours'
    else:
        time_period= f'{days} Days'

    issues_new=Issue.objects.filter(created_date__gte=dt).filter(completed=False)
    issues = Issue.objects.filter(completed=False).filter(response__date__gt=dt).annotate(Count('response')).order_by('id')
    responses = Response.objects.filter(issue__completed=False).filter(date__gt=dt).order_by('issue__id')
    #completed=Issue.objects.filter(completed_date__gte=dt)
    completed=Issue.objects.filter(completed_date__gte=dt)

    issue_responses=[]
    for i in issues:
        l=[]
        for r in responses.filter(issue_id=i.id):
            l.append(r.text)
        issue_responses.append({'id':i.id, 'short_desc':i.short_desc,'response__count':i.response__count,'response_list':l})


    return {'time_period':time_period,'issues_new':issues_new, 'issues':issues,'responses': responses, 'issue_responses':issue_responses, 'completed':completed}