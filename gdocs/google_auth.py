import os
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from .models import UserGoogleAuth

def get_google_auth_flow(request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=settings.GOOGLE_OAUTH2_SCOPES,
        redirect_uri=settings.GOOGLE_OAUTH2_REDIRECT_URI
    )
    return flow

def get_user_credentials(user):
    try:
        auth = UserGoogleAuth.objects.get(user=user)
        creds = Credentials(
            token=auth.google_access_token,
            refresh_token=auth.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            scopes=settings.GOOGLE_OAUTH2_SCOPES
        )
        
        if creds.expired:
            creds.refresh(Request())
            auth.google_access_token = creds.token
            auth.save()
        
        return creds
    except UserGoogleAuth.DoesNotExist:
        return None