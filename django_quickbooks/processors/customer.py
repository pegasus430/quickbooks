from django_quickbooks import QUICKBOOKS_ENUMS, qbwc_settings
from django_quickbooks.objects.customer import Customer
from django_quickbooks.processors.base import ResponseProcessor, ResponseProcessorMixin
from quickbooks.lexulquickbook.views import send_quickbook_to_lexul
LocalCustomer = qbwc_settings.LOCAL_MODEL_CLASSES['Customer']

class CustomerQueryResponseProcessor(ResponseProcessor, ResponseProcessorMixin):
    resource = QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER
    op_type = QUICKBOOKS_ENUMS.OPP_QR
    local_model_class = LocalCustomer
    obj_class = Customer

    def process(self, realm):
        cont = super().process(realm)
        if not cont: 
            return False
        recent_modified_time = None
        for customer_ret in list(self._response_body):
            customer = self.obj_class.from_lxml(customer_ret)
            if customer.Sublevel == '0':
                send_quickbook_to_lexul(self.resource, customer, realm.token)
            if recent_modified_time == None or recent_modified_time < customer.TimeModified:
                recent_modified_time = customer.TimeModified
        
        from datetime import datetime, timedelta
        # datetime object containing current date and time
        yesterday = datetime.today() - timedelta(days = 1 )
        tomorrow  = datetime.today() + timedelta(days = 1 )
        # dd/mm/YY H:M:S
        yesterday_str = yesterday.strftime("%Y-%m-%dT%H:%M:%S")
        tomorrow_str = tomorrow.strftime("%Y-%m-%dT%H:%M:%S")
        if recent_modified_time > tomorrow_str: recent_modified_time = yesterday_str

        if realm.last_updated_at == None or realm.last_updated_at < recent_modified_time:
            realm.last_updated_at = recent_modified_time
            realm.save()
        return True


class CustomerAddResponseProcessor(ResponseProcessor, ResponseProcessorMixin):
    resource = QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER
    op_type = QUICKBOOKS_ENUMS.OPP_ADD
    local_model_class = LocalCustomer
    obj_class = Customer

    def process(self, realm):
        cont = super().process(realm)
        if not cont:
            return False
        for customer_ret in list(self._response_body):
            customer = self.obj_class.from_lxml(customer_ret)
            local_customer = None
            if customer.Name:
                local_customer = self.find_by_name(customer.Name)

            if local_customer:
                self.update(local_customer, customer)
        return True


class CustomerModResponseProcessor(ResponseProcessor, ResponseProcessorMixin):
    resource = QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER
    op_type = QUICKBOOKS_ENUMS.OPP_MOD
    local_model_class = LocalCustomer
    obj_class = Customer

    def process(self, realm):
        cont = super().process(realm)
        if not cont:
            return False
        for customer_ret in list(self._response_body):
            customer = self.obj_class.from_lxml(customer_ret)
            local_customer = None
            if customer.ListID:
                local_customer = self.find_by_list_id(customer.ListID)
            elif not local_customer and customer.Name:
                local_customer = self.find_by_name(customer.Name)

            if local_customer:
                self.update(local_customer, customer)
        return True
