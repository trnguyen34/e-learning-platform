from rest_framework.permissions import BasePermission

class IsEnrolled(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        # Return students who are enrolled in the course.
        return obj.students.filter(id=request.user.id).exists()