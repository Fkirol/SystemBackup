from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomAuthentication(BaseAuthentication):
  
    def has_permission(self, request, view):
        auth = JWTAuthentication()
        try:
            # Intenta obtener el token de la cookie
            token = request.COOKIES.get('access_token')
            if token:
                # Verifica el token
                validated_token = auth.get_validated_token(token)
                request.user = validated_token.payload['user_id']
                return True
                
            else:
                return False
        except AuthenticationFailed:
            return False
        
        
    def has_object_permission(self, request, view, _):
        auth = JWTAuthentication()
        try:
            # Intenta obtener el token de la cookie
            token = request.COOKIES.get('access_token')
            if token:
                # Verifica el token
                validated_token = auth.get_validated_token(token)
                request.user = validated_token.payload['user_id']
                return True
                
            else:
                return False
        except AuthenticationFailed:
            return False





class Databases(APIView):
    permission_classes = [CustomAuthentication]
    
    def get(self, request):
        auth_token = request.COOKIES.get('access_token')
        
            
        return Response({"Mundo":"hola"},status=status.HTTP_200_OK)

# Create your views here.
class GoogleLoginView(APIView):
    def post(self, request):
        try:
            code = request.data.get('code')
            print(request.data)
            if not code:
                return Response({'error': 'Code not provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Exchange the code for an access token
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': '68980836329-lmv0os57s0o01sdet97j5biie9qsg01k.apps.googleusercontent.com',
                    'client_secret': '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',
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': 'http://localhost:8080/'
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            token_response_data = token_response.json()
            access_token = token_response_data.get('access_token')
            
            if not access_token:
                return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use the access token to get user information
            user_response = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_data = user_response.json()
            
            user = type('User', (object,), user_data)
            # Get or create the user in the database
           
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            response = Response({
                "user":user_data
            }, status=status.HTTP_200_OK)
            
            # Set the tokens in cookies
            response.set_cookie('access_token', str(refresh.access_token), httponly=False,
            secure=False,  # Usa True si estás en producción y usas HTTPS
            samesite='None')  # Cambia según tus necesidade)
            response.set_cookie('refresh_token', str(refresh),httponly=False,
            secure=False,  # Usa True si estás en producción y usas HTTPS
            samesite='None'  # Cambia según tus necesidade
            )
            
            
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class GithubLoginView(APIView):
    def post(self, request):
        try:
            code = request.data.get('code')
            if not code:
                return Response({'error': 'Code not provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Exchange the code for an access token
            token_response = requests.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': 'Ov23liRCYvhncUEXeJwL',
                    'client_secret': 'a2f87cb019dbea11497929be7676ce1409f81013',
                    'code': code
                },
                headers={'Accept': 'application/json'}
            )
            token_response_data = token_response.json()
            access_token = token_response_data.get('access_token')
            
            if not access_token:
                return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use the access token to get user information
            user_response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {access_token}'}
            )
            
            user_data = user_response.json()
            user = type('User', (object,), user_data)
            # Get or create the user in the database
           
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            response = Response({
                "user":user_data
            }, status=status.HTTP_200_OK)
            
            # Set the tokens in cookies
            response.set_cookie('access_token', str(refresh.access_token), httponly=False,
            secure=False,  # Usa False si estás en producción y usas HTTPS
            samesite='None')  # Cambia según tus necesidade)
            response.set_cookie('refresh_token', str(refresh),httponly=False,
            secure=False,  # Usa True si estás en producción y usas HTTPS
            samesite='None'  # Cambia según tus necesidade
            )
            
            
            
            
            return response
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
