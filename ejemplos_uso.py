"""
Ejemplos de Uso - Google Maps Scraper Educativo
================================================
Este archivo contiene ejemplos prácticos de diferentes escenarios de uso.
"""

from google_maps_scraper import GoogleMapsScraperAdvanced, BusinessData
from google_maps_scraper_advanced import (
    ConfigManager,
    CacheManager,
    DataValidator,
    ReportGenerator,
    BatchScraperManager
)
import pandas as pd
from typing import List


# ============================================================================
# EJEMPLO 1: Búsqueda Básica
# ============================================================================
def ejemplo_busqueda_basica():
    """
    Ejemplo más simple: buscar restaurantes en una ciudad
    """
    print("\n" + "="*70)
    print("EJEMPLO 1: Búsqueda Básica")
    print("="*70)
    
    # Crear scraper
    scraper = GoogleMapsScraperAdvanced(headless=False)
    
    try:
        # Buscar restaurantes
        results = scraper.search_businesses(
            categoria="restaurantes italianos",
            ubicacion="Barcelona, España",
            max_results=10
        )
        
        # Mostrar algunos resultados
        print(f"\n✅ Se encontraron {len(results)} restaurantes:")
        for i, business in enumerate(results[:5], 1):
            print(f"\n{i}. {business.nombre}")
            print(f"   📍 {business.direccion}")
            print(f"   ⭐ Rating: {business.rating}/5 ({business.reviews_count} reseñas)")
            if business.telefono:
                print(f"   📞 {business.telefono}")
        
        # Exportar
        scraper.export_to_csv("ejemplo1_restaurantes.csv")
        
    finally:
        scraper.close()


# ============================================================================
# EJEMPLO 2: Búsqueda con Análisis de Datos
# ============================================================================
def ejemplo_analisis_datos():
    """
    Buscar y analizar datos con pandas
    """
    print("\n" + "="*70)
    print("EJEMPLO 2: Búsqueda con Análisis")
    print("="*70)
    
    scraper = GoogleMapsScraperAdvanced(headless=False)
    
    try:
        results = scraper.search_businesses(
            categoria="gimnasios",
            ubicacion="Madrid, España",
            max_results=30
        )
        
        # Convertir a DataFrame para análisis
        from dataclasses import asdict
        df = pd.DataFrame([asdict(b) for b in results])
        
        print("\n📊 ANÁLISIS DE DATOS:")
        print(f"Total de gimnasios: {len(df)}")
        print(f"\nRating promedio: {df['rating'].mean():.2f}")
        print(f"Rating máximo: {df['rating'].max():.2f}")
        print(f"Rating mínimo: {df['rating'].min():.2f}")
        
        print(f"\nGimnasios con teléfono: {df['telefono'].notna().sum()}")
        print(f"Gimnasios con web: {df['sitio_web'].notna().sum()}")
        print(f"Gimnasios con email: {df['email'].notna().sum()}")
        
        # Top 5 mejor calificados
        print("\n🏆 TOP 5 MEJOR CALIFICADOS:")
        top5 = df.nlargest(5, 'rating')[['nombre', 'rating', 'reviews_count']]
        print(top5.to_string(index=False))
        
        # Exportar
        df.to_excel("ejemplo2_gimnasios_analisis.xlsx", index=False)
        
    finally:
        scraper.close()


# ============================================================================
# EJEMPLO 3: Uso del Sistema de Cache
# ============================================================================
def ejemplo_cache():
    """
    Demostrar el uso del cache para evitar re-scraping
    """
    print("\n" + "="*70)
    print("EJEMPLO 3: Sistema de Cache")
    print("="*70)
    
    cache = CacheManager()
    categoria = "hoteles"
    ubicacion = "Valencia, España"
    
    # Primera ejecución: scraping real
    print("\n🔍 Primera ejecución - Realizando scraping...")
    scraper = GoogleMapsScraperAdvanced(headless=False)
    
    try:
        results = scraper.search_businesses(
            categoria=categoria,
            ubicacion=ubicacion,
            max_results=15
        )
        
        # Guardar en cache
        cache.set(categoria, ubicacion, results)
        print(f"✅ {len(results)} resultados guardados en cache")
        
    finally:
        scraper.close()
    
    # Segunda ejecución: desde cache
    print("\n♻️  Segunda ejecución - Cargando desde cache...")
    cached_results = cache.get(categoria, ubicacion, max_age_hours=24)
    
    if cached_results:
        print(f"✅ {len(cached_results)} resultados cargados desde cache!")
        print("⚡ Mucho más rápido sin necesidad de scraping")
    else:
        print("❌ Cache no disponible o expirado")


