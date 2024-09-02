from django import forms
from core.models import UserProfile, FriendRequest

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'gender']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        if UserProfile.objects.filter(email=cleaned_data.get('email').lower()).exists():
            self.add_error('email', 'Email already exists.')

        return cleaned_data


class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        fields = ['sender', 'receiver']

    def clean(self):
        cleaned_data = super().clean()
        sender = cleaned_data.get('sender')
        receiver = cleaned_data.get('receiver')

        if sender == receiver:
            self.add_error('receiver', 'You cannot send a friend request to yourself.')

        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            self.add_error('receiver', 'Friend request already sent.')

        return cleaned_data
