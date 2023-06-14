from typing import Any, Dict
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms.models import modelform_factory
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from students.forms import CourseEnrollForm
from .models import Content, Course, Module, Subject
from .forms import ModuleFormset


class OwnerMixin:
    def get_queryset(self):
        """
        Override get_queryset() method to retrieve objects
        that belong to the current.
        """
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
    
    
class OwnerEditMixin:
    def form_valid(self, form):
        """ 
        Override the form_valid() method to automatically
        set the current user in thw owner attribute of
        the object being saved.
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)

    
class OwnerCourseMixin(OwnerMixin, 
                       LoginRequiredMixin, 
                       PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    
    
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'

class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'
    
    
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'

    
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None
    
    def get_formset(self, data=None):
        return ModuleFormset(instance=self.course,
                             data=data)
        
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)
    
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({
                                        'course': self.course,
                                        'formset': formset })
        
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({
                                        'course': self.course,
                                        'formset': formset})
        
        
class ContentCreateUpdateView(TemplateResponseMixin, View):
    """
    Create or update different models' form suck as text, video,
    image, or file.

    Args:
        TemplateResponseMixin (_type_): _description_
        View (_type_): _description_

    Returns:
        _type_: _description_
    """
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    
    def get_model(self, model_name):
        """
        Check that the given model name is one of the four
        models. Then use the get_model method from Django's
        apps to get the given model.
        """
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
            
        return None

    def get_form(self, model, *args, **kwargs):
        """
        Use modelform_factory to build a dynamic form
        based on the given model.
        """
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)
    
    def dispatch(self, request, module_id, model_name, id=None):
        """
        Args:
            request (_type_): _description_
            module_id: The ID for the module that the Content
                                is/will be associated with.
            model_name: The name of the content to create/update.
            id: The ID of the object that is being updated. If it's
                None, create a new ibjects. 

        """
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user,)
        return super().dispatch(request, module_id, model_name, id)
        
    def get(self, request, module_id, model_name, id=None):
        """
        Executed when a GET request is received. 
        """

        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})
        
    def post(self, request, module_id, model_name, id=None):
        """
        Executed when a POST request is received.
        """
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content 
                Content.objects.create(module=self.module, item=obj)
                return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                        'object': self.obj})
            

class ContentDeleteView(View):
    """
    Retrives a content object with the given id, and deletes
    the related objects like Text, Image, Video, and File. 
    After deleting all the related objects, it will delete
    the content object and redirects the user to the 
    module_content_list URL.

    Args:
        View (class): The parent of all views
    """
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)
    
    
class ModuleContentListView(TemplateResponseMixin, View):
    """
    Get a module object with the given id that belings
    to the current user.

    Args:
        TemplateResponseMixin (Mixin): Used to render a template
        View (Class): The parent class of all views

    Returns:
        Render a object to a template and return an HTTP response.
    """
    template_name = 'courses/manage/module/content_list.html'
    
    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})
    
    
class ModuleOrderView(CsrfExemptMixin,
                      JsonRequestResponseMixin,
                      View):
    """
    Allows to update the order of the course modules.

    Args:
        CsrfExemptMixin (InheritedMixin): Aviod checking CSRF token
            in POST request. 
        JsonRequestResponseMixin (InheritedMixin): Analyze the request
            data. If the request data is properly formatted, the JSON is saved
            to self.request_json as Python object. For the response, it will 
            serializes the response as JSON and returns an HTTP response with 
            the application/json content type
        View (class): Parent class for all views.
    """
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                                  course__owner=request.user).update(order=order)
        return self.render_json_response({'order': order})
    

class ContentOrderView(CsrfExemptMixin,
                       JsonRequestResponseMixin,
                       View):
    """ Allows to update the order of the content. """
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})
    

class CourseListView(TemplateResponseMixin, View):
    """
    Displays courses from all subjects or only courses to a given subject.
    
    Args:
        TemplateResponseMixin (mixin): Used to render a template.
        View (class): The parent class of all views.
    """
    model = Course
    template_name = 'courses/course/list.html'
    
    def get(self, request, subject=None):
        """
        Returns:
            Render the objects to a template and return an HTTP response.
        """
        
        # Retrieve all the subjects and courses by using the ORM's annotat()
        # method, then use the Count() aggregation function to get the toal
        # number of courses in each subject and the number of modules in each
        # course.
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))
        
        # if the subject is given, filter the courses by the subject
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        
        return self.render_to_response ({'subjects': subjects,
                                          'subject': subject,
                                          'courses': courses})
    
    
class CourseDetailView(DetailView):
    """
    Displays a single course overview.

    Args:
        DetailView (generic): Render a "detail" view of an object.
    """
    model = Course
    template_name = 'courses/course/detail.html'
    
    def get_context_data(self, **kwargs):
        """
        The get_context_data method will include the
        the enrollment form in the context for rendering
        the templates. The currrent Course object is 
        initalize with the hidden course field of the
        form.
        """
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
                                    initial={'course':self.object})
        return context
    
    
    
    
    