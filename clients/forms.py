from django import forms
from django.contrib.auth.models import Group
from scorm.models import ScormAsset, ScormAssignment

from accounts.models import CustomUser

from .models import Client


class ClientCreationForm(forms.ModelForm):
    username = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = Client
        fields = [
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "email",
            "contact_phone",
            "company",
            "domains",
            "lms_url",
            "lms_api_key",
            "lms_api_secret",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            self.add_error("password2", "Passwords do not match")

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            self.cleaned_data["username"],
            self.cleaned_data["email"],
            self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )
        user.groups.add(Group.objects.get(name="clientadmin"))
        user.is_client_admin = True
        user.save()

        client = super().save(commit=False)
        client.user = user
        if commit:
            client.save()
        return client


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "email", "contact_phone", "company", "domains"]

    def save(self, commit=True):
        client = super().save(commit=False)
        user = client.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            client.save()
        return client

class ClientLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    

class ClientUserForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    scorm = forms.ModelChoiceField(queryset=ScormAsset.objects.none())  # Empty initial queryset

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client', None)
        super(ClientUserForm, self).__init__(*args, **kwargs)
        if client:
            # Get the ScormAsset objects that are assigned to the client
            assigned_scorms = ScormAssignment.objects.filter(client=client).values_list('scorm_asset', flat=True)
            self.fields['scorm'].queryset = ScormAsset.objects.filter(id__in=assigned_scorms)