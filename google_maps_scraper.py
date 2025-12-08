"""
Google Maps Scraper - EDUCATIONAL PURPOSE ONLY
================================================
Este scraper es para fines académicos y de investigación únicamente.
NO debe usarse para violación de términos de servicio.

Características avanzadas:
- Selenium WebDriver con detección anti-bot
- Scroll infinito automático
- Rotación de User Agents
- Delays aleatorios anti-detección
- Manejo robusto de errores
- Exportación multi-formato (CSV, JSON, Excel)
- Logging detallado
- Arquitectura modular y escalable
"""

import time
import random
import json
import csv
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException
)


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BusinessData:
    """Estructura de datos para almacenar información del negocio"""
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    sitio_web: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    categoria: Optional[str] = None
    horarios: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    scrape_timestamp: str = None
    
    def __post_init__(self):
        if self.scrape_timestamp is None:
            self.scrape_timestamp = datetime.now().isoformat()


class UserAgentRotator:
    """Rotador de User Agents para evitar detección"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    @classmethod
    def get_random(cls) -> str:
        return random.choice(cls.USER_AGENTS)


class GoogleMapsScraperAdvanced:
    """
    Scraper avanzado para Google Maps con técnicas anti-detección
    """
    
    def __init__(self, headless: bool = False, proxy: Optional[str] = None):
        """
        Inicializa el scraper
        
        Args:
            headless: Ejecutar en modo headless
            proxy: Proxy a utilizar (formato: host:port)
        """
        self.driver = None
        self.headless = headless
        self.proxy = proxy
        self.results: List[BusinessData] = []
        self._setup_driver()
        
    def _setup_driver(self):
        """Configura el WebDriver con opciones anti-detección"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Opciones anti-detección
        chrome_options.add_argument(f'user-agent={UserAgentRotator.get_random()}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--lang=es-ES')
        
        # Configuración de proxy si se proporciona
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Script para ocultar webdriver
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": UserAgentRotator.get_random()
            })
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logger.info("WebDriver configurado exitosamente")
        except Exception as e:
            logger.error(f"Error al configurar WebDriver: {e}")
            raise
    
    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Añade un delay aleatorio para simular comportamiento humano"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _human_like_scroll(self, scrollable_element):
        """Simula scroll humano con pausas irregulares"""
        scroll_pause_time = random.uniform(0.5, 1.5)
        last_height = self.driver.execute_script(
            "return arguments[0].scrollHeight", scrollable_element
        )
        
        while True:
            # Scroll con velocidad variable
            scroll_amount = random.randint(300, 500)
            self.driver.execute_script(
                f"arguments[0].scrollBy(0, {scroll_amount});", scrollable_element
            )
            
            time.sleep(scroll_pause_time)
            
            new_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", scrollable_element
            )
            
            if new_height == last_height:
                break
            last_height = new_height
    
    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Extrae email usando regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone_from_text(self, text: str) -> Optional[str]:
        """Extrae teléfono usando regex (formato internacional y local)"""
        # Patrones para diferentes formatos de teléfono
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def search_businesses(
        self, 
        categoria: str, 
        ubicacion: str, 
        max_results: int = 50
    ) -> List[BusinessData]:
        """
        Busca negocios en Google Maps
        
        Args:
            categoria: Tipo de negocio (ej: "restaurantes", "hoteles")
            ubicacion: Ciudad o área (ej: "Madrid, España")
            max_results: Número máximo de resultados a extraer
            
        Returns:
            Lista de BusinessData con información de negocios
        """
        query = f"{categoria} en {ubicacion}"
        url = f"https://www.google.com/maps/search/{quote_plus(query)}"
        
        logger.info(f"Buscando: {query}")
        logger.info(f"URL: {url}")
        
        try:
            self.driver.get(url)
            self._random_delay(3, 5)
            
            # Esperar a que cargue el panel de resultados
            try:
                results_panel = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
                )
                logger.info("Panel de resultados cargado")
            except TimeoutException:
                logger.error("No se pudo cargar el panel de resultados")
                return []
            
            # Scroll para cargar más resultados
            logger.info("Realizando scroll para cargar más resultados...")
            scroll_attempts = 0
            max_scroll_attempts = max_results // 10 + 5
            
            while scroll_attempts < max_scroll_attempts:
                self._human_like_scroll(results_panel)
                scroll_attempts += 1
                
                # Verificar cantidad de resultados cargados
                business_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "div[role='feed'] > div > div[jsaction]"
                )
                logger.info(f"Resultados cargados: {len(business_elements)}")
                
                if len(business_elements) >= max_results:
                    break
                
                self._random_delay(1, 2)
            
            # Extraer información de cada negocio
            logger.info("Extrayendo información de negocios...")
            business_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "div[role='feed'] > div > div[jsaction]"
            )[:max_results]
            
            for idx, element in enumerate(business_elements, 1):
                try:
                    business_data = self._extract_business_details(element, idx)
                    if business_data:
                        self.results.append(business_data)
                        logger.info(f"[{idx}/{len(business_elements)}] Extraído: {business_data.nombre}")
                except Exception as e:
                    logger.warning(f"Error extrayendo negocio {idx}: {e}")
                    continue
                
                # Delay aleatorio entre extracciones
                if idx < len(business_elements):
                    self._random_delay(0.5, 1.5)
            
            logger.info(f"Extracción completada. Total: {len(self.results)} negocios")
            return self.results
            
        except Exception as e:
            logger.error(f"Error durante la búsqueda: {e}")
            return []
    
    def _extract_business_details(self, element, index: int) -> Optional[BusinessData]:
        """
        Extrae detalles de un negocio desde su elemento en la lista
        
        Args:
            element: WebElement del negocio
            index: Índice del negocio en la lista
            
        Returns:
            BusinessData o None si falla
        """
        try:
            # Click en el elemento para abrir detalles
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self._random_delay(0.3, 0.7)
            element.click()
            self._random_delay(2, 3)
            
            # Extraer nombre
            try:
                nombre_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
                )
                nombre = nombre_element.text
            except:
                nombre = "N/A"
            
            # Extraer dirección
            try:
                direccion_button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "button[data-item-id='address']"
                )
                direccion = direccion_button.get_attribute("aria-label").replace("Dirección: ", "")
            except:
                direccion = None
            
            # Extraer teléfono
            telefono = None
            try:
                phone_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "button[data-item-id*='phone']"
                )
                if phone_buttons:
                    aria_label = phone_buttons[0].get_attribute("aria-label")
                    telefono = self._extract_phone_from_text(aria_label)
            except:
                pass
            
            # Extraer sitio web y buscar email
            sitio_web = None
            email = None
            try:
                website_link = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "a[data-item-id='authority']"
                )
                sitio_web = website_link.get_attribute("href")
                
                # Intentar extraer email del texto visible
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                email = self._extract_email_from_text(page_text)
            except:
                pass
            
            # Extraer rating
            rating = None
            try:
                rating_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "span.ceNzKf"
                )
                rating_text = rating_element.get_attribute("aria-label")
                rating_match = re.search(r'(\d+[,.]?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1).replace(',', '.'))
            except:
                pass
            
            # Extraer número de reseñas
            reviews_count = None
            try:
                reviews_element = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "button.HHrUdb span"
                )
                reviews_text = reviews_element.text
                reviews_match = re.search(r'(\d+)', reviews_text.replace('.', '').replace(',', ''))
                if reviews_match:
                    reviews_count = int(reviews_match.group(1))
            except:
                pass
            
            # Extraer categoría
            categoria = None
            try:
                categoria_button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "button.DkEaL"
                )
                categoria = categoria_button.text
            except:
                pass
            
            # Extraer coordenadas de la URL
            lat, lng = None, None
            try:
                current_url = self.driver.current_url
                coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)
                if coords_match:
                    lat = float(coords_match.group(1))
                    lng = float(coords_match.group(2))
            except:
                pass
            
            business_data = BusinessData(
                nombre=nombre,
                direccion=direccion,
                telefono=telefono,
                email=email,
                sitio_web=sitio_web,
                rating=rating,
                reviews_count=reviews_count,
                categoria=categoria,
                lat=lat,
                lng=lng
            )
            
            return business_data
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles del negocio {index}: {e}")
            return None
    
    def export_to_csv(self, filename: str = "resultados_scraper.csv"):
        """Exporta resultados a CSV"""
        if not self.results:
            logger.warning("No hay resultados para exportar")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'nombre', 'direccion', 'telefono', 'email', 'sitio_web',
                    'rating', 'reviews_count', 'categoria', 'lat', 'lng', 'scrape_timestamp'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for business in self.results:
                    writer.writerow(asdict(business))
            
            logger.info(f"Resultados exportados a {filename}")
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
    
    def export_to_json(self, filename: str = "resultados_scraper.json"):
        """Exporta resultados a JSON"""
        if not self.results:
            logger.warning("No hay resultados para exportar")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(
                    [asdict(business) for business in self.results],
                    jsonfile,
                    indent=2,
                    ensure_ascii=False
                )
            
            logger.info(f"Resultados exportados a {filename}")
        except Exception as e:
            logger.error(f"Error exportando a JSON: {e}")
    
    def export_to_excel(self, filename: str = "resultados_scraper.xlsx"):
        """Exporta resultados a Excel"""
        try:
            import pandas as pd
            
            if not self.results:
                logger.warning("No hay resultados para exportar")
                return
            
            df = pd.DataFrame([asdict(business) for business in self.results])
            df.to_excel(filename, index=False, engine='openpyxl')
            
            logger.info(f"Resultados exportados a {filename}")
        except ImportError:
            logger.error("pandas y openpyxl son necesarios para exportar a Excel")
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
    
    def close(self):
        """Cierra el WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver cerrado")


def main():
    """Función principal de ejemplo"""
    print("="*70)
    print("Google Maps Scraper - SOLO USO EDUCATIVO")
    print("="*70)
    print("\n⚠️  ADVERTENCIA:")
    print("Este scraper es SOLO para fines educativos y de investigación.")
    print("NO debe usarse para violar términos de servicio de Google.")
    print("Para uso en producción, usa Google Places API.\n")
    print("="*70)
    
    # Configuración
    CATEGORIA = input("\nIngresa la categoría de negocios (ej: restaurantes): ").strip()
    UBICACION = input("Ingresa la ubicación (ej: Madrid, España): ").strip()
    
    try:
        MAX_RESULTS = int(input("Número máximo de resultados (ej: 20): ").strip())
    except:
        MAX_RESULTS = 20
    
    print(f"\n🔍 Iniciando scraper...")
    print(f"   Categoría: {CATEGORIA}")
    print(f"   Ubicación: {UBICACION}")
    print(f"   Max resultados: {MAX_RESULTS}\n")
    
    # Crear instancia del scraper
    scraper = GoogleMapsScraperAdvanced(headless=False)
    
    try:
        # Realizar búsqueda
        results = scraper.search_businesses(
            categoria=CATEGORIA,
            ubicacion=UBICACION,
            max_results=MAX_RESULTS
        )
        
        # Exportar resultados
        if results:
            print("\n📊 Exportando resultados...")
            scraper.export_to_csv("resultados.csv")
            scraper.export_to_json("resultados.json")
            
            # Mostrar resumen
            print("\n" + "="*70)
            print("RESUMEN DE EXTRACCIÓN")
            print("="*70)
            print(f"Total de negocios extraídos: {len(results)}")
            print(f"Con teléfono: {sum(1 for r in results if r.telefono)}")
            print(f"Con email: {sum(1 for r in results if r.email)}")
            print(f"Con sitio web: {sum(1 for r in results if r.sitio_web)}")
            print(f"Con rating: {sum(1 for r in results if r.rating)}")
            print("\n✅ Archivos generados:")
            print("   - resultados.csv")
            print("   - resultados.json")
            print("   - scraper.log")
        else:
            print("\n❌ No se encontraron resultados")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {e}")
        print(f"\n❌ Error: {e}")
    finally:
        scraper.close()
        print("\n👋 Scraper finalizado\n")


if __name__ == "__main__":
    main()
