from typing import Any, Dict
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView

from courses.models import Course
from .forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    """
    Allows students to register.
    """

    template_name  = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')
    
    
    def form_valid(self, form):
        # Override the form_valid() method to log the user in
        # after they have successfully registered.
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password'])
        login(self.request, user)
        return result
    
    
class StudentEnrollCourseView(LoginRequiredMixin,
                              FormView):
    """
    Required the users to be logged in order to
    enroll in to courses.
    """
    course = None
    form_class = CourseEnrollForm
    
    def form_valid(self, form):
        # Retrieves the 'course' field from 
        # the cleaned form date. Then add 
        # the current user to the course.
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redired the user to student_course_detail 
        # after the form is successfuly valid.
        return reverse_lazy('student_course_detail',
                            args=[self.course.id])
        


class StudentCourseListView(LoginRequiredMixin, 
                            ListView):
    """
    Display a list of courses that the students 
    are enrolled in.
    """
    model = Course
    template_name = 'students/course/list.html'
    
    def get_queryset(self):
        # Filter the QuerySet by the student's ManyToMany
        # field to retrieve only the courses that the 
        # current user is enrolled in.
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])
    
    
    
    
class StudentCourseDetailView(DetailView):
    """
    Display the first module or the given module 
    id of the course that the current user is 
    enrolled in.
    """
    model = Course
    template_name = 'students/course/detail.html'
    
    def get_queryset(self):
        # Retrieve only the courses that the 
        # current user os enrolled in.
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        # If the module_id is in the URL parameter, get
        # the module with the given id, otherwise get 
        # the first module of the course.
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = course.modules.all().first()
        return context
                         
    
    