# ============================================================================
# EJEMPLO 4: Validación de Datos
# ============================================================================
def ejemplo_validacion():
    """
    Validar la calidad de datos extraídos
    """
    print("\n" + "="*70)
    print("EJEMPLO 4: Validación de Datos")
    print("="*70)
    
    scraper = GoogleMapsScraperAdvanced(headless=False)
    validator = DataValidator()
    
    try:
        results = scraper.search_businesses(
            categoria="farmacias",
            ubicacion="Sevilla, España",
            max_results=20
        )
        
        # Validar cada resultado
        valid_count = 0
        invalid_fields = {
            'telefono': 0,
            'email': 0,
            'sitio_web': 0,
            'coordenadas': 0
        }
        
        for business in results:
            validation = validator.validate_business(business)
            
            if all(validation.values()):
                valid_count += 1
            
            for field, is_valid in validation.items():
                if not is_valid and field != 'nombre':
                    invalid_fields[field] += 1
        
        print(f"\n📊 REPORTE DE VALIDACIÓN:")
        print(f"Total de negocios: {len(results)}")
        print(f"Completamente válidos: {valid_count}")
        print(f"\nCampos inválidos o faltantes:")
        for field, count in invalid_fields.items():
            print(f"  - {field.capitalize()}: {count}")
        
        # Filtrar solo los completamente válidos
        valid_businesses = [
            b for b in results
            if all(validator.validate_business(b).values())
        ]
        
        print(f"\n✅ Exportando {len(valid_businesses)} negocios válidos...")
        
        from dataclasses import asdict
        import json
        with open("ejemplo4_farmacias_validas.json", 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(b) for b in valid_businesses],
                f,
                indent=2,
                ensure_ascii=False
            )
        
    finally:
        scraper.close()


# ============================================================================
# EJEMPLO 5: Procesamiento por Lotes (Batch)
# ============================================================================
def ejemplo_batch():
    """
    Procesar múltiples búsquedas automáticamente
    """
    print("\n" + "="*70)
    print("EJEMPLO 5: Procesamiento por Lotes")
    print("="*70)
    
    config_manager = ConfigManager()
    batch_manager = BatchScraperManager(config_manager, use_cache=True)
    
    # Definir múltiples búsquedas
    searches = [
        {
            'categoria': 'cafeterías',
            'ubicacion': 'Málaga, España',
            'max_results': 15
        },
        {
            'categoria': 'panaderías',
            'ubicacion': 'Málaga, España',
            'max_results': 15
        },
        {
            'categoria': 'librerías',
            'ubicacion': 'Málaga, España',
            'max_results': 10
        }
    ]
    
    print(f"\n🎯 Ejecutando {len(searches)} búsquedas...")
    
    # Ejecutar batch
    results_dict = batch_manager.run_batch(searches)
    
    # Exportar todos los resultados
    batch_manager.export_all("./resultados_ejemplo5")
    
    # Reporte global
    print("\n" + "="*70)
    print("📈 REPORTE GLOBAL")
    print("="*70)
    summary = ReportGenerator.generate_summary(batch_manager.all_results)
    ReportGenerator.print_summary(summary)


# ============================================================================
# EJEMPLO 6: Comparación Entre Ciudades
# ============================================================================
def ejemplo_comparacion_ciudades():
    """
    Comparar la misma categoría en diferentes ciudades
    """
    print("\n" + "="*70)
    print("EJEMPLO 6: Comparación Entre Ciudades")
    print("="*70)
    
    categoria = "pizzerías"
    ciudades = ["Madrid, España", "Barcelona, España", "Valencia, España"]
    
    scraper = GoogleMapsScraperAdvanced(headless=False)
    resultados_por_ciudad = {}
    
    try:
        for ciudad in ciudades:
            print(f"\n🔍 Buscando {categoria} en {ciudad}...")
            results = scraper.search_businesses(
                categoria=categoria,
                ubicacion=ciudad,
                max_results=20
            )
            resultados_por_ciudad[ciudad] = results
        
        # Análisis comparativo
        print("\n" + "="*70)
        print("📊 COMPARACIÓN ENTRE CIUDADES")
        print("="*70)
        
        for ciudad, results in resultados_por_ciudad.items():
            from dataclasses import asdict
            df = pd.DataFrame([asdict(b) for b in results])
            
            print(f"\n📍 {ciudad}:")
            print(f"   Total encontradas: {len(results)}")
            print(f"   Rating promedio: {df['rating'].mean():.2f}")
            print(f"   Con teléfono: {df['telefono'].notna().sum()}")
            print(f"   Con web: {df['sitio_web'].notna().sum()}")
            print(f"   Reseñas promedio: {df['reviews_count'].mean():.0f}")
        
        # Exportar comparación
        comparison_data = []
        for ciudad, results in resultados_por_ciudad.items():
            for business in results:
                from dataclasses import asdict
                data = asdict(business)
                data['ciudad'] = ciudad
                comparison_data.append(data)
        
        df_comparison = pd.DataFrame(comparison_data)
        df_comparison.to_excel("ejemplo6_comparacion_ciudades.xlsx", index=False)
        
    finally:
        scraper.close()


