from rest_framework import serializers

from courses.models import Subject, Course, Module, Content


class ModuleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class SubjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']
     
        
class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only = True)
    
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
                  'overview', 'created', 'owner',
                  'modules']
        
class ItemRalatedField(serializers.RelatedField):
    
    # to_representation() method takes the target of 
    # the field as the value argument (model instance)
    # and returns the representation should be used
    # to serialize the target.
    def to_representation(self, value):
        return value.render()
    
    
class ContentSerializer(serializers.ModelSerializer):
    item = ItemRalatedField(read_only=True)
    
    class Meta:
        model = Content
        fields = ['order', 'item']


class ModuleWithContentsSerializer(
                        serializers.ModelSerializer):
    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order', 'title', 'description',
                  'contents']


class CourseWithContentsSerializer(
                        serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
                  'overview', 'created', 'owner',
                  'modules']