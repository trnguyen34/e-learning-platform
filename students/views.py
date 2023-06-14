from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

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

