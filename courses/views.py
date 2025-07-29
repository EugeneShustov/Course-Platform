from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, FormView, UpdateView
from django.views.generic.edit import CreateView
from courses.models import Enrollment, Module, Course, Progress, Quiz, Answer, QuizResult, Question, QuizAttempt
from courses.utils import parse_quiz_file
from rapidfuzz import fuzz
from courses.forms import UploadFileForm
from django.db import transaction

class DashboardView(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = 'dashboard.html'
    login_url = 'login'
    context_object_name = 'enrollments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrollments'] = Enrollment.objects.filter(student=self.request.user)
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def post(self, request):
        self.object = self.get_object()
        module_id = request.POST.get('delete_module_id')
        if module_id and self.object.owner == request.user:
            Module.objects.filter(id=module_id, course=self.object).delete()
        return redirect('course_detail', pk=self.object.pk)

class CourseListView(ListView):
    model = Course
    template_name = 'courses/courses_list.html'
    context_object_name = 'courses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enrolled_ids = Enrollment.objects.filter(student=user).values_list('course_id', flat=True) if user.is_authenticated else []
        context['enrolled_courses'] = set(enrolled_ids)
        return context

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('login')

@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, "Вы успешно записались на курс")
    else:
        messages.info(request, "Вы уже записаны на этот курс")
    return redirect('dashboard')

@login_required
@require_POST
def mark_module_complete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    Progress.objects.get_or_create(student=request.user, module=module)
    messages.success(request, f"Модуль {module.title} выполнен")
    return redirect('course_detail', pk=module.course.pk)

class EditCourseView(UpdateView):
    model = Course
    fields = ['title', 'description']
    template_name = 'edit_course.html'

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse('course_detail', kwargs={'pk': self.object.pk})

class AddModuleView(CreateView):
    model = Module
    fields = ['title', 'description']
    template_name = 'courses/add_module.html'

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course_detail', kwargs={'pk': self.kwargs['pk']})

class MyCoursesView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'my_courses.html'

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)

class CreateCourseView(CreateView):
    model = Course
    fields = ['title', 'description']
    template_name = 'create_course.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('my_courses')

def get_match_score(user_answer: str, correct_answer: str) -> float:
    return fuzz.token_set_ratio(user_answer.strip().lower(), correct_answer.strip().lower()) / 100.0

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    existing_result = QuizResult.objects.filter(quiz=quiz, student=request.user).first()
    if existing_result:
        existing_result.attempts.set(
            QuizAttempt.objects.filter(user=request.user, question__quiz=quiz)
        )
        return render(request, 'take_quiz.html', {
            'quiz': quiz,
            'already_taken': True,
            'result': existing_result
        })

    if request.method == 'POST':
        with transaction.atomic():
            score = 0
            result = QuizResult.objects.create(
                quiz=quiz,
                student=request.user,
                score=0
            )

            for question in questions:
                user_answer = request.POST.get(f'q{question.id}', '').strip()
                correct = question.answers.filter(is_correct=True).first()
                correct_text = correct.text if correct else ''

                match_score = get_match_score(user_answer, correct_text)
                is_correct = match_score >= 0.85

                attempt = QuizAttempt.objects.create(
                    user=request.user,
                    question=question,
                    answer=user_answer,
                    match_score=match_score,
                    is_correct=is_correct
                )

                attempt.selected_answer = type('AnswerView', (), {'text': user_answer})()
                attempt.correct_answer = correct
                attempt.save()

                result.attempts.add(attempt)

                if is_correct:
                    score += 1

            result.score = round((score / questions.count()) * 100, 2)
            result.save()

        return render(request, 'take_quiz.html', {
            'quiz': quiz,
            'already_taken': True,
            'result': result
        })

    # Первый GET-запрос
    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })
class CreateQuizView(LoginRequiredMixin, CreateView):
    model = Quiz
    fields = ['title', 'description']
    template_name = 'courses/create_quiz.html'

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        form.save()
        messages.success(self.request, "Тест создан")
        return redirect('course_detail', pk=form.instance.course.pk)

class EditQuizView(LoginRequiredMixin, UpdateView):
    model = Quiz
    fields = ['title', 'description']
    template_name = 'courses/edit_quiz.html'

    def get_queryset(self):
        return Quiz.objects.all()

    def get_success_url(self):
        return reverse('course_detail', kwargs={'pk': self.object.course.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        question_flags = {
            question.id: question.answers.filter(is_correct=True).exists()
            for question in quiz.questions.all()
        }
        context['question_flags'] = question_flags
        context['import_form'] = UploadFileForm()
        return context

class CourseFullCreateView(LoginRequiredMixin, CreateView):
    model = Course
    fields = ['title', 'description']
    template_name = 'create_full_course.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return redirect('edit_course_content', pk=form.instance.pk)

class EditCourseContentView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'edit_course_content.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)

class ImportQuizQuestionsView(LoginRequiredMixin, FormView):
    form_class = UploadFileForm
    template_name = 'courses/import_questions.html'

    def form_valid(self, form):
        quiz = get_object_or_404(Quiz, pk=self.kwargs['quiz_id'], course__owner=self.request.user)
        file = form.cleaned_data['file']
        quiz.questions.all().delete()

        questions_data = parse_quiz_file(file)
        for q in questions_data:
            question = Question.objects.create(quiz=quiz, text=q['text'])
            for a in q['answers']:
                Answer.objects.create(
                    question=question,
                    text=a['text'],
                    is_correct=a.get('is_correct', False)
                )

        messages.success(self.request, "Вопросы успешно импортированы")
        return redirect('edit_quiz', pk=quiz.pk)

@login_required
@require_POST
def delete_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if quiz.course.owner != request.user:
        messages.error(request, "Вы не можете удалить этот тест")
    else:
        quiz.delete()
        messages.success(request, "Тест удалён")
    return redirect('course_detail', pk=quiz.course.pk)

@login_required
@require_POST
def auto_import_and_start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, course__owner=request.user)
    form = UploadFileForm(request.POST, request.FILES)

    if not form.is_valid():
        messages.error(request, "Файл не загружен")
        return redirect('edit_quiz', pk=quiz.pk)

    file = form.cleaned_data['file']

    quiz.questions.all().delete()
    QuizResult.objects.filter(quiz=quiz, student=request.user).delete()

    questions_data = parse_quiz_file(file)
    for q in questions_data:
        question = Question.objects.create(quiz=quiz, text=q['text'])
        for a in q['answers']:
            Answer.objects.create(
                question=question,
                text=a['text'],
                is_correct=a.get('is_correct', False)
            )

    messages.success(request, "Вопросы готовы, тест готов к повторному прохождению")
    return redirect('take_quiz', quiz_id=quiz.pk)

@login_required
@require_POST
def restart_quiz_for_user(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    QuizResult.objects.filter(quiz=quiz, student=request.user).delete()

    messages.success(request, f"Вы можете пройти тест \"{quiz.title}\" повторно")
    return redirect('take_quiz', quiz_id=quiz.id)

