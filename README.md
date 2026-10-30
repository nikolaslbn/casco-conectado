# Casco Conectado - Entregable III (Grupo 11)

Aplicación web desarrollada en Django para el proyecto semestral **Casco Conectado** (Ámbito de Estrategia de Desarrollo Regional: Justicia social y desarrollo humano). Este sistema permite a los locatarios reportar incidentes de seguridad en tiempo real mediante un mapa interactivo y un panel de control con historial detallado.

## Integrantes del Grupo 11

* José Miranda
* Anthon Valenzuela
* Nicolás Labraña
* Tomás Martínez

## Características Principales

1. **Emisión de Alertas Dinámicas:** Interfaz de doble panel para seleccionar categorías de incidentes (*Robo / Hurto*, *Vandalismo*, *Desorden*, *Emergencia*, *Incendio*, *Comercio Irregular*), presencia de armas y niveles de urgencia (*Alta*, *Media*, *Baja*).
2. **Mapa Interactivo:** Desarrollado con Folium, Leaflet y proveedor de teselas **Esri World Street Map**, acotado específicamente a la zona de Valparaíso con marcadores personalizados mediante `DivIcon` y emojis representativos.
3. **Geocodificación Inversa:** Integración con la API pública de OpenStreetMap (Nominatim) para traducir automáticamente las coordenadas de los clics en el mapa a direcciones, calles e intersecciones reales de Valparaíso.
4. **Registro Histórico:** Pestaña de historial con tarjetas dinámicas organizadas en orden cronológico inverso, mostrando iconos, fechas, horas, direcciones exactas y niveles de urgencia con códigos de color.

## Tecnologías Utilizadas

* **Backend:** Python, Django (versión estándar de desarrollo local)
* **Librerías de Mapas:** Folium, Leaflet.js
* **Geocodificación:** OpenStreetMap Nominatim API
* **Frontend:** HTML5, CSS3 (diseño responsivo de doble panel), JavaScript (`postMessage` para comunicación entre marcos)

## Requisitos Previos y Dependencias

* Python (versión 3.8 o superior)
* Pip (gestor de paquetes de Python)

Las dependencias principales requeridas para ejecutar el proyecto son:

* `django`
* `folium`

## Instrucciones para Ejecutar Localmente

Sigue estos pasos en tu terminal para clonar el repositorio, configurar el entorno y levantar el servidor local:

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/nikolaslbn/casco-conectado.git
   cd casco-conectado
   ```

2. Instalar las dependencias:
   ```bash
   pip install django folium
   ```

3. Aplicar las migraciones de Django:
   ```bash
   python manage.py migrate
   ```

4. Ejecutar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

5. Acceder a la aplicación:
   Abre tu navegador web e ingresa a la siguiente dirección local:
   `http://127.0.0.1:8000/`

## Datos para Probar la Funcionalidad Corazón

1. Ingresa a la aplicación en `http://127.0.0.1:8000/` y haz clic en la pestaña superior "EMITIR ALERTA".
2. Selecciona una categoría de incidente (por ejemplo, *Robo / Hurto* o *Comercio Irregular*).
3. Marca la casilla si existen armas involucradas y selecciona un nivel de urgencia (*Alta*, *Media* o *Baja*).
4. Haz clic en cualquier sector del mapa interactivo de Valparaíso para fijar la ubicación exacta del incidente.
5. Presiona el botón "Confirmar y Enviar Alerta" para procesar la información, visualizar el marcador en tiempo real sobre el mapa y comprobar el registro automático con su respectiva dirección y hora en la pestaña "HISTORIAL".
