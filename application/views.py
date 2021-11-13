from django.shortcuts import render
from requests.api import head
from rest_framework.decorators import api_view
from rest_framework import status
from application import utils
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from bs4 import BeautifulSoup
from django.http.response import JsonResponse
from .serializers import *
from rest_framework.generics import GenericAPIView
# Create your views here.

class MainPage(generics.GenericAPIView):

    serializer_class = MainPageSerializer
    token_param_config = [openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,),
                openapi.Parameter('order_by', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)]

    @swagger_auto_schema(manual_parameters=token_param_config)
    def get(self, request):
        
        page = request.GET.get('page')
        order_by = None if not request.GET.get('order_by') else request.GET.get('order_by')
        
        if not request.user.is_authenticated:
            # main page without sign in
            if page != None and int(page)< 0:
                return  JsonResponse({}, safe=False,  status=status.HTTP_404_NOT_FOUND)
            listProdPerPage = utils.showProduct(0 if not page else int(page),order_by)
            return  JsonResponse(listProdPerPage, safe=False,  status=status.HTTP_202_ACCEPTED)
        else :
            'TODO'
            # main page with sign in -> need to implement recommendation system

            if page != None and int(page)< 0:
                return  JsonResponse({}, safe=False,  status=status.HTTP_404_NOT_FOUND)
            listProdPerPage = utils.showProduct(0 if not page else int(page),order_by)
            return  JsonResponse(listProdPerPage, safe=False,  status=status.HTTP_202_ACCEPTED)


class ProductInfor(generics.GenericAPIView):
    serializer_class = ProductInformationSerializer
    token_param_config = openapi.Parameter('product_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        header = {  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
                    'referer': None}
        product_id = request.GET.get('product_id')
        url_id = 'https://tiki.vn/api/v2/products/'+product_id
        header['referer'] = url_id
        try:
            product_info = requests.get(url_id,headers=header).json()
            soup = BeautifulSoup(product_info['description'],features="html.parser")
            result = utils.showProductByID(product_id)
            result['description'] = soup.get_text('\n')
            return  JsonResponse(result, safe=False,  status=status.HTTP_202_ACCEPTED)
        except:
            return JsonResponse({}, safe=False,  status=status.HTTP_404_NOT_FOUND)
            
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # so many kind of response
        if request.user.is_authenticated:
            if data['command'] == 'rating':
                try:
                    
                    utils.update_rating((int)(data['product_id']),data['rating'])
                    return JsonResponse({}, safe=False,  status=status.HTTP_202_ACCEPTED)
                except:
                    return JsonResponse({}, safe=False,  status=status.HTTP_406_NOT_ACCEPTABLE)
            elif data['command'] == 'shopping':
                try:   
                    utils.update_cart(request.user.id,(int)(data['product_id']),data['quantity'])
                    return JsonResponse({'status':202}, safe=False,  status=status.HTTP_202_ACCEPTED)
                except:
                    return JsonResponse({}, safe=False,  status=status.HTTP_406_NOT_ACCEPTABLE)
            elif data['command'] == 'sameproduct':
                try:
                    result = utils.find_product_same_category((int)(data['product_id']))
                    return JsonResponse(result, safe=False,  status=status.HTTP_202_ACCEPTED)
                except:
                    return JsonResponse({}, safe=False,  status=status.HTTP_406_NOT_ACCEPTABLE)
        else :
            return JsonResponse({}, safe=False,  status=status.HTTP_404_NOT_FOUND)
        
class ShoppingCart(generics.GenericAPIView):
    # serializer_class = UserSerializer

    def get(self, request):
        
        # serializer = self.serializer_class(data=request.data)
        # page = request.GET.get('page')
        # order_by = request.GET.get('order')
        
        if not request.user.is_authenticated:
            product_id = request.GET.get('product_id')
            
            return  JsonResponse({}, safe=False,  status=status.HTTP_404_NOT_FOUND)
        else :
            'TODO'
            # main page with sign in -> need to implement recommendation system
            

        


class GoogleSocialAuthView(GenericAPIView):

    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """
        POST with "auth_token"
        Send an idtoken as from google to get user information
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data, status=status.HTTP_200_OK)



class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = ['http', 'https']


class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'Hi '+user.username + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}
        utils.create_cart(email=request.data['email'])
        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(jwt=token,algorithms=["HS256"],key= os.getenv('SECRET_KEY'))
            print(payload)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)



class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
