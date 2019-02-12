from django.contrib.auth.models import User, Group

from django.core.mail import send_mail

def new_issue_mail(request,issue):
    """
    Sends out mail when a new issue is created.

    Sent to user who submitted (submitted_by) and all in engineer group

    :param request: the view request. Used to get URI
    :param issue: the new issue
    :return:
    """

    mail_to =[issue.submitted_by.email]
    g= Group.objects.get(name="engineers")
    rs = g.user_set.all()
    for u in rs:
        mail_to.append(u.email)

    subject = f'New Issue {issue.id} Created'
    message = """
A new issue has been submitted and can be viewed at http {}
Please do not respond to this email. Use the link above to submit a response.

SHORT DESCRIPTION: {}

DESCRIPTION:

HR3D Engineering Team
HR3D_ENG@lediso.com

{}
    """.format(request.build_absolute_uri(f"/issues/{issue.id}"), issue.short_desc, issue.desc)

    send_mail(
        subject,
        message,
        'noreply@leidos.com',
        mail_to,
        fail_silently=False,
    )
