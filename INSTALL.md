# 📥 Guía de Instalación Detallada

Esta guía proporciona instrucciones paso a paso para configurar el Google Maps Scraper en diferentes sistemas operativos.

---

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación en Windows](#instalación-en-windows)
- [Instalación en macOS](#instalación-en-macos)
- [Instalación en Linux](#instalación-en-linux)
- [Verificación de la Instalación](#verificación-de-la-instalación)
- [Solución de Problemas](#solución-de-problemas)

---

## ⚙️ Requisitos Previos

Antes de comenzar, asegúrate de tener:

1. **Python 3.8 o superior**
2. **pip** (gestor de paquetes de Python)
3. **Google Chrome** (última versión)
4. **10 GB** de espacio en disco
5. **Conexión a Internet** estable

---

## 🪟 Instalación en Windows

### Paso 1: Instalar Python

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Ejecuta el instalador
3. ✅ **IMPORTANTE:** Marca "Add Python to PATH"
4. Instala con "Install Now"

**Verificar instalación:**
```cmd
python --version
pip --version
```

### Paso 2: Instalar Google Chrome

1. Descarga desde [google.com/chrome](https://www.google.com/chrome/)
2. Instala normalmente

### Paso 3: Descargar el Proyecto

```cmd
# Si tienes git
git clone [URL_DEL_REPOSITORIO]
cd google-maps-scraper

# O descarga el ZIP y extrae
```

### Paso 4: Crear Entorno Virtual (Recomendado)

```cmd
python -m venv venv
venv\Scripts\activate
```

Tu terminal debería mostrar `(venv)` al inicio.

### Paso 5: Instalar Dependencias

**Opción A - Automática (Recomendado):**
```cmd
python setup.py
```

**Opción B - Manual:**
```cmd
pip install -r requirements.txt
```

### Paso 6: Verificar Instalación

```cmd
python -c "from selenium import webdriver; print('✅ Selenium OK')"
```

### Paso 7: Primera Ejecución

```cmd
python google_maps_scraper.py
```

---

## 🍎 Instalación en macOS

### Paso 1: Instalar Homebrew (si no lo tienes)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Paso 2: Instalar Python

```bash
brew install python@3.11
```

**Verificar:**
```bash
python3 --version
pip3 --version
```

### Paso 3: Instalar Google Chrome

```bash
brew install --cask google-chrome
```

O descarga manualmente desde [google.com/chrome](https://www.google.com/chrome/)

### Paso 4: Descargar el Proyecto

```bash
git clone [URL_DEL_REPOSITORIO]
cd google-maps-scraper
```

### Paso 5: Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 6: Instalar Dependencias

**Automático:**
```bash
python3 setup.py
```

**Manual:**
```bash
pip install -r requirements.txt
```

### Paso 7: Primera Ejecución

```bash
python3 google_maps_scraper.py
```

---

## 🐧 Instalación en Linux (Ubuntu/Debian)

### Paso 1: Actualizar Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Paso 2: Instalar Python y pip

```bash
sudo apt install python3 python3-pip python3-venv -y
```

**Verificar:**
```bash
python3 --version
pip3 --version
```

### Paso 3: Instalar Google Chrome

```bash
# Descargar
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Instalar
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Resolver dependencias si hay errores
sudo apt-get install -f

# Verificar
google-chrome --version
```

### Paso 4: Instalar Dependencias del Sistema

```bash
sudo apt install -y \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxtst6
```

### Paso 5: Descargar Proyecto

```bash
git clone [URL_DEL_REPOSITORIO]
cd google-maps-scraper
```

### Paso 6: Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 7: Instalar Dependencias Python

**Automático:**
```bash
python3 setup.py
```

**Manual:**
```bash
pip install -r requirements.txt
```

### Paso 8: Primera Ejecución

```bash
python3 google_maps_scraper.py
```

### Ejecución en Servidor (Headless)

Si estás en un servidor sin interfaz gráfica:

```bash
# Instalar Xvfb
sudo apt install xvfb

# Ejecutar con display virtual
xvfb-run python3 google_maps_scraper.py
```

O modifica el código para usar `headless=True`.

---

## ✅ Verificación de la Instalación

### Test Completo Automatizado

```bash
python setup.py
```

Este script verifica:
- ✅ Versión de Python
- ✅ pip instalado
- ✅ Directorios creados
- ✅ Dependencias instaladas
- ✅ Chrome disponible
- ✅ Selenium funcionando

### Test Manual de Selenium

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless=new')

driver = webdriver.Chrome(options=options)
driver.get('https://www.google.com')
print(f"Título: {driver.title}")
driver.quit()

print("✅ Selenium funciona correctamente!")
```

### Test del Scraper

```bash
# Ejecutar con valores de prueba
python google_maps_scraper.py
# Cuando pida datos, ingresa:
# Categoría: cafeterías
# Ubicación: Madrid, España
# Resultados: 5
```

---

## 🔧 Solución de Problemas

### Problema 1: "python: command not found"

**Windows:**
```cmd
# Usa py en lugar de python
py --version
```

**macOS/Linux:**
```bash
# Usa python3
python3 --version
```

### Problema 2: "No module named 'selenium'"

```bash
# Asegúrate de estar en el entorno virtual
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Reinstala
pip install selenium
```

### Problema 3: "ChromeDriver not found"

El driver se descarga automáticamente, pero si falla:

```bash
pip install webdriver-manager --upgrade
```

### Problema 4: "Chrome binary not found"

**Linux:**
```bash
# Verifica que Chrome esté instalado
which google-chrome

# Si no está, instala
sudo apt install google-chrome-stable
```

**macOS:**
```bash
# Verifica instalación
ls /Applications/ | grep Chrome

# Si no está
brew install --cask google-chrome
```

**Windows:**
Reinstala Chrome desde [google.com/chrome](https://www.google.com/chrome/)

### Problema 5: "Permission denied" (Linux/macOS)

```bash
chmod +x google_maps_scraper.py
chmod +x setup.py
```

### Problema 6: Scraper muy lento

1. Reduce `max_results`
2. Usa modo headless:
   ```python
   scraper = GoogleMapsScraperAdvanced(headless=True)
   ```
3. Cierra otras aplicaciones

### Problema 7: "Element not found" o TimeoutException

Esto puede ocurrir si Google Maps cambia su estructura HTML.

**Soluciones:**
1. Actualiza el proyecto a la última versión
2. Aumenta el timeout en `config.json`
3. Revisa que tengas buena conexión a Internet

### Problema 8: IP bloqueada por Google

**Síntomas:** Captchas frecuentes, páginas en blanco

**Soluciones:**
1. Aumenta los delays en `config.json`
2. Usa un proxy/VPN
3. Espera unas horas antes de reintentar
4. Reduce la cantidad de resultados solicitados

### Problema 9: Sin resultados

**Verificar:**
1. La búsqueda tiene sentido (ej: "restaurantes en Madrid")
2. Google Maps encuentra resultados para esa búsqueda manualmente
3. La ortografía de categoría y ubicación es correcta
4. Tienes conexión a Internet

### Problema 10: ImportError con pandas o openpyxl

```bash
pip install pandas openpyxl --upgrade
```

---

## 📞 Soporte Adicional

### Logs

Revisa el archivo `scraper.log` para detalles de errores:

```bash
# Ver últimas líneas
tail -n 50 scraper.log

# Ver todo el log
cat scraper.log
```

### Modo Debug

Activa logging verbose en el código:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Recursos Útiles

- [Documentación Selenium](https://selenium-python.readthedocs.io/)
- [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/)

---

## ✨ Instalación Exitosa

Si llegaste hasta aquí sin errores:

🎉 **¡Felicitaciones!** 🎉

Tu Google Maps Scraper está listo para usar.

### Próximos Pasos:

1. Lee el `README.md` completo
2. Explora los ejemplos en `ejemplos_uso.py`
3. Configura tus búsquedas en `config.json`
4. Empieza a experimentar (con responsabilidad)

### Recuerda:

⚠️ **Este proyecto es SOLO para fines educativos**
⚠️ **Para producción, usa Google Places API oficial**
⚠️ **Respeta los términos de servicio de Google**

---

**¿Preguntas o problemas?**

Revisa la sección de Issues del repositorio o la documentación adicional.

¡Buen scraping! 🚀
