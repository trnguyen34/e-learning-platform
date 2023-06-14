from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView

from .forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    """
    Allows students to register.
    """

    template_name  = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')
    
    def form_valid(self, form):
        """
        Override the form_valid() method to log the user in
        after they have successfully registered.
        """
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
        # Valid the form, then add the current user
        # to the course.
        self.course = form.cleaned_data['course']
        self.course.student.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redired the user to student_course_detail 
        # after the form is successfuly valid.
        return reverse_lazy('student_course_detail',
                            args=[self.course.id])

