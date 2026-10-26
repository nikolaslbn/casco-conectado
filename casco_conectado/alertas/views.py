from django.shortcuts import render
import folium
from folium import Element, DivIcon

def index(request):
    if 'alertas' not in request.session:
        request.session['alertas'] = []

    if request.method == "POST":
        categoria = request.POST.get("categoria", "")
        urgencia = request.POST.get("urgencia", "")
        armas_texto = "¡SÍ!" if request.POST.get("armas") else "No"
        lat = request.POST.get("lat", "")
        lon = request.POST.get("lon", "")
        
        if lat and lon:
            nueva_alerta = {
                'lat': float(lat),
                'lon': float(lon),
                'categoria': categoria.capitalize(),
                'urgencia': urgencia,
                'armas': armas_texto
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
    
    iconos_cat = {
        'Robo': '🕵️',
        'Vandalismo': '💥',
        'Desorden': '👥',
        'Emergencia': '🚑',
        'Incendio': '🔥',
        'Comercio': '🏪'
    }
    
    colores_hex = {
        'Alta': '#ff3b30',
        'Media': '#ff9500',
        'Baja': '#ffcc00'
    }

    for alerta in request.session.get('alertas', []):
        cat = alerta['categoria']
        urg = alerta['urgencia']
        armas = alerta['armas']
        
        emoji = iconos_cat.get(cat, '⚠️')
        color_fondo = colores_hex.get(urg, '#007bff')
        
        texto_hover = f"{emoji} {cat} | Urgencia: {urg} | Armas: {armas}"
        texto_popup = f"<div style='text-align:center; min-width:140px; font-family:sans-serif;'><b>{emoji} {cat}</b><br>Urgencia: {urg}<br>Armas: {armas}</div>"

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

    script_inyectado = """
    <script>
        setTimeout(function(){
            var map_instance;
            for (var key in window) {
                if (key.startsWith('map_')) { map_instance = window[key]; break; }
            }
            if (map_instance) {
                // Mueve los botones de zoom hacia la esquina inferior derecha
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
    return render(request, "alertas/index.html", {"mapa_folium": mapa_html})