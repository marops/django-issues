from django.contrib.auth.models import User, Group
from django.core.mail import send_mail


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

    subject = f'New Issue ({issue.id}) {issue.short_desc[0:30]} '
    message = f"""
A new issue has been submitted and can be viewed at {request.build_absolute_uri(f"/issues/{issue.id}")}

Please do not respond to this email. Use the link above to submit a response.

SHORT DESCRIPTION: {issue.short_desc}

DESCRIPTION:

{issue.desc}

HR3D Engineering Team
HR3D_ENG@lediso.com

    """

    send_mail(
        subject,
        message,
        'noreply@hr3d.leidos.com',
        mail_to.list,
        fail_silently=False,
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
    message = f"""
A new response to issue {issue.id} ({issue.short_desc}) has been submitted and can be viewed at {request.build_absolute_uri(f"/issues/{issue.id}")}.

Please do not respond to this email. Use the link above to submit a response.

TEXT:

{issue_response.text}

HR3D Engineering Team
HR3D_ENG@ledios.com   
    """

    send_mail(
        subject,
        message,
        'noreply@hr3d.leidos.com',
        mail_to.list,
        fail_silently=False,
    )
