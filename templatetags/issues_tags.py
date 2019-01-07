from django import template

register = template.Library()

@register.inclusion_tag('issues/responses.html')
def show_responses(issue):
    issue_responses = issue.response_set.all()
    return {'issue_responses': issue_responses}

@register.inclusion_tag('issues/files.html')
def issues_response_files(issue_response):
    files = issue_response.document_set.all()
    return {'response_files': files}