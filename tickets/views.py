# tickets/views.py
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# from itsm_ticketing.tickets.models import Ticket
from .models import Ticket

# from itsm_ticketing.tickets.models import Ticket
from .forms import TicketForm
import requests
from oauth2_provider.models import Application
import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('board')
    return render(request,"tickets/index.html")
def signup(request):
        if request.method=="POST":
            fname=request.POST['first_name']
            lname=request.POST['last_name']
            username=request.POST['username']
            email=request.POST['email']
            pass1=request.POST['password']
            pass2=request.POST['confirm_password']
            if User.objects.filter(username=username):
                messages.error(request, "Username already exist! Please try some other username.")
                return render(request,"tickets/index.html")
        
            # if User.objects.filter(email=email).exists():
            #     messages.error(request, "Email Already Registered!!")
            #     return render(request,"authentication/index.html")
        
            if len(username)>20:
                messages.error(request, "Username must be under 20 charcters!!")
                return render(request,"tickets/index.html")
        
            if pass1 != pass2:
                messages.error(request, "Passwords didn't matched!!")
                return render(request,"tickets/index.html")
        
            if not username.isalnum():
                messages.error(request, "Username must be Alpha-Numeric!!")
                return render(request,"tickets/index.html")

            myuser=User.objects.create_user(username,email,pass1)
            myuser.first_name=fname
            myuser.last_name=lname
            myuser.save()
            messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")

        # Welcome Email
            subject = "Welcome to Portfolio-Chiragx._.17"
            message = "Hello " + myuser.first_name + "!! \n" + "Welcome to My website!! \nThank you for visiting\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nAnubhav Madhav"        
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            return redirect('signin')
        return render(request,"tickets/signup.html")
def signin(request):
    # If the user is already logged in, redirect to 'fb.html'
    if request.user.is_authenticated:
        return render(request,'tickets/board.html')

    # If it's a POST request, attempt to authenticate the user
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            return render(request,'tickets/board.html')
        else:
            messages.error(request, 'Username or password incorrect!')
            return redirect('signin')

    return render(request,"tickets/signin.html")
def signout(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged Out Successfully!!")
    else:
        messages.warning(request, "You are not signed in. Sign in first to logout.")

    return redirect('home')


def ticketform(request):
    form = TicketForm()
    return render(request, 'tickets/submit_ticket.html', {'form': form})





























































# Set up the logger
logger = logging.getLogger(__name__)
ITSM_API_URL = "https://chiragarora.atlassian.net/rest/api/3"

def index(request):
    return render(request,"tickets/index.html")

def submit_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            print("Form Data:", request.POST)
            # Use the newly created fields in your Jira API request
            jira_issue_data = {
                'fields': {
                    'project': {'key': 'TIC'},
                    'summary': ticket.summary,
                    'description': {
                        'type': 'doc',
                        'version': 1,
                        'content': [
                            {
                                'type': 'paragraph',
                                'content': [{'type': 'text', 'text': ticket.description}]
                            }
                        ]
                    },
                }
            }

            # The rest of your Jira API request logic goes here

            application_name = 'Ticketmanager'  # Update with your application name
            redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
            authorization_url = "https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=gZGT3o3zVpVYwaT3OApjNa6XJ7oBpF6h&scope=read%3Ajira-work%20read%3Ajira-user%20write%3Ajira-work%20manage%3Ajira-project&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Foauth-callback%2F&state=${YOUR_USER_BOUND_VALUE}&response_type=code&prompt=consent"
            request.session['ticket_id'] = ticket.id
            return HttpResponseRedirect(authorization_url)
    else:
        form = TicketForm()
    return render(request, 'tickets/submit_ticket.html', {'form': form})

def oauth_callback(request):
    print('reached oauth')
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Authorization code not received.")

    token_url = "https://auth.atlassian.com/oauth/token"
    payload = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': 'gZGT3o3zVpVYwaT3OApjNa6XJ7oBpF6h',
        'client_secret': 'ATOAzkncX3_Qyqcgo-3WJG4rtPHkPvmvuqjyM9qFThypW8kY1IiVLBynZGfCRv6E2chP0AC5CF58',
        'redirect_uri': request.build_absolute_uri(reverse('oauth_callback')),
    }
    
    try:
        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            print("oauth done")
            access_token = response.json().get('access_token')
            request.session['jira_access_token'] = access_token
            return HttpResponseRedirect(reverse('view_using_jira_api'))
        else:
            print("Failed to exchange code for access token.")
            print("Error response:", response.json())
            return render(request, 'tickets/error.html')
    except requests.RequestException as e:
        print("Exception during token exchange:", str(e))
        return render(request, 'tickets/error.html')

