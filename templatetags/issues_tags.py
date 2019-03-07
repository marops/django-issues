from django import template
from issues.models import Issue, Response
from django.db.models import Q
from datetime import datetime, timedelta, timezone

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

    issues=Issue.objects.filter(created_date__gte=dt).filter(completed=False)
    responses = Response.objects.filter(issue__completed=False).filter(date__gt=dt)
    #completed=Issue.objects.filter(completed_date__gte=dt)
    completed=Issue.objects.filter(completed_date__gte=dt)

    return {'time_period':time_period,'issues':issues,'responses': responses, 'completed':completed}