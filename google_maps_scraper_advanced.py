"""
Google Maps Scraper - VERSIÓN AVANZADA CON GESTIÓN DE CONFIGURACIÓN
====================================================================
Versión mejorada con:
- Carga de configuración desde JSON
- Procesamiento por lotes (batch)
- Gestión de proxies
- Sistema de cache para evitar re-scraping
- Validación de datos
- Reporting automático
"""

import json
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pickle

from google_maps_scraper import (
    GoogleMapsScraperAdvanced,
    BusinessData,
    logger
)

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    logger.warning("gspread o google-auth no instalados. La exportación a Google Sheets estará deshabilitada.")
    GSPREAD_AVAILABLE = False


class ConfigManager:
    """Gestor de configuración desde archivo JSON"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Carga configuración desde archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuración cargada desde {self.config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"No se encontró {self.config_path}, usando configuración por defecto")
            return self._default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear {self.config_path}: {e}")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Configuración por defecto"""
        return {
            "scraper_config": {
                "delays": {
                    "min_delay": 1.0,
                    "max_delay": 3.0,
                    "page_load_delay": 3.0
                },
                "browser": {
                    "headless": False,
                    "window_size": "1920,1080"
                },
                "extraction": {
                    "max_scroll_attempts": 15,
                    "timeout_seconds": 15
                },
                "export": {
                    "csv_enabled": True,
                    "json_enabled": True,
                    "excel_enabled": True,
                    "google_sheets": {
                        "enabled": False,
                        "credentials_path": "gen-lang-client-0571756605-0e567500e274.json",
                        "sheet_name": "Scraper Results"
                    },
                    "output_directory": "./resultados"
                }
            }
        }
    
    def get(self, *keys, default=None):
        """Obtiene valor anidado de configuración"""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value


