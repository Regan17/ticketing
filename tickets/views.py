# tickets/views.py
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .forms import TicketForm
import requests
from oauth2_provider.models import Application
import logging

# Set up the logger
logger = logging.getLogger(__name__)
ITSM_API_URL = "https://chiragarora.atlassian.net/rest/api/2"

def index(request):
    return render(request,"tickets/index.html")

def submit_ticket(request):
    print("Reached submit_ticket view")
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            print("system")
            application_name = 'Ticketmanager'  # Update with your application name
            application = Application.objects.get(name=application_name)
            redirect_uri = settings.JIRA_OAUTH_SETTINGS['redirect_uri']
            print('hello')
            authorization_url = "https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=gZGT3o3zVpVYwaT3OApjNa6XJ7oBpF6h&scope=read%3Ame&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Foauth-callback%2F&state=${YOUR_USER_BOUND_VALUE}&response_type=code&prompt=consent"
            print(authorization_url)
            request.session['ticket_id'] = ticket.id

            return HttpResponseRedirect(authorization_url)

    else:
        form = TicketForm()
    return render(request, 'tickets/submit_ticket.html', {'form': form})

def oauth_callback(request):
    print("Reached oauth_callback view")
    
    # Handle the OAuth callback
    code = request.GET.get('code')
    print("Received authorization code:", code)

    if not code:
        print("Authorization code not received.")
        return HttpResponse("Authorization code not received.")

    # Make a POST request to exchange the code for an access token
    print("Exchanging code for access token...")
    token_url = "https://auth.atlassian.com/oauth/token"
    application = Application.objects.get(name='Ticketmanager')  # Replace with your app name
    # redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    payload = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': 'gZGT3o3zVpVYwaT3OApjNa6XJ7oBpF6h',
        'client_secret': 'ATOAzkncX3_Qyqcgo-3WJG4rtPHkPvmvuqjyM9qFThypW8kY1IiVLBynZGfCRv6E2chP0AC5CF58',
        'redirect_uri': 'http://127.0.0.1:8000/oauth-callback/',
    }
    
    # Initialize the response variable
    response = None
    
    try:
        response = requests.post(token_url, data=payload)
        print("Token exchange response status code:", response.status_code)

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            # Store the access token securely, for example, in the Django session or database
            request.session['jira_access_token'] = access_token
            print("Access token:", access_token)
            logger.info("Access token: %s", access_token)
            return render(request, 'tickets/success.html')

        else:
            print("Failed to exchange code for access token.")
            print("Error response:", response.json())  # Print the error response for debugging
            return render(request, 'tickets/error.html')

    except Exception as e:
        print("Exception during token exchange:", str(e))
        return render(request, 'tickets/error.html')




def view_using_jira_api(request):
    # Example view using Jira API with stored access token
    access_token = request.session.get('jira_access_token')
    if not access_token:
        return render(request, 'tickets/error.html', {'message': 'Access token not available'})

    # Make authenticated requests to Jira API using access_token
    headers = {'Authorization': f'Bearer {access_token}'}
    jira_response = requests.get(f'{ITSM_API_URL}/your-api-endpoint', headers=headers)

    if jira_response.status_code == 200:
        jira_data = jira_response.json()
        return render(request, 'jira_data.html', {'jira_data': jira_data})
    else:
        return render(request, 'tickets/error.html', {'message': 'Failed to fetch data from Jira API'})


# ATATT3xFfGF0Dn9UAU999ciulv0J3mnSU-Lf6M1j7_xZIMG0XJgDTJ79PpvTo_hZNeIrgNzuBFAXyIYb8GEdReift9fQJm9MCK_rsr6Kl0e3mdDsKH714NBlWWXBz1nIqOC3JZE4E4GgzE0l1PQaP9QQNFctHfFpvpGxsyqRxAh3CCeeaUUAyl8=BE7E24E8