def view_using_jira_api(request):
    ticket_id = request.session.get('ticket_id')
    print("got ticket id")
    if not ticket_id:
        return render(request, 'tickets/error.html', {'message': 'Ticket ID not available'})
    
    try:
        print("in thiss try")
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return render(request, 'tickets/error.html', {'message': 'Ticket not found'})

    access_token = request.session.get('jira_access_token')
    if not access_token:
        return render(request, 'tickets/error.html', {'message': 'Access token not available'})

    # Make a GET request to get accessible resources
    accessible_resources_url = "https://api.atlassian.com/oauth/token/accessible-resources"
    print('heree')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(accessible_resources_url, headers=headers)
        print("get done")
        response.raise_for_status()
        print("success")  # Check for errors in the response

        accessible_resources = response.json()
        print("Accessible Resources:", accessible_resources)

        if not accessible_resources:
            return render(request, 'tickets/error.html', {'message': 'No accessible resources found'})

        # Assuming the response is a JSON array, extract the first item (site) and get its 'id' (cloudid)
        cloudid = accessible_resources[0].get('id')

        if not cloudid:
            return render(request, 'tickets/error.html', {'message': 'No cloudid found in accessible resources'})

    except requests.RequestException as e:
        print("Exception during accessible resources request:", str(e))
        return render(request, 'tickets/error.html')

    # Construct the Jira API request URL with the cloudid
    jira_api_url = f'https://api.atlassian.com/ex/jira/{cloudid}/rest/api/3/issue'
    print("here also")
    headers['Content-Type'] = 'application/json'  # Add this line to headers
    jira_issue_data = {
        'fields': {
            'project': {'key': 'TIC'},
            'summary': str(ticket.summary),  # Ensure that summary is a string
            'description': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': ticket.description}]
                    }
                ]
            },
            'issuetype': {'name': 'Task'}, # Retrieve issue type from the form
        }
    }

    try:
        jira_response = requests.post(jira_api_url, json=jira_issue_data, headers=headers)
        print("Request Headers:", jira_response.request.headers)
        
        if jira_response.status_code == 201:
            print("Jira issue created successfully!")
            created_issue_key = jira_response.json().get('key')
            return render(request, 'tickets/board.html')
        else:
            print("Failed to create Jira issue. Status Code:", jira_response.status_code)
            print("Error response:", jira_response.json())
            return render(request, 'tickets/error.html')
        
    except requests.RequestException as e:
        print("Exception during Jira API request:", str(e))
        return render(request, 'tickets/error.html')
# "description": {
#       "content": [
#         {
#           "content": [
#             {
#               "text": "Order entry fails when selecting supplier.",
#               "type": "text"
#             }
#           ],
#           "type": "paragraph"
#         }
#       ],
#       "type": "doc",
#       "version": 1
#     },
    #     "issuetype": {
    #   "id": "10000"
    # },
    #     "summary": "Main order flow broken",
    # "timetracking": {
    #   "originalEstimate": "10",
    #   "remainingEstimate": "5"
    # },
#     response = requests.request(
#    "POST",
#    url,
#    data=payload,
#    headers=headers,
#    auth=auth
# )


# ATATT3xFfGF0Dn9UAU999ciulv0J3mnSU-Lf6M1j7_xZIMG0XJgDTJ79PpvTo_hZNeIrgNzuBFAXyIYb8GEdReift9fQJm9MCK_rsr6Kl0e3mdDsKH714NBlWWXBz1nIqOC3JZE4E4GgzE0l1PQaP9QQNFctHfFpvpGxsyqRxAh3CCeeaUUAyl8=BE7E24E8