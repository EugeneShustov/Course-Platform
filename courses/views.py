from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, FormView, UpdateView
from django.views.generic.edit import CreateView

from courses.models import Enrollment, Module, Course, Progress

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

        if user.is_authenticated:
            enrolled_ids = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
            context['enrolled_courses'] = set(enrolled_ids)
        else:
            context['enrolled_courses'] = set()

        return context


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    already = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not already:
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

    messages.success(request, f"Модуль {module.title} выполненный")
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
        course = Course.objects.get(pk=self.kwargs['pk'])
        form.instance.course = course
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


