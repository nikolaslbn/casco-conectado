from django.shortcuts import render
import folium
from folium import Element, DivIcon
from datetime import datetime
import urllib.request
import json

def index(request):
    if 'alertas' not in request.session:
        request.session['alertas'] = []

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

    if request.method == "POST":
        cat_raw = request.POST.get("categoria", "")
        urgencia = request.POST.get("urgencia", "")
        armas_texto = "¡SÍ!" if request.POST.get("armas") else "No"
        lat = request.POST.get("lat", "")
        lon = request.POST.get("lon", "")
        
        if lat and lon:
            hora_actual = datetime.now().strftime("%H:%M")
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            categoria_formateada = nombres_completos.get(cat_raw, cat_raw.capitalize())
            emoji_asignado = iconos_cat.get(categoria_formateada, '⚠️')
            
            direccion_exacta = "Ubicación en el mapa"
            try:
                url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
                req = urllib.request.Request(url, headers={'User-Agent': 'CascoConectadoUSM/1.0'})
                respuesta = urllib.request.urlopen(req, timeout=3)
                datos = json.loads(respuesta.read().decode('utf-8'))
                
                if 'display_name' in datos:
                    partes_direccion = datos['display_name'].split(',')
                    direccion_exacta = ", ".join(partes_direccion[:2]).strip()
            except Exception:
                pass
            
            nueva_alerta = {
                'lat': float(lat),
                'lon': float(lon),
                'categoria': categoria_formateada,
                'urgencia': urgencia,
                'armas': armas_texto,
                'hora': hora_actual,
                'fecha': fecha_actual,
                'emoji': emoji_asignado,
                'direccion': direccion_exacta
            }
            request.session['alertas'].append(nueva_alerta)
            request.session.modified = True

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

    alertas_guardadas = request.session.get('alertas', [])

    for alerta in alertas_guardadas:
        if alerta.get('categoria') == 'Comercio':
            alerta['categoria'] = 'Comercio Irregular'
        if alerta.get('categoria') == 'Robo':
            alerta['categoria'] = 'Robo / Hurto'

        cat = alerta['categoria']
        urg = alerta['urgencia']
        armas = alerta['armas']
        hora = alerta.get('hora', 'N/A')
        fecha = alerta.get('fecha', 'N/A')
        emoji = alerta.get('emoji', iconos_cat.get(cat, '⚠️'))
        direccion = alerta.get('direccion', 'Valparaíso (Registro antiguo)')
        
        alerta['emoji'] = emoji
        alerta['direccion'] = direccion
        
        color_fondo = colores_hex.get(urg, '#007bff')
        
        texto_hover = f"{emoji} {cat} | {fecha} {hora} | Urgencia: {urg}"
        texto_popup = f"<div style='text-align:center; min-width:140px; font-family:sans-serif;'><b>{emoji} {cat}</b><br>Fecha: {fecha}<br>Hora: {hora}<br>Urgencia: {urg}<br>Armas: {armas}</div>"

        icono_personalizado = DivIcon(
            icon_size=(36, 36),
            icon_anchor=(18, 18),
            html=f"<div style='background-color:{color_fondo}; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; border:2px solid white; box-shadow:0 3px 6px rgba(0,0,0,0.4);'>{emoji}</div>"
        )

        folium.Marker(
            location=[alerta['lat'], alerta['lon']],
            tooltip=texto_hover,
            popup=folium.Popup(texto_popup, max_width=250),
            icon=icono_personalizado
        ).add_to(mapa)

    request.session['alertas'] = alertas_guardadas
    request.session.modified = True

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
    return render(request, "alertas/index.html", {"mapa_folium": mapa_html, "alertas": alertas_guardadas})