from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from courses import views
from courses.views import restart_quiz_for_user


urlpatterns = [
 path('admin/', admin.site.urls),
 path('', views.CourseListView.as_view(), name='course_list'),
 path('courses/', views.CourseListView.as_view(), name='course_list'),
 path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
 path('courses/<int:pk>/edit/', views.EditCourseView.as_view(), name='edit_course'),
 path('courses/<int:pk>/add-module/', views.AddModuleView.as_view(), name='add_module'),
 path('courses/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
 path('module/<int:pk>/complete/', views.mark_module_complete, name='mark_module_complete'),
 path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
 path('my-courses/', views.MyCoursesView.as_view(), name='my_courses'),
 path('create/', views.CreateCourseView.as_view(), name='create_course'),
 path('login/', LoginView.as_view(template_name='login.html'), name='login'),
 path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
 path('register/', views.RegisterView.as_view(), name='register'),
 path('course/<int:pk>/quiz/create/', views.CreateQuizView.as_view(), name='create_quiz'),
 path('quiz/<int:pk>/edit/', views.EditQuizView.as_view(), name='edit_quiz'),
 path('quiz/<int:quiz_id>/import/', views.ImportQuizQuestionsView.as_view(), name='import_questions'),
 path('quiz/<int:pk>/delete/', views.delete_quiz, name='delete_quiz'),
 path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
 path('quiz/<int:quiz_id>/import-and-run/', views.auto_import_and_start_quiz, name='auto_import_and_start_quiz'),
 path('quiz/<int:quiz_id>/restart/', restart_quiz_for_user, name='restart_quiz_for_user'),
]

