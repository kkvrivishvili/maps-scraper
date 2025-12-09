
import logging
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Optional, Set

logger = logging.getLogger(__name__)

class WebsiteEmailExtractor:
    """Extrae emails de sitios web visitando home y páginas de contacto"""
    
    def __init__(self, timeout: int = 10, max_depth: int = 1):
        self.timeout = timeout
        self.max_depth = max_depth
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        # Regex para emails
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        # Palabras clave para páginas de contacto (ignorando case)
        self.contact_keywords = ['contacto', 'contact', 'contact-us', 'about', 'sobre-nosotros', 'contactanos']

    def extract(self, url: str) -> Optional[str]:
        """
        Intenta extraer un email del sitio web.
        1. Escanea la Home.
        2. Si no encuentra, busca link de Contacto y escanea.
        """
        if not url:
            return None
            
        # Asegurar esquema
        if not url.startswith('http'):
            url = 'http://' + url
            
        emails = set()
        visited = set()
        
        try:
            # 1. Escanear Home
            logger.info(f"Escaneando sitio web: {url}")
            soup, current_url = self._get_soup(url)
            if not soup:
                return None
                
            visited.add(current_url)
            self._find_emails_in_soup(soup, emails)
            
            if emails:
                 return self._select_best_email(emails)
            
            # 2. Buscar página de contacto
            contact_link = self._find_contact_link(soup, current_url)
            if contact_link:
                logger.info(f"Visitando página de contacto: {contact_link}")
                contact_soup, _ = self._get_soup(contact_link)
                if contact_soup:
                    self._find_emails_in_soup(contact_soup, emails)
            
            return self._select_best_email(emails)
            
        except Exception as e:
            logger.warning(f"Error extrayendo email de {url}: {e}")
            return None

    def _get_soup(self, url: str):
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser'), response.url
        except Exception:
            return None, None

    def _find_emails_in_soup(self, soup: BeautifulSoup, emails: Set[str]):
        # 1. Buscar mailto:
        for a in soup.select('a[href^="mailto:"]'):
            email = a['href'].replace('mailto:', '').split('?')[0].strip()
            if self._is_valid_email(email):
                emails.add(email)
                
        # 2. Buscar texto visible (más lento, backup)
        text = soup.get_text()
        found = self.email_pattern.findall(text)
        for email in found:
            if self._is_valid_email(email):
                emails.add(email)

    def _find_contact_link(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().lower()
            href_lower = href.lower()
            
            # Verificar si parece un link de contacto
            if any(keyword in href_lower or keyword in text for keyword in self.contact_keywords):
                full_url = urljoin(base_url, href)
                # Validar que sea del mismo dominio
                if urlparse(base_url).netloc == urlparse(full_url).netloc:
                    return full_url
        return None

    def _is_valid_email(self, email: str) -> bool:
        # Filtros básicos de basura
        if not email or len(email) > 100: return False
        if email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js')): return False
        if 'example.com' in email or 'domain.com' in email: return False
        return True

    def _select_best_email(self, emails: Set[str]) -> Optional[str]:
        if not emails:
            return None
        
        # Priorizar info@, contacto@, hola@
        priority = ['info', 'contacto', 'contact', 'hola', 'ventas', 'admin']
        email_list = list(emails)
        
        # Ordenar: primero los que empiezan con prioridad, luego por longitud (más corto suele ser mejor)
        email_list.sort(key=lambda x: (
            not any(x.lower().startswith(p) for p in priority), # False (0) viene antes que True (1), así que negamos
            len(x)
        ))
        
        return email_list[0]
