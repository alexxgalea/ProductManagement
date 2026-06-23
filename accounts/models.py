from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass
    
# gestiune
class Location(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.id} {self.name}"
    
    

class Membership(models.Model):
    #defining the choices
    class Role(models.TextChoices):
        owner = "PATRON", "Patron"
        manager = "MANAGER", "Manager"
        worker = "PERSONAL", "Personal"
        accountant = "CONTABIL", "Contabil"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.worker)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['user', 'location'],
                name = "uq_user_location"
            )
        ]

    def __str__(self):
        return f"{self.user} {self.location} {self.role}"

class AuditLog(models.Model):
    actor = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="audit_logs")
    action = models.CharField(max_length=120)
    target = models.CharField(max_length=120)
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL, related_name="audit_logs")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.actor} {self.action} {self.timestamp}"





