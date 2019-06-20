from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class MailList:
    """
    Simple class to build a list without duplicates

    list is a python list
    """

    def __init__(self):
        self.list=[]

    def add(self, item):
        """
        Adds unique items to list. IE if item already exists
        it will not be added.

        :param item:

        """
        if item not in self.list:
            self.list.append(item)


def new_issue_mail(request,issue):
    """
    Sends out mail when a new issue is created.

    Sent to user who submitted (submitted_by) and all in engineer group

    :param request: the view request. Used to get URI
    :param issue: the new issue
    :return:
    """

    mail_to = MailList()
    mail_to.add(issue.submitted_by.email)
    g= Group.objects.get(name="engineers")
    rs = g.user_set.all()
    for u in rs:
        mail_to.add(u.email)

    if issue.category_id == 2:  #LIDAR sensor
        template_base="new_issue_mail_lidar"
    else:
        template_base="new_issue_mail"

    subject = f'New Issue ({issue.id}) {issue.short_desc[0:50]} '

    if issue.location:
        location=issue.location.name
    else:
        location=""

    message = render_to_string(f'issues/{template_base}.txt', {
        'submitted_by': issue.submitted_by.username,
        'location': location,
        'link': request.build_absolute_uri(f"/issues/{issue.id}"),
        'short_desc' : issue.short_desc,
        'desc' : issue.desc,
    })

    html_message=render_to_string(f'issues/{template_base}.html', {
        'submitted_by': issue.submitted_by.username,
        'location': location,
        'link': request.build_absolute_uri(f"/issues/{issue.id}"),
        'short_desc' : issue.short_desc,
        'desc' : issue.desc,
    })

    #message=strip_tags(html_message)

    send_mail(
        subject,
        message,
        'noreply@hr3d.leidos.com',
        mail_to.list,
        fail_silently=False,
        html_message=html_message
    )

def new_issue_response_mail(request,issue,issue_response):
    """
    Sends out mail when a new response is submitted.

    Sent to user who submitted (submitted_by) and all in engineer group
    :param request: the view request. Used to get URI
    :param issue: the new issue
    :param issue_response: the new issue_response
    :return:
    """

    mail_to = MailList()
    mail_to.add(issue.submitted_by.email)
    mail_to.add(issue_response.author.email)

    if(issue.assigned_to):
        mail_to.add(issue.assigned_to.email)
    else: #If not assigned then send to all in engineers group
        g= Group.objects.get(name="engineers")
        rs = g.user_set.all()
        for u in rs:
            mail_to.add(u.email)

    subject = f'New Response to Issue ({issue.id}) {issue.short_desc[0:30]}'

    html_message=render_to_string('issues/new_response_mail.html', {
        'submitted_by': issue.submitted_by.username,
        'issue_id' : issue.id,
        'author' : f'{issue_response.author.username} ({issue_response.author.email})',
        'link': request.build_absolute_uri(f"/issues/{issue.id}"),
        'short_desc' : issue.short_desc,
        'text' : issue_response.text
    })

    message=strip_tags(html_message)

    send_mail(
        subject,
        message,
        'noreply@hr3d.leidos.com',
        mail_to.list,
        fail_silently=False,
        html_message=html_message
    )
