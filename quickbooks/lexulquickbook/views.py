# from curses.ascii import HT
from django.shortcuts import render

from rest_framework import generics
from .models import Customer
from .models import Qwc
from .serializers import CustomerSerializer
from .serializers import QwcSerializer
import json
from django.http import HttpResponse
from django.views import View
from django_quickbooks.models import create_qwc, Realm
import requests
from django.shortcuts import redirect
from django_quickbooks import QUICKBOOKS_ENUMS
from quickbooks.settings import LEXUL_API_URL, LEXUL_API, APP_URL
from requests.structures import CaseInsensitiveDict

from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User,Permission
from django.contrib.contenttypes.models import ContentType

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerDetail(generics.UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class QwcList(generics.ListCreateAPIView):
    queryset = Qwc.objects.all()
    serializer_class = QwcSerializer

    def post(self, request, *args, **kwargs):
        req = request.body.decode('utf-8')
        req = json.loads(req)
        qwc = Qwc.objects.create(username=req['username'], qbtype=req['qbtype'], run_every_minutes=req['run_every_minutes'])
        qwc.save()
        try:
            realm = Realm.objects.filter(id = qwc.username).first()
        except:
            return HttpResponse("The user is not existed.")

        qwc_xml = create_qwc(
            realm,
            owner_id = qwc.owner_id,
            file_id = qwc.file_id,
            qb_type = qwc.qbtype,
            schedule_n_minutes = qwc.run_every_minutes
        )
        response = HttpResponse(qwc_xml)
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename=quickbooks.qwc'
        return response

class Login(View):

    def get(self, request, *args, **kwargs):
       
        context = {'app_url': APP_URL}
        return render(request, "login.html", context=context)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username','')
        password = request.POST.get('password','')

        res = requests.post(f'{LEXUL_API_URL}api/auth/login/', json = {"username": username, "password": password})
        user = json.loads(res.text)
        if "error" in user.keys():
            response = HttpResponse('error')
        else:

            realm = None
            realms = Realm.objects.filter(name=username)

            if realms.count() > 0:
                realm = realms[0]
            
            if realm == None:
                realm = Realm.objects.create(name=username, is_active=True, token=user['token'])
                realm.set_password(password)
                realm.save()
            else:
                
                realm.token = user['token']
                realm.set_password(password)

                realm.save()


            response = HttpResponse(request.POST.get('username'))
            user = User.objects.filter(username=username).first()
            if user == None:
                user = User.objects.create_superuser(username=username, password=password)

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
            else:
                return HttpResponse("error")
        logger.info(f'{request.POST.get("username")} is logged in.')
        return response

class Home(View):

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            context = {'app_url': APP_URL}
            return render(request, "home.html", context=context)
        else:
            return redirect('/login/')
            

def download_qwc(request):
    if request.user.is_authenticated:
        realm = Realm.objects.filter(name = request.user.username).first()
    else:
        return redirect('/login/')

    qwc = Qwc.objects.create(username=realm.id, qbtype='QBFS', run_every_minutes=2)
    qwc.save()

    qwc_xml = create_qwc(
        realm,
        owner_id = qwc.owner_id,
        file_id = qwc.file_id,
        qb_type = qwc.qbtype,
        schedule_n_minutes = qwc.run_every_minutes
    )
    response = HttpResponse(qwc_xml)
    response['Content-Type'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename=quickbooks.qwc'
    
    return response

def log_out(request, *args, **kwargs):
    if request.user.is_authenticated:
        realm = Realm.objects.filter(name=request.user.username).first()
        logout(request)
        
        if realm != None:
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Authorization"] = f'TOKEN {realm.token}'
            res = requests.post(f'{LEXUL_API_URL}api/auth/logout/', headers=headers)

    return HttpResponse("")

def send_quickbook_to_lexul(resource, quickbook_obj, token):
    
    integration_id = quickbook_obj.ListID
    quickbook = {}

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f'TOKEN {token}' 
    
    if resource == QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER:
        resource_api = f'{LEXUL_API_URL}{LEXUL_API[resource]["resource_api"]}'
        get_api = f'{resource_api}?filter=integration_id:{integration_id}'
        post_api = f'{LEXUL_API_URL}{LEXUL_API[resource]["post_api"]}'
        patch_api = f'{LEXUL_API_URL}{LEXUL_API[resource]["post_api"]}'
        qb_data = vars(quickbook_obj)
        
        quickbook["integration_id"] = integration_id
        quickbook["name"] = qb_data["CompanyName"] if qb_data["CompanyName"] != None else ""
        
        get_workspace_api = f'{LEXUL_API_URL}{LEXUL_API["Workspace"]["get_api"]}'
        workspace = requests.get(get_workspace_api,headers=headers).json()

        if (isinstance(workspace, dict) and 'detail' in workspace.keys()) or len(workspace) == 0:
            quickbook["workspace_id"] = 10
        else:
            quickbook["workspace_id"] = workspace[0]['id']

        try:
            qb_bill_address = vars(quickbook_obj.BillAddress)
            quickbook["address1"] = qb_bill_address["Addr1"] if qb_bill_address["Addr1"] != None else ""
            quickbook["address2"] = qb_bill_address["Addr2"] if qb_bill_address["Addr2"] != None else ""
            quickbook["city"] = qb_bill_address["City"] if qb_bill_address["City"] != None else ""
            quickbook["state"] = qb_bill_address["State"] if qb_bill_address["State"] != None else ""
            quickbook["zip"] = qb_bill_address["PostalCode"] if qb_bill_address["PostalCode"] != None else ""
        except:
            quickbook["address1"] = ""
            quickbook["address2"] = ""
            quickbook["city"] = ""
            quickbook["state"] = ""
            quickbook["zip"] = ""
        
        quickbook["first_name"] = qb_data['FirstName'] if qb_data['FirstName'] != None else ""
        quickbook["last_name"] = qb_data['LastName'] if qb_data['LastName'] != None else ""
        quickbook["phone"] = qb_data['Phone'] if qb_data['Phone'] != None else ""
        quickbook["email"] = qb_data['Email'] if qb_data['Email'] != None else ""
        quickbook["created_on"] = qb_data['TimeCreated'] if qb_data['TimeCreated'] != None else ""
        quickbook["modified_on"] = qb_data['TimeModified'] if qb_data['TimeModified'] != None else ""
        quickbook["notes"] = ""
        
    else:
        resource_api = ""
    
    rexul_quickbook = requests.get(get_api,headers=headers).json()
    
    if 'detail' in rexul_quickbook.keys():
        logger.inf(f'token error')
    else:
        rexul_quickbook = rexul_quickbook['results']
        workspace_chk = False

        for k in range(0, len(rexul_quickbook)):
            if rexul_quickbook[k]['workspace_id'] == quickbook["workspace_id"]:
                rexul_quickbook = rexul_quickbook[k]
                workspace_chk = True
                break
        logger.info(f'{workspace_chk}')
        if workspace_chk == True:
            id = rexul_quickbook['id']
            quickbook['id'] = id
            patch_api = f'{patch_api}{quickbook["id"]}/'

            rexul_response = requests.patch(patch_api,json=quickbook,headers=headers)

        else:
            post_api = f'{post_api}{quickbook["workspace_id"]}/'
            rexul_response = requests.post(post_api,json=quickbook,headers=headers)

    return 'ok'