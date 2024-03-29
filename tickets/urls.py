# your_app_name/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="home"),
    path('signup',views.signup,name="signup"),
    path('signin',views.signin,name="signin"),
    path('signout',views.signout,name="signout"),
     path('ticketform',views.ticketform,name="ticketform"),  # home page
    path('submit-ticket/', views.submit_ticket, name='submit_ticket'),
    path('oauth-callback/', views.oauth_callback, name='oauth_callback'),
    path('view-using-jira-api/', views.view_using_jira_api, name='view_using_jira_api'),
]
