from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    friends = models.ManyToManyField(User, related_name='friends')
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} ({self.email})'

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(
        UserProfile, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        UserProfile, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"From: {self.sender} | To: {self.receiver} | Status: {self.status}"

    def accept(self):
        if self.status == 'pending':
            self.status = 'accepted'
            self.sender.friends.add(self.receiver.user)
            self.receiver.friends.add(self.sender.user)
            self.save()

    def reject(self):
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
