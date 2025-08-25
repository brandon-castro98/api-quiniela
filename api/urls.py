from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CambiarMostrarEleccionesView, EquipoViewSet, RankingQuinielaView,
    EditarFechaLimiteView, EleccionesDeOtrosQuinielaView, EleccionCreateView,
    RegisterView, QuinielaListCreateView, UnirseQuinielaView,
    QuinielaRetrieveDestroyView, DetalleQuinielaView, MisEleccionesView,
    PartidoListCreateForQuinielaView, PartidoResultadoView, FCMTokenView,
    FCMTokenDetailView, TestNotificationView, TestAuthView
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'equipos', EquipoViewSet, basename='equipos')

urlpatterns = [
    path('', include(router.urls)),
    
    # Autenticación
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Quinielas
    path('quinielas/', QuinielaListCreateView.as_view(), name='quinielas'),
    path('quinielas/<int:pk>/', QuinielaRetrieveDestroyView.as_view(), name='detalles-quiniela'),
    path('quinielas/<int:quiniela_id>/unirse/', UnirseQuinielaView.as_view(), name='unirse-quiniela'),
    path('quinielas/<int:pk>/cambiar-mostrar-elecciones/', CambiarMostrarEleccionesView.as_view(), name='cambiar-mostrar-elecciones'),
    path('quinielas/<int:pk>/editar-fecha-limite/', EditarFechaLimiteView.as_view(), name='editar-fecha-limite'),
    path('quinielas/<int:quiniela_id>/ranking/', RankingQuinielaView.as_view(), name='ranking-quiniela'),
    
    # Partidos
    path('quinielas/<int:quiniela_id>/partidos/', PartidoListCreateForQuinielaView.as_view(), name='quiniela-partidos'),
    path('quinielas/<int:quiniela_id>/partidos/<int:partido_id>/resultado/', PartidoResultadoView.as_view(), name='quiniela-partido-resultado'),
    
    # Elecciones
    path('elecciones/', EleccionCreateView.as_view(), name='crear-elecciones'),
    path('quinielas/<int:quiniela_id>/mis-elecciones/', MisEleccionesView.as_view(), name='ver-mis-elecciones'),
    path('quinielas/<int:quiniela_id>/elecciones/', EleccionesDeOtrosQuinielaView.as_view(), name='ver-elecciones-quiniela'),
    
    # FCM (Firebase Cloud Messaging)
    path('fcm-tokens/', FCMTokenView.as_view(), name='fcm-tokens'),
    path('fcm-tokens/<int:token_id>/', FCMTokenDetailView.as_view(), name='fcm-token-detail'),
    path('test-notification/', TestNotificationView.as_view(), name='test-notification'),
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
]