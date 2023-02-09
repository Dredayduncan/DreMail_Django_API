from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

# Create your models here.
class CustomUser(AbstractUser):

    email = models.EmailField(_('email address'), unique=True)
    avi = models.ImageField(upload_to="userImages/", null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


    def __str__(self):
        return self.email



class EmailGroup(models.Model):
  
    # Create the attributes for the email group
    name = models.CharField(max_length=20, blank=False, null=False, unique=True)
    description = models.TextField(null=False)
    creator = models.ForeignKey(to=CustomUser, on_delete=models.DO_NOTHING)
    members = models.ManyToManyField(to=CustomUser, related_name="members")


class Email(models.Model):
    subject =  models.CharField(max_length=100, blank=False, null=False)
    message = models.TextField(blank=False)
    attachment = models.FileField(upload_to='attachments/')


class EmailTransfer(models.Model):
    email = models.ForeignKey(to=Email, on_delete=models.CASCADE)
    sender = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(null=True, to=CustomUser, on_delete=models.CASCADE, related_name="recipient")
    group = models.ForeignKey(null=True, to=EmailGroup, on_delete=models.CASCADE)
    dateSent = models.DateTimeField(default=now, null=False, blank=False)
    unread = models.BooleanField(default=True)
    

class Favorites(models.Model):
    favoriter = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Junk(models.Model):
    junker = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Trash(models.Model):
    deleter = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Spam(models.Model):
    spammer = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Drafts(models.Model):
    drafter = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    email = models.ForeignKey(to=Email, on_delete=models.CASCADE)