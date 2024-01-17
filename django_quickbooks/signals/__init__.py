from django.dispatch import Signal

qbd_task_create = Signal([
    "qb_operation",
    "qb_resource",
    "object_id",
    "content_type",
    "realm_id",
    "instance",
])

customer_created = Signal(["qbd_model_mixin_obj", "realm_id"])
customer_updated = Signal(["qbd_model_mixin_obj", "realm_id"])
invoice_created = Signal(["qbd_model_mixin_obj", "realm_id"])
invoice_updated = Signal(["qbd_model_mixin_obj", "realm_id"])
realm_authenticated = Signal(["realm"])
qbd_first_time_connected = Signal(["realm_id"])

from django_quickbooks.signals.customer import *
from django_quickbooks.signals.invoice import *
from django_quickbooks.signals.qbd_task import *
