from django.core.management.base import BaseCommand
from api.models import Equipo

EQUIPOS = [
    {"nombre": "Arizona Cardinals", "abreviatura": "ARI", "ciudad": "Arizona", "logo_url": "https://upload.wikimedia.org/wikipedia/en/7/72/Arizona_Cardinals_logo.svg"},
    {"nombre": "Atlanta Falcons", "abreviatura": "ATL", "ciudad": "Atlanta", "logo_url": "https://upload.wikimedia.org/wikipedia/en/c/c5/Atlanta_Falcons_logo.svg"},
    {"nombre": "Baltimore Ravens", "abreviatura": "BAL", "ciudad": "Baltimore", "logo_url": "https://upload.wikimedia.org/wikipedia/en/1/16/Baltimore_Ravens_logo.svg"},
    {"nombre": "Buffalo Bills", "abreviatura": "BUF", "ciudad": "Buffalo", "logo_url": "https://upload.wikimedia.org/wikipedia/en/7/77/Buffalo_Bills_logo.svg"},
    {"nombre": "Carolina Panthers", "abreviatura": "CAR", "ciudad": "Carolina", "logo_url": "https://upload.wikimedia.org/wikipedia/en/1/1c/Carolina_Panthers_logo.svg"},
    {"nombre": "Chicago Bears", "abreviatura": "CHI", "ciudad": "Chicago", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Chicago_Bears_logo.svg"},
    {"nombre": "Cincinnati Bengals", "abreviatura": "CIN", "ciudad": "Cincinnati", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/8/81/Cincinnati_Bengals_logo.svg"},
    {"nombre": "Cleveland Browns", "abreviatura": "CLE", "ciudad": "Cleveland", "logo_url": "https://upload.wikimedia.org/wikipedia/en/d/d9/Cleveland_Browns_logo.svg"},
    {"nombre": "Dallas Cowboys", "abreviatura": "DAL", "ciudad": "Dallas", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/1/15/Dallas_Cowboys.svg"},
    {"nombre": "Denver Broncos", "abreviatura": "DEN", "ciudad": "Denver", "logo_url": "https://upload.wikimedia.org/wikipedia/en/4/44/Denver_Broncos_logo.svg"},
    {"nombre": "Detroit Lions", "abreviatura": "DET", "ciudad": "Detroit", "logo_url": "https://upload.wikimedia.org/wikipedia/en/7/71/Detroit_Lions_logo.svg"},
    {"nombre": "Green Bay Packers", "abreviatura": "GB", "ciudad": "Green Bay", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/5/50/Green_Bay_Packers_logo.svg"},
    {"nombre": "Houston Texans", "abreviatura": "HOU", "ciudad": "Houston", "logo_url": "https://upload.wikimedia.org/wikipedia/en/2/28/Houston_Texans_logo.svg"},
    {"nombre": "Indianapolis Colts", "abreviatura": "IND", "ciudad": "Indianapolis", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/0/00/Indianapolis_Colts_logo.svg"},
    {"nombre": "Jacksonville Jaguars", "abreviatura": "JAX", "ciudad": "Jacksonville", "logo_url": "https://upload.wikimedia.org/wikipedia/en/7/74/Jacksonville_Jaguars_logo.svg"},
    {"nombre": "Kansas City Chiefs", "abreviatura": "KC", "ciudad": "Kansas City", "logo_url": "https://upload.wikimedia.org/wikipedia/en/e/e1/Kansas_City_Chiefs_logo.svg"},
    {"nombre": "Las Vegas Raiders", "abreviatura": "LV", "ciudad": "Las Vegas", "logo_url": "https://upload.wikimedia.org/wikipedia/en/4/48/Las_Vegas_Raiders_logo.svg"},
    {"nombre": "Los Angeles Chargers", "abreviatura": "LAC", "ciudad": "Los Angeles", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Los_Angeles_Chargers_logo.svg"},
    {"nombre": "Los Angeles Rams", "abreviatura": "LAR", "ciudad": "Los Angeles", "logo_url": "https://upload.wikimedia.org/wikipedia/en/8/8a/Los_Angeles_Rams_logo.svg"},
    {"nombre": "Miami Dolphins", "abreviatura": "MIA", "ciudad": "Miami", "logo_url": "https://upload.wikimedia.org/wikipedia/en/3/37/Miami_Dolphins_logo.svg"},
    {"nombre": "Minnesota Vikings", "abreviatura": "MIN", "ciudad": "Minnesota", "logo_url": "https://upload.wikimedia.org/wikipedia/en/4/48/Minnesota_Vikings_logo.svg"},
    {"nombre": "New England Patriots", "abreviatura": "NE", "ciudad": "New England", "logo_url": "https://upload.wikimedia.org/wikipedia/en/b/b9/New_England_Patriots_logo.svg"},
    {"nombre": "New Orleans Saints", "abreviatura": "NO", "ciudad": "New Orleans", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/5/50/New_Orleans_Saints_logo.svg"},
    {"nombre": "New York Giants", "abreviatura": "NYG", "ciudad": "New York", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/6/60/New_York_Giants_logo.svg"},
    {"nombre": "New York Jets", "abreviatura": "NYJ", "ciudad": "New York", "logo_url": "https://upload.wikimedia.org/wikipedia/en/6/6b/New_York_Jets_logo.svg"},
    {"nombre": "Philadelphia Eagles", "abreviatura": "PHI", "ciudad": "Philadelphia", "logo_url": "https://upload.wikimedia.org/wikipedia/en/8/8e/Philadelphia_Eagles_logo.svg"},
    {"nombre": "Pittsburgh Steelers", "abreviatura": "PIT", "ciudad": "Pittsburgh", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Pittsburgh_Steelers_logo.svg"},
    {"nombre": "San Francisco 49ers", "abreviatura": "SF", "ciudad": "San Francisco", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/archive/3/3a/20250118072730%21San_Francisco_49ers_logo.svg"},
    {"nombre": "Seattle Seahawks", "abreviatura": "SEA", "ciudad": "Seattle", "logo_url": "https://upload.wikimedia.org/wikipedia/en/8/8e/Seattle_Seahawks_logo.svg"},
    {"nombre": "Tampa Bay Buccaneers", "abreviatura": "TB", "ciudad": "Tampa Bay", "logo_url": "https://upload.wikimedia.org/wikipedia/en/a/a2/Tampa_Bay_Buccaneers_logo.svg"},
    {"nombre": "Tennessee Titans", "abreviatura": "TEN", "ciudad": "Tennessee", "logo_url": "https://upload.wikimedia.org/wikipedia/en/c/c1/Tennessee_Titans_logo.svg"},
    {"nombre": "Washington Commanders", "abreviatura": "WAS", "ciudad": "Washington", "logo_url": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Washington_Commanders_logo.svg"}
]

class Command(BaseCommand):
    help = "Carga/actualiza los 32 equipos de la NFL con logo y ciudad."

    def handle(self, *args, **options):
        creados = 0
        actualizados = 0
        
        for e in EQUIPOS:
            try:
                # Intentar obtener el equipo existente
                equipo = Equipo.objects.get(abreviatura=e["abreviatura"])
                
                # Verificar si necesita actualización
                if (equipo.nombre != e["nombre"] or 
                    equipo.ciudad != e["ciudad"] or 
                    equipo.logo_url != e["logo_url"]):
                    
                    equipo.nombre = e["nombre"]
                    equipo.ciudad = e["ciudad"]
                    equipo.logo_url = e["logo_url"]
                    equipo.save()
                    actualizados += 1
                    self.stdout.write(f"✅ Actualizado: {equipo.nombre} ({equipo.abreviatura})")
                
            except Equipo.DoesNotExist:
                # Crear nuevo equipo si no existe
                Equipo.objects.create(
                    nombre=e["nombre"],
                    abreviatura=e["abreviatura"],
                    ciudad=e["ciudad"],
                    logo_url=e["logo_url"]
                )
                creados += 1
                self.stdout.write(f"🆕 Creado: {e['nombre']} ({e['abreviatura']})")
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS(
            f"\n🎯 RESUMEN: {creados} equipos creados, {actualizados} actualizados"
        ))
        
        total_equipos = Equipo.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"🎯 Total de equipos en BD: {total_equipos}/32"
        ))
        
        if total_equipos == 32:
            self.stdout.write(self.style.SUCCESS(
                "✅ ¡Todos los equipos NFL están listos!"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"⚠️  Se esperaban 32 equipos, pero hay {total_equipos}"
            ))