from spyne.decorator import rpc
from spyne.model.complex import Array, Unicode
from spyne.model.primitive import Integer, String
from spyne.service import ServiceBase

from django_quickbooks import QBWC_CODES, HIGHEST_SUPPORTING_QBWC_VERSION,get_session_manager_class, get_queue_manager_class
from django_quickbooks.models import QBDTask
from django_quickbooks.signals import realm_authenticated
from django_quickbooks import QUICKBOOKS_ENUMS
from requests.structures import CaseInsensitiveDict
from quickbooks.settings import LEXUL_API_URL, LEXUL_API, APP_URL
import requests
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class QuickBooksService(ServiceBase):

    @rpc(Unicode, Unicode, _returns=Array(Unicode))
    def authenticate(ctx, strUserName, strPassword):
        """
        Authenticate the web connector to access this service.

        @param strUserName user name to use for authentication
        @param strPassword password to use for authentication

        @return the completed array
        """
        logger.info(f'Quickbooks authenticate request is comming from {strUserName}')
        return_array = []
        realm = session_manager.authenticate(username=strUserName, password=strPassword)

        if realm and realm.is_active:
            realm_authenticated.send(sender=realm.__class__, realm=realm)

            if not session_manager.in_session(realm):
                headers = CaseInsensitiveDict()
                headers["Accept"] = "application/json"
                headers["Authorization"] = f'TOKEN {realm.token}' 
                get_workspace_api = f'{LEXUL_API_URL}{LEXUL_API["Workspace"]["get_api"]}'

                workspace = requests.get(get_workspace_api,headers=headers).json()

                if (isinstance(workspace, dict) and 'detail' in workspace.keys()):
                    logger.warning("Token is invalid.")
                    return_array.append(QBWC_CODES.NVU)
                    return_array.append(QBWC_CODES.NVU)
                    return return_array
                try:
                    qbd_current_task = QBDTask.objects.filter(realm_id=realm.id).first()
                    
                    if qbd_current_task == None:
                       
                        qbd_new_task = QBDTask.objects.create(qb_operation=QUICKBOOKS_ENUMS.OPP_QR_BY_DATE, qb_resource=QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER, realm_id = realm.id)
                        qbd_new_task.save()
                except:
                    logger.info(f'QBD Task Searching Issue.')
                session_manager.add_new_requests(realm)

                if session_manager.new_requests_count(realm) > 0:

                    ticket = session_manager.create_session(realm)
                    return_array.append(ticket)
                    return_array.append(QBWC_CODES.CC)
                else:
                    return_array.append(QBWC_CODES.NONE)
                    return_array.append(QBWC_CODES.NONE)

            else:
                return_array.append(QBWC_CODES.BUSY)
                return_array.append(QBWC_CODES.BUSY)
                logger.info(f'{realm.name} is working now.')
        else:
            return_array.append(QBWC_CODES.NVU)
            return_array.append(QBWC_CODES.NVU)
            logger.info(f'{strUserName} is not existed.')
        
        return return_array

    @rpc(Unicode, _returns=Unicode)
    def clientVersion(ctx, strVersion):
        """
        Evaluate the current web connector version and react to it.

        @param strVersion the version of the QB web connector

        @return string telling the web connector what to do next.
        """
        # TODO: add version checker for types: warning, error, ok
        return QBWC_CODES.CV

    @rpc(Unicode, _returns=Unicode)
    def closeConnection(ctx, ticket):
        """
        Tell the web service that the web connector is finished with the updated session.

        @param ticket the ticket from web connector supplied by web service during call to authenticate method
        @return string telling the web connector what to do next.
        """
        print('closeConnection(): ticket=%s' % ticket)
        realm = session_manager.get_realm(ticket)
        session_manager.close_session(realm)
        return QBWC_CODES.CONN_CLS_OK

    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def connectionError(ctx, ticket, hresult, message):
        """
        Tell the web service about an error the web connector encountered in its attempt to connect to QuickBooks
        or QuickBooks POS

        @param ticket the ticket from web connector supplied by web service during call to authenticate method
        @param hresult the HRESULT (in HEX) from the exception thrown by the request processor
        @param message The error message that accompanies the HRESULT from the request processor

        @return string value "done" to indicate web service is finished or the full path of the different company for
        retrying _set_connection.
        """
        print('connectionError(): ticket=%s, hresult=%s, message=%s' % (ticket, hresult, message))
        realm = session_manager.get_realm(ticket)
        session_manager.close_session(realm)
        return QBWC_CODES.CONN_CLS_ERR

    @rpc(Unicode, _returns=Unicode)
    def getLastError(ctx, ticket):
        """
        Allow the web service to return the last web service error, normally for displaying to user, before
        causing the update action to stop.

        @param ticket the ticket from web connector supplied by web service during call to authenticate method

        @return string message describing the problem and any other information that you want your user to see.
        The web connector writes this message to the web connector log for the user and also displays it in the web
        connector’s Status column.
        """
        print('getLastError(): ticket=%s' % ticket)
        return QBWC_CODES.UNEXP_ERR

    @rpc(Unicode, _returns=Unicode)
    def getServerVersion(ctx, ticket):
        """
        Provide a way for web-service to notify web connector of it’s version and other details about version

        @param ticket the ticket from web connector supplied by web service during call to authenticate method

        @return string message string describing the server version and any other information that user may want to see
        """
        print('getServerVersion(): version=%s' % HIGHEST_SUPPORTING_QBWC_VERSION)
        return HIGHEST_SUPPORTING_QBWC_VERSION

    @rpc(Unicode, _returns=Unicode)
    def interactiveDone(ctx, ticket):
        """
        Allow the web service to indicate to web connector that it is done with interactive mode.

        @param ticket the ticket from web connector supplied by web service during call to authenticate method

        @return string value "Done" should be returned when interactive session is over
        """
        print('interactiveDone(): ticket=%s' % ticket)
        return QBWC_CODES.INTR_DONE

    @rpc(Unicode, Unicode, _returns=Unicode)
    def interactiveRejected(ctx, ticket, reason):
        """
        Allow the web service to take alternative action when the interactive session it requested was
        rejected by the user or by timeout in the absence of the user.

        @param ticket the ticket from web connector supplied by web service during call to authenticate method
        @param reason the reason for the rejection of interactive mode

        @return string value "Done" should be returned when interactive session is over
        """
        print('interactiveRejected()')
        print(ticket)
        print(reason)
        return 'Interactive mode rejected'

    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ctx, ticket, response, hresult, message):
        """
        Return the data request response from QuickBooks or QuickBooks POS.

        @param ticket the ticket from web connector supplied by web service during call to authenticate method
        @param response qbXML response from QuickBooks or qbposXML response from QuickBooks POS
        @param hresult  The hresult and message could be returned as a result of certain errors that could occur when
        QuickBooks or QuickBooks POS sends requests is to the QuickBooks/QuickBooks POS request processor via the
        ProcessRequest call
        @param message The error message that accompanies the HRESULT from the request processor

        @return int a positive integer less than 100 represents the percentage of work completed. A value of 1 means one
        percent complete, a value of 100 means 100 percent complete--there is no more work. A negative value means an
        error has occurred and the Web Connector responds to this with a getLastError call.
        """
        logger.info(f'receiveResponseXML().')
        if hresult:
            print("hresult=" + hresult)
            print("message=" + message)

        return session_manager.process_response(ticket, response, hresult, message)

    @rpc(Unicode, Unicode, Unicode, Unicode, Integer, Integer, _returns=String)
    def sendRequestXML(ctx, ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers):
        logger.info(f'sendRequestXML() has been called.')  
        realm = session_manager.get_realm(ticket)
        request = session_manager.get_request(realm)
        session_manager.check_iterating_request(request, ticket)
        return request

    @rpc(Unicode, Unicode, _returns=Unicode)
    def interactiveUrl(ctx, ticket, sessionID):
        print('interactiveUrl')
        print(ticket)
        print(sessionID)
        return ''


QueueManager = get_queue_manager_class()
session_manager = get_session_manager_class()(queue_manager=QueueManager())
