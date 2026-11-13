from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import folium
from folium import Element, DivIcon
from datetime import datetime
import urllib.request
import json
from .models import Perfil, Alerta
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import localtime
from django.http import JsonResponse

def index(request):
    nombres_completos = {
        'robo': 'Robo / Hurto',
        'vandalismo': 'Vandalismo',
        'desorden': 'Desorden',
        'emergencia': 'Emergencia',
        'incendio': 'Incendio',
        'comercio': 'Comercio Irregular'
    }

    iconos_cat = {
        'Robo / Hurto': '🕵️',
        'Robo': '🕵️',
        'Vandalismo': '💥',
        'Desorden': '👥',
        'Emergencia': '🚑',
        'Incendio': '🔥',
        'Comercio Irregular': '🏪',
        'Comercio': '🏪'
    }

    if request.method == "POST" and request.user.is_authenticated:
        cat_raw = request.POST.get("categoria", "")
        urgencia = request.POST.get("urgencia", "")
        armas_texto = request.POST.get("armas") == "on"  # Ahora guardamos True/False en la bd
        lat = request.POST.get("lat", "")
        lon = request.POST.get("lon", "")
        
        if lat and lon:
            categoria_formateada = nombres_completos.get(cat_raw, cat_raw.capitalize())
            
            direccion_exacta = f"Lat: {str(lat)[:7]}, Lon: {str(lon)[:7]}" 
            try:
                url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                respuesta = urllib.request.urlopen(req, timeout=3.0)
                datos = json.loads(respuesta.read().decode('utf-8'))
                
                if 'display_name' in datos:
                    partes_direccion = datos['display_name'].split(',')
                    direccion_exacta = ", ".join(partes_direccion[:2]).strip()
            except Exception:
                pass
            
            # GUARDAMOS LA ALERTA DE FORMA PERMANENTE
            Alerta.objects.create(
                usuario=request.user,
                categoria=categoria_formateada,
                urgencia=urgencia,
                armas=armas_texto,
                lat=float(lat),
                lon=float(lon),
                direccion=direccion_exacta
            )
            return redirect('index')

    mapa = folium.Map(
        location=[-33.0472, -71.6271],
        zoom_start=15,
        min_zoom=14,
        max_bounds=True,
        min_lat=-33.0700,
        max_lat=-33.0100,
        min_lon=-71.6500,
        max_lon=-71.5600,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri"
    )
    
    colores_hex = {
        'Alta': '#ff3b30',
        'Media': '#ff9500',
        'Baja': '#ffcc00'
    }

    limite_tiempo = timezone.now() - timedelta(days=1)
    
    Alerta.objects.filter(fecha_creacion__lt=limite_tiempo).delete()
    alertas_db = Alerta.objects.all().order_by('fecha_creacion','id')
    
    lista_alertas_historial = []
    
    for alerta in alertas_db:
        cat = alerta.categoria
        urg = alerta.urgencia
        armas_bool = alerta.armas
        lat = alerta.lat
        lon = alerta.lon
        fecha_local = localtime(alerta.fecha_creacion)
        hora = fecha_local.strftime('%H:%M')
        fecha = fecha_local.strftime('%d/%m/%Y')
        direccion = alerta.direccion
        emoji = iconos_cat.get(cat, '⚠️')
        armas_str = "¡SÍ!" if armas_bool else "No"
        
        color_fondo = colores_hex.get(urg, '#007bff')
        
        texto_hover = f"{emoji} {cat} | {fecha} {hora} | Urgencia: {urg}"
        texto_popup = f"<div style='text-align:center; min-width:140px; font-family:sans-serif;'><b>{emoji} {cat}</b><br>Fecha: {fecha}<br>Hora: {hora}<br>Urgencia: {urg}<br>Armas: {armas_str}</div>"

        icono_personalizado = DivIcon(
            icon_size=(36, 36),
            icon_anchor=(18, 18),
            html=f"<div style='background-color:{color_fondo}; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; border:2px solid white; box-shadow:0 3px 6px rgba(0,0,0,0.4);'>{emoji}</div>"
        )

        folium.Marker(
            location=[lat, lon],
            tooltip=texto_hover,
            popup=folium.Popup(texto_popup, max_width=250),
            icon=icono_personalizado
        ).add_to(mapa)

        # Preparamos los datos del creador para el historial lateral
        nombre_completo = f"{alerta.usuario.first_name} {alerta.usuario.last_name}".strip()
        if not nombre_completo:
            nombre_completo = alerta.usuario.username
            
        nombre_negocio = None
        if hasattr(alerta.usuario, 'perfil'):
            nombre_negocio = alerta.usuario.perfil.nombre_negocio

        lista_alertas_historial.append({
            'emoji': emoji,
            'categoria': cat,
            'urgencia': urg,
            'armas': armas_str,
            'direccion': direccion,
            'fecha': fecha,
            'hora': hora,
            'emisor': nombre_completo,
            'negocio': nombre_negocio
        })

    script_inyectado = """
    <script>
        setTimeout(function(){
            var map_instance;
            for (var key in window) {
                if (key.startsWith('map_')) { map_instance = window[key]; break; }
            }
            if (map_instance) {
                if (map_instance.zoomControl) {
                    map_instance.zoomControl.setPosition('bottomright');
                }

                var marcador_temporal = null;
                map_instance.on('click', function(e) {
                    var pantallaAlerta = window.parent.document.getElementById('pantalla-alerta');
                    if (pantallaAlerta && pantallaAlerta.style.display !== 'flex') { return; }

                    if (marcador_temporal) { map_instance.removeLayer(marcador_temporal); }
                    marcador_temporal = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map_instance);
                    window.parent.postMessage({lat: e.latlng.lat, lon: e.latlng.lng}, "*");
                });
            }
        }, 1000);
    </script>
    """
    mapa.get_root().html.add_child(Element(script_inyectado))
    
    mapa_html = mapa._repr_html_()
    return render(request, "alertas/index.html", {"mapa_folium": mapa_html, "alertas": lista_alertas_historial})
