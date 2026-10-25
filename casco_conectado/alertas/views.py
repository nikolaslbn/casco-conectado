from django.shortcuts import render
import folium

def index(request):
    # Crea el mapa centrado en el casco histórico de Valparaíso
    mapa = folium.Map(location=[-33.0472, -71.6271], zoom_start=15, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", attr="Esri")
    
    # Transforma el mapa a código HTML
    mapa_html = mapa._repr_html_()
    
    # Manda el mapa hacia tu plantilla visual
    return render(request, "alertas/index.html", {"mapa_folium": mapa_html})