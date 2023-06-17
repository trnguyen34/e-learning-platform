from django.shortcuts import get_object_or_404

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.api.permissions import IsEnrolled
from courses.api.serializers import (CourseSerializer,
                                     CourseWithContentsSerializer, 
                                     SubjectSerializer)
from courses.models import Subject, Course

class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
    
class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
    
class CourseEnrollView(APIView):
    # The users will be identified by the credential
    # set in the Authorization header of the HTTP
    # request.
    authentication_classes = [BasicAuthentication]
    # Unauthenticated users will not have access 
    # to this view.
    permission_classes = [IsAuthenticated]
    
    # Retrieve a Course object with the given pk 
    # in the URL parameter and add the current 
    # user to the students many-to-many 
    # relationship. Then, return a successful
    # response.
    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, pk=pk)
        course.students.add(request.user)
        return Response({'enrolled': True})
    
    
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    # detail=True to specify that this is an action
    # to be performed on a single object.
    @action(detail=True,
            methods=['post'],
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        # Use self.get_object() to get the current Course
        # object and add the current user to the students
        # many-to-many relationship. Then, return a 
        # successful response. 
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled': True})
       
    # Only students who are enrolled in the course
    # can have access to the course's contents
    # because of the custome permissions, IsEnrolled.
    @action(detail=True,
            methods=['get'],
            serializer_class=CourseWithContentsSerializer,
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated, IsEnrolled])
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)