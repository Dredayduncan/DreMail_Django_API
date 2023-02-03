from django.db import models
from django.utils.timezone import now

# Create your models here.
class EmailUser(models.Model):
  
    # Create the attributes for the user
    firstName = models.CharField(max_length=20, blank=False, null=False)
    lastName = models.CharField(max_length=20, blank=False, null=False)
    email = models.CharField(max_length=50, blank=False, null=False)
    password = models.CharField(max_length=100, default="", blank=False, null=False)
    avi = models.ImageField(upload_to="userImages/", null=True)


class EmailGroup(models.Model):
  
    # Create the attributes for the email group
    name = models.CharField(max_length=20, blank=False, null=False)
    description = models.CharField(max_length=150, null=False)

class UserEmailGroup(models.Model):
  
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
    recipient = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE, related_name="recipient")
    group = models.ForeignKey(to=EmailGroup, on_delete=models.CASCADE)
    dateSent = models.DateField(default=now, null=False, blank=False)
    unread = models.BooleanField(default=False)

class Favorites(models.Model):
    favoriter = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Junk(models.Model):
    junker = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class DeletedEmail(models.Model):
    deleter = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Spam(models.Model):
    spammer = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)

class Drafts(models.Model):
    drafter = models.ForeignKey(to=EmailUser, on_delete=models.CASCADE)
    emailTransfer = models.ForeignKey(to=EmailTransfer, on_delete=models.CASCADE)