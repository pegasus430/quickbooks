from django.db import models
from django_quickbooks.models import QBDModelMixin
from uuid import uuid4, uuid1
# Create your models here.

class Customer(QBDModelMixin):
    
    quickbooks_identifier = models.BigIntegerField()
    name = models.CharField(max_length=100 , default = '')
    workspace_id = models.IntegerField()
    address1 = models.CharField(max_length=50 , default = '')
    address2 = models.CharField(max_length=50 , default = '', null = True)
    city = models.CharField(max_length=50 , default = '')
    state = models.CharField(max_length=5 , default = '')
    zip = models.CharField(max_length=10 , default = '')
    first_name = models.CharField(max_length=50 , null = True)
    last_name = models.CharField(max_length=50 , null = True)
    phone = models.CharField(max_length=50 , default = '')
    email = models.EmailField(max_length=50)
    created_on = models.DateTimeField(auto_now_add = True)
    modified_on = models.DateTimeField(auto_now = True)
    notes = models.CharField(max_length=50 , default = '' ,null = True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def to_qbd_obj(self, **fields):
        from django_quickbooks.objects import Customer as QBCustomer
        # map your fields to the qbd_obj fields
        return QBCustomer(Name=self.__str__(),
                          IsActive=True,
                          CompanyName=self.name,
                          FirstName=self.first_name,
                          LastName=self.last_name,
                          Phone=self.phone,
                          Email=self.email
                          )

    @classmethod			  
    def from_qbd_obj(cls, qbd_obj):
        # map qbd_obj fields to your model fields
        return cls(
            first_name=qbd_obj.Name,
	        phone=qbd_obj.Phone,
            qbd_object_id=qbd_obj.ListID,
            qbd_object_version=qbd_obj.EditSequence
        )

class Assets (QBDModelMixin):
    quickbooks_identifier = models.BigIntegerField()
    company_id = models.IntegerField()
    workspace_id = models.IntegerField()
    name = models.CharField(max_length=100 , default = '')
    address1 = models.CharField(max_length=50 , default = '')
    address2 = models.CharField(max_length=50 , default = '', null = True)
    city = models.CharField(max_length=50 , default = '')
    state = models.CharField(max_length=5 , default = '')
    zip = models.CharField(max_length=10 , default = '')
    first_name = models.CharField(max_length=50 , null = True)
    last_name = models.CharField(max_length=50 , null = True)
    phone = models.CharField(max_length=50 , default = '')
    email = models.EmailField(max_length=50)
    notes = models.CharField(max_length=50 , default = '' ,null = True)
    created_on = models.DateTimeField(auto_now_add = True)
    modified_on = models.DateTimeField(auto_now = True)

class Items(QBDModelMixin):
    quickbooks_identifier = models.BigIntegerField()
    workspace_id = models.IntegerField()
    name = models.CharField(max_length=100 , default = '')
    part_number = models.CharField(max_length=100 , default = '')
    label = models.CharField(max_length=100 , default = '')
    plural_label = models.CharField(max_length=100 , default = '')
    type = models.CharField(max_length=50 , default = '')
    cost = models.IntegerField()
    category_id = models.IntegerField()
    last_name = models.CharField(max_length=50 , null = True)
    notes = models.CharField(max_length=50 , default = '' ,null = True)
    created_on = models.DateTimeField(auto_now_add = True)
    modified_on = models.DateTimeField(auto_now = True)

class Qwc(models.Model):

    class Qb_type(models.TextChoices):
        QBFS = 'QBFS'
        QBPOS = 'QBPOS'
    app_name = models.CharField(max_length=50 , default = "")
    app_id = models.CharField(max_length=10 , default = "")
    app_url = models.CharField(max_length=100 , default = "")
    app_description = models.TextField(default = "")
    username = models.CharField(max_length = 100 , default = "")
    owner_id = models.UUIDField(editable=False, default=uuid4)
    file_id = models.UUIDField(editable=False, default=uuid4)
    qbtype = models.CharField(
        max_length = 10 , 
        choices=Qb_type.choices,
        default=Qb_type.QBFS,
    )
    run_every_minutes = models.PositiveSmallIntegerField(default=5 , null=False)
