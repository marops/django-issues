#from django.conf.urls import include, url
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from . import views

#from django.conf import settings
# from django.contrib import admin
# from django.contrib.sitemaps.views import sitemap
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from django.views.static import serve
#from django.urls import path, include
from rest_framework import routers


# router = routers.DefaultRouter()
# router.register(r'issues', views.IssueViewSet)
# #router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

app_name = 'issues'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/',views.issues_list, name='list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/data/', login_required(views.DTIssueListViewData.as_view()), name='list-data'),
    path('<int:pk>/', views.issue_detail, name='issue-detail'),
    path('<int:pk>/<str:action>/', views.issue_view, name='issues-action'),
    path('new/',views.issue_new, name='issue-new'),
    path('location/', views.LocationView.as_view(), name='issues-location'),
    path('test/',views.test, name='issues-test'),
    path('rest/', views.rest, name='rest'),
    #path('data/', include(router.urls)),
]


# urlpatterns = [
#     url(r'^$',  views.index, name='index'),
#     url(r'^list/$', views.issues_list, name='list'),
#     url(r'^dashboard/$',  views.dashboard, name='dashboard'),
#     url(r'^list/data/', login_required(views.DTIssueListViewData.as_view()), name='list-data'),
#     url(r'(?P<pk>\d+)/(?P<action>\w+)/$', views.issue_view, name='issues-action'),
#     url(r'(?P<pk>\d+)/$', views.issue_detail, name='issue-detail'),
#     url(r'^new/$', views.issue_new, name='issue-new'),
#     url(r'^test', views.test)
#
#     # url(r'^list/data/', views.DTIssueListViewData.as_view(), name='issues-list-data'),
#     # url(r'^list/data/', views.DTIssueListViewData.as_view(), name='issues-list-data'),
#     #url(r'^issues/', include('issues.urls')),
# ]