from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='courses_joined', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.ManyToManyField(User, related_name='completed_modules', blank=True)

    def is_completed_by(self, user):
        return self.completed.filter(pk=user.pk).exists()

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"


class Progress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'module']


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    description = models.TextField(blank=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)
    attempts = models.ManyToManyField('QuizAttempt', related_name='results', blank=True)

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=1)
    answer = models.CharField(max_length=255, null=True, blank=True)
    match_score = models.FloatField(default=0.0)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)