class CacheManager:
    """Gestor de cache para evitar re-scraping"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _generate_key(self, categoria: str, ubicacion: str) -> str:
        """Genera clave única para búsqueda"""
        key_string = f"{categoria.lower()}_{ubicacion.lower()}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, categoria: str, ubicacion: str, max_age_hours: int = 24) -> Optional[List[BusinessData]]:
        """Obtiene resultados del cache si existen y no son muy antiguos"""
        cache_key = self._generate_key(categoria, ubicacion)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if not cache_file.exists():
            return None
        
        try:
            # Verificar edad del cache
            file_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if file_age > max_age_hours * 3600:
                logger.info(f"Cache expirado para {categoria} en {ubicacion}")
                return None
            
            # Cargar cache
            with open(cache_file, 'rb') as f:
                results = pickle.load(f)
            
            logger.info(f"Resultados cargados desde cache: {len(results)} negocios")
            return results
        except Exception as e:
            logger.error(f"Error al cargar cache: {e}")
            return None
    
    def set(self, categoria: str, ubicacion: str, results: List[BusinessData]):
        """Guarda resultados en cache"""
        cache_key = self._generate_key(categoria, ubicacion)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(results, f)
            logger.info(f"Resultados guardados en cache: {cache_file}")
        except Exception as e:
            logger.error(f"Error al guardar cache: {e}")


class DataValidator:
    """Validador de datos extraídos"""
    
    @staticmethod
    def validate_phone(phone: Optional[str]) -> bool:
        """Valida formato de teléfono"""
        if not phone:
            return False
        # Debe tener al menos 7 dígitos
        digits = ''.join(filter(str.isdigit, phone))
        return len(digits) >= 7
    
    @staticmethod
    def validate_email(email: Optional[str]) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: Optional[str]) -> bool:
        """Valida formato de URL"""
        if not url:
            return False
        return url.startswith('http://') or url.startswith('https://')
    
    @staticmethod
    def validate_coordinates(lat: Optional[float], lng: Optional[float]) -> bool:
        """Valida coordenadas GPS"""
        if lat is None or lng is None:
            return False
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    @classmethod
    def validate_business(cls, business: BusinessData) -> Dict[str, bool]:
        """Valida todos los campos de un negocio"""
        return {
            'nombre': bool(business.nombre and business.nombre != "N/A"),
            'telefono': cls.validate_phone(business.telefono),
            'email': cls.validate_email(business.email),
            'sitio_web': cls.validate_url(business.sitio_web),
            'coordenadas': cls.validate_coordinates(business.lat, business.lng)
        }


class ReportGenerator:
    """Generador de reportes estadísticos"""
    
    @staticmethod
    def generate_summary(results: List[BusinessData]) -> Dict:
        """Genera resumen estadístico de resultados"""
        if not results:
            return {}
        
        validator = DataValidator()
        validations = [validator.validate_business(b) for b in results]
        
        summary = {
            'total_negocios': len(results),
            'con_telefono_valido': sum(1 for v in validations if v['telefono']),
            'con_email_valido': sum(1 for v in validations if v['email']),
            'con_sitio_web_valido': sum(1 for v in validations if v['sitio_web']),
            'con_coordenadas_validas': sum(1 for v in validations if v['coordenadas']),
            'con_rating': sum(1 for b in results if b.rating),
            'rating_promedio': sum(b.rating for b in results if b.rating) / sum(1 for b in results if b.rating) if any(b.rating for b in results) else 0,
            'categorias_unicas': len(set(b.categoria for b in results if b.categoria))
        }
        
        return summary
    
    @staticmethod
    def print_summary(summary: Dict):
        """Imprime resumen de manera formateada"""
        print("\n" + "="*70)
        print("📊 REPORTE DE EXTRACCIÓN")
        print("="*70)
        
        for key, value in summary.items():
            label = key.replace('_', ' ').title()
            if isinstance(value, float):
                print(f"{label}: {value:.2f}")
            else:
                print(f"{label}: {value}")
        
        print("="*70 + "\n")


class BatchScraperManager:
    """Gestor de scraping por lotes (batch processing)"""
    
    def __init__(self, config_manager: ConfigManager, use_cache: bool = True):
        self.config_manager = config_manager
        self.cache_manager = CacheManager() if use_cache else None
        self.all_results: List[BusinessData] = []
    
    def run_batch(self, searches: List[Dict]) -> Dict[str, List[BusinessData]]:
        """
        Ejecuta múltiples búsquedas en lote
        
        Args:
            searches: Lista de diccionarios con 'categoria', 'ubicacion', 'max_results'
            
        Returns:
            Diccionario con resultados por búsqueda
        """
        results_dict = {}
        
        scraper_config = self.config_manager.config.get('scraper_config', {})
        headless = self.config_manager.get('scraper_config', 'browser', 'headless', default=False)
        proxy_data = scraper_config.get('proxy', {})
        proxy = f"{proxy_data.get('host')}:{proxy_data.get('port')}" if proxy_data.get('enabled') and proxy_data.get('host') else None

        scraper = GoogleMapsScraperAdvanced(
            headless=headless,
            proxy=proxy,
            config=scraper_config
        )
        
        try:
            for idx, search in enumerate(searches, 1):
                categoria = search['categoria']
                ubicacion = search['ubicacion']
                max_results = search.get('max_results', 50)
                
                print(f"\n{'='*70}")
                print(f"BÚSQUEDA {idx}/{len(searches)}")
                print(f"{'='*70}")
                print(f"Categoría: {categoria}")
                print(f"Ubicación: {ubicacion}")
                print(f"Max resultados: {max_results}")
                
                # Intentar cargar desde cache
                if self.cache_manager:
                    cached_results = self.cache_manager.get(categoria, ubicacion)
                    if cached_results:
                        print("✅ Resultados cargados desde cache")
                        results_dict[f"{categoria}_{ubicacion}"] = cached_results
                        self.all_results.extend(cached_results)
                        continue
                
                # Realizar scraping
                results = scraper.search_businesses(
                    categoria=categoria,
                    ubicacion=ubicacion,
                    max_results=max_results
                )
                
                # Guardar en cache
                if self.cache_manager and results:
                    self.cache_manager.set(categoria, ubicacion, results)
                
                # Generar reporte para esta búsqueda
                summary = ReportGenerator.generate_summary(results)
                ReportGenerator.print_summary(summary)

                # Deduplicación y Agregación
                for result in results:
                    # Asignar grupo de búsqueda
                    result.search_group = f"{categoria} en {ubicacion}"
                    
                    # Generar firma única (nombre + direccion)
                    # Usar .lower() y eliminar espacios para robustez
                    sig_name = (result.nombre or "").lower().strip()
                    sig_addr = (result.direccion or "").lower().strip()
                    if not sig_name or sig_name == "n/a":
                        # Si no tiene nombre, usar lat/lng si existe, sino saltar
                        if result.lat and result.lng:
                            signature = f"gps|{result.lat}|{result.lng}"
                        else:
                            continue
                    else:
                        signature = f"{sig_name}|{sig_addr}"
                    
                    # Verificar si ya existe
                    exists = False
                    for existing in self.all_results:
                        ex_sig_name = (existing.nombre or "").lower().strip()
                        ex_sig_addr = (existing.direccion or "").lower().strip()
                        if ex_sig_name == sig_name and ex_sig_addr == sig_addr:
                            exists = True
                            # Opcional: Agregar este grupo de búsqueda al existente si quisiéramos lista
                            # existing.search_group += f", {result.search_group}"
                            break
                    
                    if not exists:
                        self.all_results.append(result)
                    else:
                        logger.info(f"Duplicado detectado y omitido: {result.nombre}")
                
        finally:
            scraper.close()
        
        return results_dict
    
    def export_all(self, output_dir: str = "./resultados"):
        """Exporta todos los resultados acumulados"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not self.all_results:
            logger.warning("No hay resultados para exportar")
            return
        
        # Exportar a CSV
        csv_file = output_path / f"batch_results_{timestamp}.csv"
        self._export_csv(csv_file)
        
        # Exportar a JSON
        json_file = output_path / f"batch_results_{timestamp}.json"
        self._export_json(json_file)
        
        # Exportar a Excel
        try:
            excel_file = output_path / f"batch_results_{timestamp}.xlsx"
            self._export_excel(excel_file)
        except ImportError:
            logger.warning("pandas/openpyxl no disponible, saltando exportación a Excel")
        
        # Exportar a Google Sheets
        self._export_google_sheets()
        
        print(f"\n✅ Archivos exportados a: {output_dir}")
    
    def _export_csv(self, filename: Path):
        """Exporta a CSV"""
        import csv
        from dataclasses import asdict
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            if self.all_results:
                fieldnames = asdict(self.all_results[0]).keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for business in self.all_results:
                    writer.writerow(asdict(business))
        
        logger.info(f"CSV exportado: {filename}")
    
    def _export_json(self, filename: Path):
        """Exporta a JSON"""
        from dataclasses import asdict
        
        # Calcular resumen
        # Calcular resumen detallado
        total_businesses = len(self.all_results)
        emails_found = sum(1 for b in self.all_results if b.email)
        websites_found = sum(1 for b in self.all_results if b.sitio_web)
        
        # Desglose de sitios web
        tn_count = 0
        fb_count = 0
        ig_count = 0
        other_count = 0
        
        for b in self.all_results:
            if b.instagram:
                ig_count += 1
            if b.facebook:
                fb_count += 1
                
            if b.sitio_web:
                url_lower = b.sitio_web.lower()
                if 'tiendanube' in url_lower:
                    tn_count += 1
                else:
                    other_count += 1
        
        # Calcular tasa de éxito de emails sobre el target relevante (Tienda Nube + Otros)
        # Excluye redes sociales del denominador ya que raramente tienen email scrapable directamente
        target_websites = tn_count + other_count
        # Contamos emails encontrados en negocios que SON target (TN u otros)
        emails_in_target = sum(1 for b in self.all_results if b.email and b.sitio_web and 
                             ('tiendanube' in b.sitio_web.lower() or 
                              ('facebook.com' not in b.sitio_web.lower() and 'instagram.com' not in b.sitio_web.lower())))
        
        # Si no tiene website pero tiene email, cuenta como éxito global, 
        # pero para esta métrica especifica, el usuario pidió "respecto a paginas web otras y tienda nube"
        # Así que usamos emails_in_target / target_websites
        
        email_success_rate = f"{(emails_in_target/target_websites*100):.1f}%" if target_websites else "0%"

        with open(filename, 'w', encoding='utf-8') as f:
            data = {
                "_summary": {
                    "generated_at": datetime.now().isoformat(),
                    "total_results": total_businesses,
                    "emails_found": emails_found,
                    "websites_found": websites_found,
                    "websites_breakdown": {
                        "tienda_nube": tn_count,
                        "instagram": ig_count,
                        "facebook": fb_count,
                        "other_websites": other_count
                    },
                    "email_success_rate_target_sites": email_success_rate,
                    "note": "Success rate based on Tienda Nube + Other Websites (excluding Social Media)"
                },
                "results": [asdict(b) for b in self.all_results]
            }
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON exportado: {filename}")
        
        # Imprimir resumen en consola para el usuario
        print("\n" + "="*50)
        print("📊 RESUMEN DE EXTRACCIÓN")
        print("="*50)
        print(f"Total Resultados: {total_businesses}")
        print(f"Emails Encontrados: {emails_found}")
        print(f"Sitios Web: {websites_found}")
        print(f"  - Tienda Nube: {tn_count}")
        print(f"  - Instagram: {ig_count}")
        print(f"  - Facebook: {fb_count}")
        print(f"  - Otros: {other_count}")
        print(f"Tasa Éxito Email (TN + Otros): {email_success_rate}")
        print("="*50 + "\n")
    
    def _export_excel(self, filename: Path):
        """Exporta a Excel"""
        import pandas as pd
        from dataclasses import asdict
        
        df = pd.DataFrame([asdict(b) for b in self.all_results])
        df.to_excel(filename, index=False, engine='openpyxl')
        
        logger.info(f"Excel exportado: {filename}")

    def _export_google_sheets(self):
        """Exporta a Google Sheets"""
        if not GSPREAD_AVAILABLE:
            logger.warning("Saltando exportación a Google Sheets: librerías no instaladas")
            return

        gs_config = self.config_manager.get('scraper_config', 'export', 'google_sheets', default={})
        if not gs_config.get('enabled', False):
            return

        creds_path = gs_config.get('credentials_path')
        sheet_name = gs_config.get('sheet_name')

        if not creds_path or not os.path.exists(creds_path):
            logger.error(f"Archivo de credenciales no encontrado: {creds_path}")
            print(f"❌ Error: Archivo de credenciales no encontrado: {creds_path}")
            return

        print(f"\n📤 Exportando a Google Sheets: {sheet_name}...")
        
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                creds_path,
                scopes=scopes
            )
            
            gc = gspread.authorize(credentials)
            
            try:
                sh = gc.open(sheet_name)
            except gspread.exceptions.SpreadsheetNotFound:
                print(f"⚠️  Hoja '{sheet_name}' no encontrada. Intentando crearla...")
                try:
                    sh = gc.create(sheet_name)
                    # Compartir con el usuario si es posible (impreso en logs)
                    print(f"✅ Hoja creada. NOTA: Debes compartirla manualmente o usar la URL.")
                    print(f"   URL: {sh.url}")
                    
                    # Intentar compartir si se configura email
                    share_email = gs_config.get('share_email')
                    if share_email:
                        try:
                            sh.share(share_email, perm_type='user', role='writer')
                            print(f"✅ Hoja compartida con: {share_email}")
                        except Exception as e:
                            logger.error(f"No se pudo compartir la hoja: {e}")
                            print(f"⚠️  No se pudo compartir automáticamente: {e}")

                except Exception as e:
                    logger.error(f"No se pudo crear la hoja: {e}")
                    print(f"❌ Error creando hoja: {e}")
                    return

            worksheet = sh.sheet1
            
            # Preparar datos
            from dataclasses import asdict
            if not self.all_results:
                return

            # Obtener encabezados
            headers = list(asdict(self.all_results[0]).keys())
            
            # Leer datos existentes para deduplicar contra la hoja (básico)
            existing_data_all = worksheet.get_all_values()
            
            data_to_write = []
            
            # Si la hoja está vacía, escribir headers
            if not existing_data_all:
                data_to_write.append(headers)
                existing_signatures = set()
            else:
                # Crear set de firmas existentes (nombre|direccion) para evitar duplicados en la hoja
                # Asumiendo indices: nombre=0, direccion=1 (verificar orden en headers)
                # Mejor usar dict reader logic si posible, pero aquí headers son dinámicos
                header_row = existing_data_all[0]
                try:
                    idx_name = header_row.index('nombre')
                    idx_addr = header_row.index('direccion')
                    existing_signatures = {
                        f"{row[idx_name].lower().strip()}|{row[idx_addr].lower().strip()}" 
                        for row in existing_data_all[1:] 
                        if len(row) > max(idx_name, idx_addr)
                    }
                except ValueError:
                    existing_signatures = set()
            
            count_new = 0
            for business in self.all_results:
                # Verificar duplicado contra hoja
                sig_name = (business.nombre or "").lower().strip()
                sig_addr = (business.direccion or "").lower().strip()
                signature = f"{sig_name}|{sig_addr}"
                
                if signature in existing_signatures:
                    continue
                
                row = list(asdict(business).values())
                # Convertir valores a string para asegurar compatibilidad
                row = [str(x) if x is not None else "" for x in row]
                data_to_write.append(row)
                existing_signatures.add(signature) # Evitar duplicados internos en lote si falló dedup previo
                count_new += 1
            
            # Escribir datos
            if data_to_write:
                worksheet.append_rows(data_to_write)
                print(f"✅ Se añadieron {count_new} nuevas filas a Google Sheets (Duplicados omitidos)")
            else:
                print("ℹ️  No hay datos nuevos para añadir (todo duplicado)")

        except Exception as e:
            logger.error(f"Error exportando a Google Sheets: {e}")
            print(f"❌ Error exportando a Google Sheets: {e}") 




