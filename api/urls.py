from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipoViewSet, RegistrarResultadoPartidoView, RankingQuinielaView, HacerEleccionView, EditarFechaLimiteView, EleccionesDeOtrosQuinielaView, EleccionCreateView, RegisterView, QuinielaListCreateView, UnirseQuinielaView, QuinielaRetrieveDestroyView, CrearPartidoView, DetalleQuinielaView, MisEleccionesView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
router = DefaultRouter()
router.register(r'equipos', EquipoViewSet, basename='equipos')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('quinielas/', QuinielaListCreateView.as_view(), name='quinielas'),
    path('quinielas/<int:quiniela_id>/unirse/', UnirseQuinielaView.as_view(), name='unirse-quiniela'),
    path('quinielas/<int:pk>/', QuinielaRetrieveDestroyView.as_view(), name='detalles-quiniela'),
    path('quinielas/<int:quiniela_id>/partidos/', CrearPartidoView.as_view(), name='crear-partido'),
    path('quinielas/<int:pk>/', DetalleQuinielaView.as_view()),
    path('elecciones/', EleccionCreateView.as_view()),
    path('quinielas/<int:quiniela_id>/mis-elecciones/', MisEleccionesView.as_view(), name='ver-mis-elecciones'),
    path('quinielas/<int:quiniela_id>/elecciones/', EleccionesDeOtrosQuinielaView.as_view(), name='ver-elecciones-quiniela'),
    path("quinielas/<int:pk>/editar-fecha-limite/", EditarFechaLimiteView.as_view(), name="editar-fecha-limite"),
    path("quinielas/<int:quiniela_id>/partidos/<int:partido_id>/elegir/", HacerEleccionView.as_view(), name="hacer-eleccion"),
    path("quinielas/<int:quiniela_id>/ranking/", RankingQuinielaView.as_view(), name="ranking-quiniela"),
    path("partidos/<int:partido_id>/resultado/", RegistrarResultadoPartidoView.as_view(), name="registrar-resultado-partido"),
]