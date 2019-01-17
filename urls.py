from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.contrib.auth.decorators import login_required

#from django.urls import path, include

from . import views
#from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'issues', views.IssueViewSet)
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

# urlpatterns = [
#     path('', views.dashboard, name='issues-dashboard'),
#     path('list/',views.issues_list, name='issues-list'),
#     path('list/data/', views.DTIssueListViewData.as_view(), name='issues-list-data'),
#     path('<int:pk>/', views.issue_detail, name='issues-detail'),
#     path('<int:pk>/<str:action>/', views.issue_view, name='issues-action'),
#     path('test/',views.test, name='isues-test'),
#     # path('rest', views.rest, name='issues-rest'),
#     # path('data/', include(router.urls))
# ]

app_name = 'issues'

urlpatterns = [
    url(r'^$',  views.dashboard, name='index'),
    url(r'^list/$', views.issues_list, name='list'),
    url(r'^dashboard/$',  views.dashboard, name='dashboard'),
    url(r'^list/data/', login_required(views.DTIssueListViewData.as_view()), name='list-data'),
    url(r'(?P<pk>\d+)/(?P<action>\w+)/$', views.issue_view, name='issues-action'),
    url(r'(?P<pk>\d+)/$', views.issue_detail, name='issues-detail'),
    # url(r'^list/data/', views.DTIssueListViewData.as_view(), name='issues-list-data'),
    # url(r'^list/data/', views.DTIssueListViewData.as_view(), name='issues-list-data'),
    #url(r'^issues/', include('issues.urls')),
]