def main_batch_mode():
    """Modo de ejecución por lotes"""
    print("="*70)
    print("🎯 Google Maps Scraper - MODO BATCH (Lotes)")
    print("="*70)
    print("\n⚠️  SOLO USO EDUCATIVO - Respeta los términos de servicio\n")
    
    # Cargar configuración
    config_manager = ConfigManager()
    
    # Verificar si hay búsquedas predefinidas
    presets = config_manager.get('search_presets', default=[])
    
    if presets:
        print(f"📋 Se encontraron {len(presets)} búsquedas predefinidas en config.json")
        print("\nBúsquedas a ejecutar:")
        for idx, preset in enumerate(presets, 1):
            print(f"{idx}. {preset['name']}: {preset['categoria']} en {preset['ubicacion']}")
        
        response = input("\n¿Ejecutar estas búsquedas? (s/n): ").strip().lower()
        
        if response == 's':
            # Ejecutar batch
            # Leer configuración de cache
            cache_config = config_manager.get('scraper_config', 'cache', default={})
            use_cache = cache_config.get('enabled', False) # Default a False si no existe o para forzar nueva búsqueda
            
            if not use_cache:
                print("⚠️  Cache deshabilitado. Se realizará una nueva búsqueda.")
            
            batch_manager = BatchScraperManager(config_manager, use_cache=use_cache)
            results_dict = batch_manager.run_batch(presets)
            
            # Exportar todo
            output_dir = config_manager.get('scraper_config', 'export', 'output_directory', default='./resultados')
            batch_manager.export_all(output_dir)
            
            # Reporte final global
            print("\n" + "="*70)
            print("📈 REPORTE GLOBAL")
            print("="*70)
            global_summary = ReportGenerator.generate_summary(batch_manager.all_results)
            ReportGenerator.print_summary(global_summary)
        else:
            print("❌ Operación cancelada")
    else:
        print("❌ No se encontraron búsquedas predefinidas en config.json")
        print("\nAgrega búsquedas al array 'search_presets' en config.json:")
        print("""
{
  "search_presets": [
    {
      "name": "Restaurantes Madrid",
      "categoria": "restaurantes",
      "ubicacion": "Madrid, España",
      "max_results": 50
    }
  ]
}
        """)


def main_interactive():
    """Modo interactivo mejorado"""
    from google_maps_scraper import main as original_main
    
    print("\n🔍 Modo: Búsqueda Individual Interactiva")
    original_main()


def main():
    """Punto de entrada principal"""
    print("\n" + "="*70)
    print("🚀 GOOGLE MAPS SCRAPER AVANZADO")
    print("="*70)
    print("\nSelecciona modo de operación:")
    print("1. Modo Interactivo (una búsqueda)")
    print("2. Modo Batch (múltiples búsquedas desde config.json)")
    print("3. Salir")
    
    choice = input("\nOpción (1-3): ").strip()
    
    if choice == '1':
        main_interactive()
    elif choice == '2':
        main_batch_mode()
    elif choice == '3':
        print("\n👋 Hasta luego!\n")
    else:
        print("\n❌ Opción inválida")


if __name__ == "__main__":
    main()
