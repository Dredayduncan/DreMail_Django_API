from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# Create your models here.
class EmailUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
  
    # Create the attributes for the user
    avi = models.ImageField(upload_to="userImages/", null=True, blank=True)

    def __str__(self):
        return str(self.user)


class EmailGroup(models.Model):
  
    # Create the attributes for the email group
    name = models.CharField(max_length=20, blank=False, null=False)
    description = models.TextField(null=False)

class EmailGroupMembers(models.Model):
  
    # Create the attributes for the user
    user = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    group = models.ForeignKey(to=EmailGroup, on_delete=models.CASCADE)

class Email(models.Model):
    subject =  models.CharField(max_length=100, blank=False, null=False)
    message = models.TextField(blank=False)
    attachment = models.FileField(upload_to='attachments/')

class EmailTransfer(models.Model):
    email = models.ForeignKey(to=Email, on_delete=models.CASCADE)
    sender = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(null=True, to=EmailUser, on_delete=models.CASCADE, related_name="recipient")
    group = models.ForeignKey(null=True, to=EmailGroup, on_delete=models.CASCADE)
    dateSent = models.DateTimeField(default=now, null=False, blank=False)
    unread = models.BooleanField(default=True)

class Favorites(models.Model):
    favoriter = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Junk(models.Model):
    junker = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Trash(models.Model):
    deleter = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Spam(models.Model):
    spammer = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Drafts(models.Model):
    drafter = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    email = models.ForeignKey(to=Email, on_delete=models.CASCADE)