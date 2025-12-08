# 🎓 Google Maps Scraper Avanzado - Proyecto Educativo

## ⚠️ DISCLAIMER IMPORTANTE

**Este proyecto es EXCLUSIVAMENTE para fines educativos, académicos y de investigación.**

- ❌ NO debe usarse para violar los Términos de Servicio de Google
- ❌ NO debe usarse para scraping masivo o comercial
- ❌ NO debe usarse para spam o contacto no solicitado
- ✅ Para uso en producción, utiliza [Google Places API](https://developers.google.com/maps/documentation/places/web-service)

**El autor no se hace responsable del uso indebido de este código.**

---

## 📋 Índice

- [Características Técnicas](#-características-técnicas)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Configuración Avanzada](#-configuración-avanzada)
- [Técnicas Anti-Detección](#-técnicas-anti-detección)
- [Exportación de Datos](#-exportación-de-datos)
- [Troubleshooting](#-troubleshooting)
- [Consideraciones Éticas](#-consideraciones-éticas)

---

## 🚀 Características Técnicas

### Scraping Avanzado
- ✅ **Selenium WebDriver** con configuración anti-detección
- ✅ **Scroll infinito automático** con simulación humana
- ✅ **Rotación de User Agents** aleatoria
- ✅ **Delays aleatorios** para evitar patrones de bot
- ✅ **Extracción multi-campo**: nombre, dirección, teléfono, email, web, rating, reviews, coordenadas
- ✅ **Manejo robusto de errores** con reintentos automáticos
- ✅ **Logging detallado** en archivo y consola

### Extracción de Datos
- 📍 Nombre del negocio
- 📍 Dirección completa
- 📞 Teléfono (múltiples formatos)
- ✉️ Email (extracción mediante regex)
- 🌐 Sitio web
- ⭐ Rating (calificación)
- 💬 Número de reseñas
- 🏷️ Categoría del negocio
- 🗺️ Coordenadas GPS (latitud/longitud)
- ⏰ Timestamp de extracción

### Exportación
- 📊 CSV (Excel-compatible)
- 📄 JSON (estructurado)
- 📈 Excel (.xlsx) con pandas
- 📝 Logs detallados

---

## 🏗️ Arquitectura del Sistema

```
google-maps-scraper/
│
├── google_maps_scraper.py    # Script principal
├── config.json                # Configuración del scraper
├── requirements.txt           # Dependencias
├── README.md                  # Documentación
│
├── resultados/                # Directorio de salida
│   ├── resultados.csv
│   ├── resultados.json
│   └── resultados.xlsx
│
└── scraper.log                # Archivo de logs
```

### Clases Principales

#### `BusinessData`
```python
@dataclass
class BusinessData:
    nombre: str
    direccion: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    sitio_web: Optional[str]
    rating: Optional[float]
    reviews_count: Optional[int]
    categoria: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    scrape_timestamp: str
```

#### `UserAgentRotator`
Gestiona la rotación de User Agents para evitar detección:
- 6+ User Agents diferentes
- Rotación aleatoria en cada sesión
- Soporte para Chrome, Firefox, Safari

#### `GoogleMapsScraperAdvanced`
Clase principal con métodos:
- `search_businesses()`: Búsqueda y extracción
- `_extract_business_details()`: Extracción de datos individuales
- `_human_like_scroll()`: Simulación de scroll humano
- `export_to_csv/json/excel()`: Exportación en múltiples formatos

---

## 📦 Requisitos

### Software Necesario
- **Python 3.8+**
- **Google Chrome** (última versión)
- **ChromeDriver** (se instala automáticamente con webdriver-manager)

### Sistema Operativo
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 20.04+, Debian, etc.)

---

## 🔧 Instalación

### 1. Clonar o Descargar el Proyecto

```bash
# Si está en un repositorio
git clone [URL_DEL_REPO]
cd google-maps-scraper

# O simplemente descargar los archivos
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar Instalación

```bash
python google_maps_scraper.py
```

---

## 💻 Uso

### Uso Básico (Interactivo)

```bash
python google_maps_scraper.py
```

El script te pedirá:
1. **Categoría** de negocios (ej: "restaurantes", "hoteles", "gimnasios")
2. **Ubicación** (ej: "Madrid, España", "Barcelona, España")
3. **Número máximo** de resultados (ej: 20, 50, 100)

### Ejemplo de Sesión

```
==================================================================
Google Maps Scraper - SOLO USO EDUCATIVO
==================================================================

⚠️  ADVERTENCIA:
Este scraper es SOLO para fines educativos y de investigación.
NO debe usarse para violar términos de servicio de Google.
Para uso en producción, usa Google Places API.

==================================================================

Ingresa la categoría de negocios (ej: restaurantes): restaurantes
Ingresa la ubicación (ej: Madrid, España): Madrid, España
Número máximo de resultados (ej: 20): 30

🔍 Iniciando scraper...
   Categoría: restaurantes
   Ubicación: Madrid, España
   Max resultados: 30

[INFO] WebDriver configurado exitosamente
[INFO] Buscando: restaurantes en Madrid, España
[INFO] Panel de resultados cargado
[INFO] Realizando scroll para cargar más resultados...
[INFO] [1/30] Extraído: Restaurante El Prado
[INFO] [2/30] Extraído: Casa Lucio
...
[INFO] Extracción completada. Total: 30 negocios

📊 Exportando resultados...
[INFO] Resultados exportados a resultados.csv
[INFO] Resultados exportados a resultados.json

==================================================================
RESUMEN DE EXTRACCIÓN
==================================================================
Total de negocios extraídos: 30
Con teléfono: 28
Con email: 12
Con sitio web: 25
Con rating: 30

✅ Archivos generados:
   - resultados.csv
   - resultados.json
   - scraper.log

👋 Scraper finalizado
```

### Uso Programático

```python
from google_maps_scraper import GoogleMapsScraperAdvanced

# Crear instancia
scraper = GoogleMapsScraperAdvanced(headless=False)

# Buscar negocios
results = scraper.search_businesses(
    categoria="cafeterías",
    ubicacion="Barcelona, España",
    max_results=50
)

# Exportar resultados
scraper.export_to_csv("cafeterias_barcelona.csv")
scraper.export_to_json("cafeterias_barcelona.json")
scraper.export_to_excel("cafeterias_barcelona.xlsx")

# Cerrar
scraper.close()

# Procesar resultados
for business in results:
    print(f"{business.nombre} - {business.telefono}")
```

---

## ⚙️ Configuración Avanzada

### Archivo `config.json`

```json
{
  "scraper_config": {
    "delays": {
      "min_delay": 1.0,
      "max_delay": 3.0,
      "page_load_delay": 3.0
    },
    "browser": {
      "headless": false,
      "window_size": "1920,1080"
    },
    "extraction": {
      "max_scroll_attempts": 15,
      "timeout_seconds": 15
    }
  }
}
```

### Parámetros del Scraper

```python
scraper = GoogleMapsScraperAdvanced(
    headless=True,        # Ejecutar sin interfaz gráfica
    proxy="host:port"     # Usar proxy (opcional)
)
```

### Modo Headless

Para ejecutar sin ventana visible:

```python
scraper = GoogleMapsScraperAdvanced(headless=True)
```

---

## 🛡️ Técnicas Anti-Detección

### 1. Rotación de User Agents
```python
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
    # ... más user agents
]
```

### 2. Ocultación de WebDriver
```javascript
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
})
```

### 3. Delays Aleatorios
```python
delay = random.uniform(1.0, 3.0)
time.sleep(delay)
```

### 4. Scroll Humano
```python
def _human_like_scroll(self, scrollable_element):
    scroll_amount = random.randint(300, 500)
    scroll_pause = random.uniform(0.5, 1.5)
    # Scroll con pausas irregulares
```

### 5. Configuración de Chrome
```python
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

---

## 📊 Exportación de Datos

### Formato CSV
```csv
nombre,direccion,telefono,email,sitio_web,rating,reviews_count
"Restaurante El Prado","Calle Mayor 1","+34 915 555 555","info@elprado.com","https://elprado.com",4.5,245
```

### Formato JSON
```json
[
  {
    "nombre": "Restaurante El Prado",
    "direccion": "Calle Mayor 1, Madrid",
    "telefono": "+34 915 555 555",
    "email": "info@elprado.com",
    "sitio_web": "https://elprado.com",
    "rating": 4.5,
    "reviews_count": 245,
    "categoria": "Restaurante",
    "lat": 40.4168,
    "lng": -3.7038,
    "scrape_timestamp": "2024-12-08T10:30:00"
  }
]
```

### Formato Excel
Tabla con todas las columnas formateadas, lista para análisis.

---

## 🔍 Troubleshooting

### Error: "ChromeDriver not found"
```bash
pip install webdriver-manager --upgrade
```

### Error: "Element not found"
- Aumentar `timeout_seconds` en la configuración
- Verificar que Google Maps cargue correctamente
- Revisar cambios en la estructura HTML de Google Maps

### Error: "Too many requests" o IP bloqueada
- Aumentar los delays entre peticiones
- Usar un proxy
- Esperar unas horas antes de reintentar
- Usar VPN

### Scraper muy lento
- Reducir `max_results`
- Disminuir delays (con precaución)
- Activar modo `headless=True`

### No encuentra emails
- Los emails son difíciles de extraer de Google Maps
- Muchos negocios no publican emails públicamente
- Considera visitar los sitios web para obtener emails

---

## 🛠️ Mejoras Futuras

### Implementaciones Posibles

1. **Multiprocessing/Multithreading**
   - Scraping paralelo de múltiples ubicaciones
   - Pool de navegadores

2. **Base de Datos**
   - Integración con SQLite/PostgreSQL
   - Almacenamiento persistente

3. **API RESTful**
   - Servidor Flask/FastAPI
   - Endpoints para búsquedas programáticas

4. **Dashboard**
   - Interfaz web con Streamlit/Dash
   - Visualización de datos en tiempo real

5. **Machine Learning**
   - Clasificación automática de negocios
   - Detección de duplicados

6. **Proxy Rotation**
   - Pool de proxies rotativos
   - Distribución de carga

---

## ⚖️ Consideraciones Éticas

### Uso Responsable

1. **Respeta los Términos de Servicio**
   - Lee y comprende los TOS de Google Maps
   - Usa la API oficial para proyectos comerciales

2. **Protección de Datos**
   - Cumple con GDPR, CCPA y leyes locales
   - No almacenes datos personales innecesariamente
   - Implementa medidas de seguridad

3. **Rate Limiting**
   - No sobrecargues los servidores de Google
   - Implementa delays apropiados
   - Limita la cantidad de peticiones

4. **Propósito Legítimo**
   - Usa los datos solo para investigación legítima
   - No para spam o contacto no solicitado
   - No para competencia desleal

5. **Transparencia**
   - Sé honesto sobre cómo obtuviste los datos
   - Cita las fuentes apropiadamente

### Alternativas Legales

#### Google Places API
```python
import googlemaps

gmaps = googlemaps.Client(key='TU_API_KEY')

places_result = gmaps.places_nearby(
    location={'lat': 40.4168, 'lng': -3.7038},
    radius=5000,
    type='restaurant'
)
```

**Ventajas:**
- ✅ Legal y dentro de los TOS
- ✅ Datos estructurados y confiables
- ✅ Soporte oficial
- ✅ Capa gratuita: $200/mes en créditos

---

## 📚 Referencias

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Google Maps Platform](https://developers.google.com/maps)
- [Web Scraping Ethics](https://www.scraperapi.com/blog/web-scraping-ethics/)
- [GDPR Compliance](https://gdpr.eu/)

---

## 📝 Licencia

Este proyecto es exclusivamente para **fines educativos**.

**MIT License** - Úsalo para aprender, no para producción.

---

## 👨‍💻 Autor

Proyecto creado para propósitos académicos y educativos.

**Contacto**: Para preguntas académicas sobre el código.

---

## 🎯 Conclusión

Este scraper demuestra técnicas avanzadas de web scraping con Python y Selenium, incluyendo:
- Arquitectura de software escalable
- Técnicas anti-detección
- Manejo robusto de errores
- Exportación multi-formato
- Prácticas de código limpio

**Recuerda:** Para proyectos reales, usa siempre las APIs oficiales.

---

**⭐ Si este proyecto te ayudó en tu aprendizaje, considera darle una estrella!**
