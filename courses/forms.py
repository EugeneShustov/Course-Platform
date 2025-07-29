from django import forms
from courses.models import Quiz

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Файл")

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']