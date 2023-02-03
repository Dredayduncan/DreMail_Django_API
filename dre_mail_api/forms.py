from django import forms, ModelForm
    
class EmailUserForm(ModelForm):
    class Meta:
        model = Email