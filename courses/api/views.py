from django.shortcuts import get_object_or_404

from rest_framework import generics, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Subject, Course
from courses.api.serializers import SubjectSerializer, CourseSerializer

class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
    
class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    
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
    
       