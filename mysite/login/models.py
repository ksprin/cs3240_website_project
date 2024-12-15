from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):
    report_name = models.CharField(max_length=200)
    report_description = models.CharField(
        max_length=1000, default="No description provided"
    )
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="reports/", null=True, blank=True)
    admin_message = models.TextField(
        null=True, blank=True
    )  # Message from admin upon approval/disapproval

    def delete(self, *args, **kwargs):
        if self.image:
            storage, name = self.image.storage, self.image.name
            super().delete(*args, **kwargs)
            storage.delete(name)
        else:
            super().delete(*args, **kwargs)

    def __str__(self):
        return self.report_name


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.ForeignKey("Report", null=True, on_delete=models.SET_NULL)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"


# new model
class UserScore(models.Model):
    info_for = models.CharField(max_length=200)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.info_for
from django.db import models
from django.utils.timezone import now

class Category(models.Model):
    category_text = models.CharField(max_length=200)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.category_text


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    answer_text = models.CharField(max_length=200)
    max_lat = models.DecimalField(max_digits=9, decimal_places=6)
    min_lat = models.DecimalField(max_digits=9, decimal_places=6)
    max_long = models.DecimalField(max_digits=9, decimal_places=6)
    min_long = models.DecimalField(max_digits=9, decimal_places=6)
    hint = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text

    
class GameInstance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=200)
    t_start = models.DateTimeField(default=now)
    t_end = models.DateTimeField(default=now)
    current_question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    hint_provided = models.BooleanField(default=False)
    guesses_used = models.IntegerField(default=0)
    has_won = models.BooleanField(default=False)

class QuestionSuggestion(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    answer_text = models.CharField(max_length=200)
    max_lat = models.DecimalField(max_digits=9, decimal_places=6)
    min_lat = models.DecimalField(max_digits=9, decimal_places=6)
    max_long = models.DecimalField(max_digits=9, decimal_places=6)
    min_long = models.DecimalField(max_digits=9, decimal_places=6)
    hint = models.CharField(max_length=200)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_message = models.TextField(   
        null=True, blank=True
    ) 

    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.question_text