# ============================================================================
# EJEMPLO 7: Búsqueda Específica con Filtros
# ============================================================================
def ejemplo_filtros_avanzados():
    """
    Buscar y filtrar por criterios específicos
    """
    print("\n" + "="*70)
    print("EJEMPLO 7: Filtros Avanzados")
    print("="*70)
    
    scraper = GoogleMapsScraperAdvanced(headless=False)
    
    try:
        results = scraper.search_businesses(
            categoria="restaurantes veganos",
            ubicacion="Barcelona, España",
            max_results=50
        )
        
        # Aplicar filtros
        print("\n🔍 APLICANDO FILTROS:")
        
        # Filtro 1: Rating >= 4.5
        high_rated = [b for b in results if b.rating and b.rating >= 4.5]
        print(f"\n⭐ Con rating >= 4.5: {len(high_rated)} de {len(results)}")
        
        # Filtro 2: Más de 100 reseñas
        popular = [b for b in results if b.reviews_count and b.reviews_count >= 100]
        print(f"💬 Con más de 100 reseñas: {len(popular)} de {len(results)}")
        
        # Filtro 3: Con web y teléfono
        complete_info = [
            b for b in results 
            if b.sitio_web and b.telefono
        ]
        print(f"📞🌐 Con web y teléfono: {len(complete_info)} de {len(results)}")
        
        # Combinar filtros: rating alto Y popular Y info completa
        premium = [
            b for b in results
            if b.rating and b.rating >= 4.5
            and b.reviews_count and b.reviews_count >= 100
            and b.sitio_web and b.telefono
        ]
        
        print(f"\n🏆 PREMIUM (todos los filtros): {len(premium)}")
        print("\nTop 5 Premium:")
        for i, business in enumerate(sorted(premium, key=lambda x: x.rating, reverse=True)[:5], 1):
            print(f"{i}. {business.nombre}")
            print(f"   ⭐ {business.rating} ({business.reviews_count} reseñas)")
            print(f"   📞 {business.telefono}")
            print(f"   🌐 {business.sitio_web}")
        
        # Exportar solo los premium
        from dataclasses import asdict
        import json
        with open("ejemplo7_premium.json", 'w', encoding='utf-8') as f:
            json.dump([asdict(b) for b in premium], f, indent=2, ensure_ascii=False)
        
    finally:
        scraper.close()


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================
def menu():
    """
    Menú interactivo para ejecutar ejemplos
    """
    ejemplos = {
        '1': ('Búsqueda Básica', ejemplo_busqueda_basica),
        '2': ('Análisis de Datos', ejemplo_analisis_datos),
        '3': ('Sistema de Cache', ejemplo_cache),
        '4': ('Validación de Datos', ejemplo_validacion),
        '5': ('Procesamiento por Lotes', ejemplo_batch),
        '6': ('Comparación Entre Ciudades', ejemplo_comparacion_ciudades),
        '7': ('Filtros Avanzados', ejemplo_filtros_avanzados),
    }
    
    print("\n" + "="*70)
    print("🎓 EJEMPLOS DE USO - Google Maps Scraper Educativo")
    print("="*70)
    print("\n⚠️  Todos los ejemplos son SOLO para propósitos educativos\n")
    
    print("Ejemplos disponibles:")
    for key, (nombre, _) in ejemplos.items():
        print(f"{key}. {nombre}")
    print("0. Salir")
    
    while True:
        opcion = input("\n🔍 Selecciona un ejemplo (0-7): ").strip()
        
        if opcion == '0':
            print("\n👋 ¡Hasta luego!\n")
            break
        elif opcion in ejemplos:
            nombre, funcion = ejemplos[opcion]
            print(f"\n▶️  Ejecutando: {nombre}")
            try:
                funcion()
                print(f"\n✅ Ejemplo completado: {nombre}")
            except KeyboardInterrupt:
                print("\n⚠️  Ejemplo interrumpido")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    menu()
