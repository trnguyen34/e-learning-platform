from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.loader import render_to_string

from .fields import OrderField

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']
        
    def __str__(self):
        return self.title
    
class Course(models.Model):
    owner = models.ForeignKey(User,
                              related_name='couses_created',
                              on_delete=models.CASCADE)
    students = models.ManyToManyField(User,
                                      related_name='courses_joined',
                                      blank=True)
    subject = models.ForeignKey(Subject, 
                                related_name='courses',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
        
    def __str__(self):
        return self.title
    
class Module(models.Model):
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f'{self.order}. {self.title}'
    
class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':(
                                         'text',
                                         'video',
                                         'image',
                                         'file')})
    object_id = models.PositiveBigIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    
    class Meta:
        ordering = ['order']
    
class ItemBase(models.Model):
    owner = models.ForeignKey(User,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def render(self):
        # The render_to_string() method renders a template
        # and return the rendered content as a string.
        # self._meta.model_name is use to generate a template
        # for each content type model dynamically.
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item':self})
    
    class Mate:
        abstract = True
        
    def __str__(self):
        return self.title
    
class Text(ItemBase):
    content = models.TextField()
    
class File(ItemBase):
    pdf_file = models.FileField(upload_to='files')
    
class Image(ItemBase):
    image_file = models.FileField(upload_to='images')
    
class Video(ItemBase):
    url = models.URLField()
    
    
