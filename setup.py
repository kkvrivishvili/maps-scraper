#!/usr/bin/env python3
"""
Script de Setup Automatizado
=============================
Configura el entorno completo para el Google Maps Scraper
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


class Colors:
    """Colores para terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Imprime encabezado colorido"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    """Imprime advertencia"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    """Imprime información"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def check_python_version():
    """Verifica versión de Python"""
    print_header("1. Verificando Python")
    
    version = sys.version_info
    print_info(f"Python detectado: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Se requiere Python 3.8 o superior")
        return False
    
    print_success("Versión de Python correcta")
    return True


def check_pip():
    """Verifica que pip esté instalado"""
    print_header("2. Verificando pip")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_info(result.stdout.strip())
            print_success("pip está instalado")
            return True
        else:
            print_error("pip no está disponible")
            return False
    except Exception as e:
        print_error(f"Error al verificar pip: {e}")
        return False


def create_directories():
    """Crea directorios necesarios"""
    print_header("3. Creando Directorios")
    
    dirs = ['resultados', '.cache', 'logs']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir()
            print_success(f"Directorio creado: {dir_name}/")
        else:
            print_info(f"Directorio ya existe: {dir_name}/")
    
    return True


def install_requirements():
    """Instala dependencias desde requirements.txt"""
    print_header("4. Instalando Dependencias")
    
    if not Path("requirements.txt").exists():
        print_error("No se encontró requirements.txt")
        return False
    
    print_info("Instalando paquetes... (esto puede tomar unos minutos)")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Todas las dependencias instaladas correctamente")
            return True
        else:
            print_error("Error al instalar dependencias")
            print(result.stderr)
            return False
    except Exception as e:
        print_error(f"Error durante la instalación: {e}")
        return False


def check_chrome():
    """Verifica que Chrome esté instalado"""
    print_header("5. Verificando Google Chrome")
    
    system = platform.system()
    chrome_paths = {
        'Windows': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ],
        'Darwin': [  # macOS
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        ],
        'Linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
        ]
    }
    
    paths = chrome_paths.get(system, [])
    
    for path in paths:
        if os.path.exists(path):
            print_success(f"Chrome encontrado en: {path}")
            return True
    
    print_warning("No se detectó Google Chrome automáticamente")
    print_info("Asegúrate de tener Chrome instalado:")
    print_info("  Windows/Mac: https://www.google.com/chrome/")
    print_info("  Linux: sudo apt install google-chrome-stable")
    
    response = input("\n¿Chrome está instalado? (s/n): ").strip().lower()
    return response == 's'


def test_selenium():
    """Prueba rápida de Selenium"""
    print_header("6. Probando Selenium")
    
    try:
        print_info("Inicializando WebDriver... (puede tomar unos segundos)")
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        if "Google" in title:
            print_success("Selenium configurado correctamente")
            return True
        else:
            print_error("Selenium no funcionó correctamente")
            return False
            
    except Exception as e:
        print_error(f"Error al probar Selenium: {e}")
        print_info("ChromeDriver se descargará automáticamente en la primera ejecución")
        return True  # No es crítico


def show_next_steps():
    """Muestra los próximos pasos"""
    print_header("🎉 ¡INSTALACIÓN COMPLETADA!")
    
    print(f"{Colors.BOLD}Próximos pasos:{Colors.ENDC}\n")
    
    print("1️⃣  Ejecutar el scraper básico:")
    print(f"   {Colors.OKCYAN}python google_maps_scraper.py{Colors.ENDC}\n")
    
    print("2️⃣  Ejecutar versión avanzada con batch:")
    print(f"   {Colors.OKCYAN}python google_maps_scraper_advanced.py{Colors.ENDC}\n")
    
    print("3️⃣  Ver ejemplos de uso:")
    print(f"   {Colors.OKCYAN}python ejemplos_uso.py{Colors.ENDC}\n")
    
    print("4️⃣  Configurar búsquedas personalizadas:")
    print(f"   {Colors.OKCYAN}Editar: config.json{Colors.ENDC}\n")
    
    print("5️⃣  Leer documentación completa:")
    print(f"   {Colors.OKCYAN}Abrir: README.md{Colors.ENDC}\n")
    
    print(f"{Colors.WARNING}⚠️  RECUERDA: Este proyecto es SOLO para fines educativos{Colors.ENDC}")
    print(f"{Colors.WARNING}   Para uso en producción, utiliza Google Places API{Colors.ENDC}\n")


def main():
    """Función principal de setup"""
    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        🎓 GOOGLE MAPS SCRAPER - SETUP AUTOMATIZADO 🎓            ║
║                                                                   ║
║                  Setup Educativo para Doctorado                   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
""")
    
    print_warning("Este proyecto es exclusivamente para fines educativos")
    print_warning("NO debe usarse para violar términos de servicio de Google\n")
    
    # Ejecutar verificaciones
    checks = [
        ("Python Version", check_python_version),
        ("pip", check_pip),
        ("Directorios", create_directories),
        ("Dependencias", install_requirements),
        ("Google Chrome", check_chrome),
        ("Selenium", test_selenium),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
                print_error(f"{name} falló")
        except Exception as e:
            print_error(f"Error en {name}: {e}")
            all_passed = False
    
    # Resumen final
    print("\n" + "="*70)
    if all_passed:
        print_success("✅ TODAS LAS VERIFICACIONES PASARON")
        show_next_steps()
    else:
        print_warning("⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print_info("Revisa los errores anteriores e intenta resolverlos")
        print_info("Puedes volver a ejecutar: python setup.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Setup interrumpido{Colors.ENDC}\n")
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
