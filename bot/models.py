from django.contrib.auth.models import AbstractUser
from django.db import models
import re

class User(AbstractUser):
    full_name = models.CharField(max_length=200,null=True,blank=True)
    telegram_id = models.CharField(max_length=100,null=True,blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    
    def __str__(self):
        return self.full_name or f"user({self.pk})"



class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_id = models.CharField(max_length=100)
    url = models.URLField()
    title = models.CharField(max_length=300)
    keywords = models.TextField(null=True, blank=True)
    length = models.IntegerField(null=True,blank=True)
    chat_id = models.CharField(max_length=100,null=True,blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'youtube_id'], name='unique_user_video')]

    def __str__(self):
        return f"{self.title} ({self.user})"
    
    def get_keywords(self):
        if not self.keywords:
            return []
        
        keywords = [k.strip() for k in self.keywords.split(",") if k.strip()]
        clean_keywords = []
        for k in keywords:
            clean_k = re.sub(r"[^a-zA-Z0-9\u0400-\u04FF]", "", k).lower()
            if clean_k:
                clean_keywords.append(clean_k)
        return clean_keywords

        



class Comment(models.Model):
    video = models.ForeignKey(Video,on_delete=models.CASCADE)
    user_name = models.CharField(max_length=200,null=True,blank=True)
    youtube_id = models.CharField(max_length=100,null=True,blank=True)
    comment_id =models.CharField(max_length=100,null=True,blank=True)
    text = models.TextField(null=True,blank=True)
    sent_to_telegram = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_name or f"comment({self.pk})"
    
    






    


    


    