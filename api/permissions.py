from rest_framework.permissions import BasePermission

class EsCreadorDeQuiniela(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creada_por == request.user