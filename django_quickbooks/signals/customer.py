from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver

from django_quickbooks import get_realm_model, QUICKBOOKS_ENUMS
from django_quickbooks.signals import customer_created, customer_updated, qbd_task_create
from quickbooks.lexulquickbook.models import Customer
from django_quickbooks.models import QBDTask
RealmModel = get_realm_model()


@receiver(customer_created)
def create_qbd_customer(sender, qbd_model_mixin_obj, realm_id, *args, **kwargs):
    qbd_task_create.send(
        sender=qbd_model_mixin_obj.__class__,
        qb_operation=QUICKBOOKS_ENUMS.OPP_ADD,
        qb_resource=QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER,
        object_id=qbd_model_mixin_obj.id,
        content_type=ContentType.objects.get_for_model(qbd_model_mixin_obj),
        realm_id=realm_id,
    )


from django.db.models.signals import pre_delete, post_save
@receiver(post_save, sender=Customer)
def send_customer_to_qbtask(sender, instance, **kwargs):
	QBDTask.objects.create(qb_operation=QUICKBOOKS_ENUMS.OPP_QR,
                       qb_resource=QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER,
                       object_id=instance.id,
                       content_type=ContentType.objects.get_for_model(instance),
                       realm_id="5896429b-8fd9-4e02-bfa6-aca016c640cb"
                       )

@receiver(customer_updated)
def update_qbd_customer(sender, qbd_model_mixin_obj, realm_id, *args, **kwargs):
    qbd_task_create.send(
        sender=qbd_model_mixin_obj.__class__,
        qb_operation=QUICKBOOKS_ENUMS.OPP_MOD,
        qb_resource=QUICKBOOKS_ENUMS.RESOURCE_CUSTOMER,
        object_id=qbd_model_mixin_obj.id,
        content_type=ContentType.objects.get_for_model(qbd_model_mixin_obj),
        realm_id=realm_id,
    )
