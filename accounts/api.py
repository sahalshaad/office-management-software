from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.models import Department, User
from accounts.serializers import DepartmentSerializer, ProfileSerializer, StaffCreateUpdateSerializer, UserSerializer
from accounts.services import send_verification_email
from core.permissions import IsAdminRole


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.select_related("manager").all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminRole]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related("department").all()
    permission_classes = [IsAuthenticated]
    search_fields = ["first_name", "last_name", "email", "employee_id", "department__name"]
    filterset_fields = ["role", "status", "department"]
    ordering_fields = ["first_name", "employee_id", "created_at"]

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return self.queryset
        return self.queryset.filter(pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.request.method in {"POST", "PUT", "PATCH"}:
            return StaffCreateUpdateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(self.request, user)

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminRole()]
        return super().get_permissions()

    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == "PATCH":
            serializer = ProfileSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
