from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import Issue


class IssuesMenu(CMSAttachMenu):
    name = _("Issues Menu")  # give the menu a name this is required.

    def get_nodes(self, request):
        """
        This method is used to build the menu tree.
        """
        nodes = []
        # node = NavigationNode(
        #     title='dashboard',
        #     url=reverse('polls:detail', args=(poll.pk,)),
        #     id=1,  # unique id for this node within the menu
        # )

        nodes.append(NavigationNode(title='My Issues', url='/issues/list', id=1))
        nodes.append(NavigationNode(title='New Issue', url='/issues/new', id=2))
        nodes.append(NavigationNode(title='Dashboard', url='/issues/dashboard', id=3))
        nodes.append(NavigationNode(title='By Location', url='/issues/location', id=3))
        nodes.append(NavigationNode(title='SITREP', url='/issues/sitrep', id=4))

        # n = NavigationNode(_('sample settings page'), "/bye/", 2)
        # nodes.append(n)

        return nodes

menu_pool.register_menu(IssuesMenu)