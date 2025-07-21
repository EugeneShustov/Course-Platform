from django.contrib import admin
from django.urls import path
from courses.views import CourseListView, CourseDetailView, DashboardView, RegisterView, CreateCourseView
from courses.views import enroll_course, mark_module_complete, EditCourseView, AddModuleView, MyCoursesView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
path('admin/', admin.site.urls),
path('', CourseListView.as_view(), name='course_list'),
path('courses/', CourseListView.as_view(), name='course_list'),
path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
path('courses/<int:pk>/edit/', EditCourseView.as_view(), name='edit_course'),
path('courses/<int:pk>/add-module/', AddModuleView.as_view(), name='add_module'),
path('courses/<int:pk>/enroll/', enroll_course, name='enroll_course'),
path('module/<int:pk>/complete/', mark_module_complete, name='mark_module_complete'),
path('dashboard/', DashboardView.as_view(), name='dashboard'),
path('my-courses/', MyCoursesView.as_view(), name='my_courses'),
path('create/', CreateCourseView.as_view(), name='create_course'),
path('login/', LoginView.as_view(template_name='login.html'), name='login'),
path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
path('register/', RegisterView.as_view(), name='register'),
]
