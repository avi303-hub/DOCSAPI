from django.shortcuts import render

from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .google_auth import get_google_auth_flow
from .doc_service import create_google_doc
from .models import UserGoogleAuth
import json

@api_view(['GET'])
def google_auth_init(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    flow = get_google_auth_flow(request)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['google_oauth_state'] = state
    return Response({'auth_url': authorization_url})

@api_view(['GET'])
def oauth2callback(request):
    if not request.user.is_authenticated:
        return redirect('/')
    
    state = request.session.get('google_oauth_state')
    if not state or state != request.GET.get('state'):
        return Response({'error': 'Invalid state parameter'}, status=status.HTTP_400_BAD_REQUEST)
    
    flow = get_google_auth_flow(request)
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    
    creds = flow.credentials
    UserGoogleAuth.objects.update_or_create(
        user=request.user,
        defaults={
            'google_access_token': creds.token,
            'google_refresh_token': creds.refresh_token,
            'token_expiry': creds.expiry
        }
    )
    
    return Response({'status': 'Google authentication successful'})
import logging

logger = logging.getLogger(__name__)  # Set up logging

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_doc(request):
    html_content = request.data.get('content')
    title = request.data.get('title', 'New Document')

    if not html_content:
        return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        doc_url = create_google_doc(request.user, html_content, title)
        return Response({'url': doc_url}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating Google Doc: {e}", exc_info=True)  # Logs full error stack trace
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.shortcuts import render

def index(request):
    return render(request, '1gdocs/index.html', {'user': request.user})
