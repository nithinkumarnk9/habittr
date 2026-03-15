from django.db import models
from datetime import date

class Habit(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date = models.DateField(default=date.today)
    
class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pinned = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100)
   

    def __str__(self):
        return self.title
    
class Password(models.Model):

    website = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.website
    
class Journal(models.Model):

    title = models.CharField(max_length=200)
    content = models.TextField()
    motivation = models.CharField(max_length=20)
    created = models.DateField(auto_now_add=True)
class Expense(models.Model):
    
    title = models.CharField(max_length=100)
    amount = models.FloatField()
    category = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"