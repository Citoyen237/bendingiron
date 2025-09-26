from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
# from usesOrders.models import Order
# Create your models here.

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=200)
    is_partenaire = models.BooleanField(default=0)
    groups = models.ManyToManyField(Group, related_name="customuser_set")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_set")
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
    
    @property
    def nb_commande(self):
        return self.order_set.count()
    
    @property
    def montant(self):
        total =sum(item.net_payer for item in self.order_set.all())
        return round(total)