def login_view(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'login':
            correo = request.POST.get('correo_login')
            pass_ingresada = request.POST.get('pass_login')
            
            user_obj = User.objects.filter(email=correo).first()
            
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=pass_ingresada)
                if user is not None:
                    login(request, user)
                    # CARGAMOS LOS DATOS Y LA EDAD EN LA SESIÓN DE FORMA SEGURA
                    perfil, created = Perfil.objects.get_or_create(usuario=user, defaults={'edad': 18})
                    request.session['edad'] = perfil.edad
                    request.session['nombre_completo'] = f"{user.first_name} {user.last_name}"
                    request.session['nombre_negocio'] = perfil.nombre_negocio
                    return redirect('index')
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            else:
                messages.error(request, 'Este correo no está registrado.')
            return render(request, 'login.html')
            
        elif accion == 'registro':
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellidos')
            edad = request.POST.get('edad')
            tiene_negocio = request.POST.get('tiene_negocio') == 'on'
            nombre_negocio = request.POST.get('nombre_negocio') if tiene_negocio else None
            correo = request.POST.get('correo_reg')
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')
            
            # Validamos el mínimo de 6 caracteres
            if len(pass1) < 6:
                messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                return render(request, 'login.html')

            if pass1 != pass2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'login.html')
            if User.objects.filter(email=correo).exists():
                messages.error(request, 'Ya existe una cuenta con este correo.')
                return render(request, 'login.html')
                
            user = User.objects.create_user(username=correo, email=correo, password=pass1, first_name=nombre, last_name=apellidos)
            Perfil.objects.create(usuario=user, edad=int(edad), nombre_negocio=nombre_negocio)
            
            # CARGAMOS LOS DATOS EN LA SESIÓN TRAS REGISTRARSE
            request.session['edad'] = int(edad)
            request.session['nombre_completo'] = f"{nombre} {apellidos}"
            request.session['nombre_negocio'] = nombre_negocio
            
            login(request, user)
            return redirect('index')
            
    return render(request, 'login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('index')

def obtener_ultima_alerta(request):
    ultima = Alerta.objects.order_by('-id').first()
    if ultima:
        if ultima.usuario:
            nombre_completo = f"{ultima.usuario.first_name} {ultima.usuario.last_name}".strip()
            emisor = nombre_completo if nombre_completo else ultima.usuario.username
        else:
            emisor = "Anónimo"
            
        hora_local = timezone.localtime(ultima.fecha_creacion).strftime('%H:%M')
        texto_armas = "⚠️ Con armas involucradas" if ultima.armas else "Sin armas reportadas"
        
        return JsonResponse({
            'id': ultima.id,
            'categoria': ultima.categoria,
            'urgencia': ultima.urgencia,
            'lat': ultima.lat,
            'lon': ultima.lon,
            'direccion': ultima.direccion,
            'descripcion': f"📍 {ultima.direccion} — {texto_armas}",
            'emisor': emisor,
            'hora': hora_local,
        })
    return JsonResponse({'id': None})