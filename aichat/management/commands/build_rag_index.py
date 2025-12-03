import json
import logging
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.conf import settings
from openai import OpenAI

from training.models import TrainingSection
from finance.models import Product

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Build RAG index from TrainingSection and Product content (including scraped URLs) into rag_index.jsonl"

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-scraping',
            action='store_true',
            help='Skip scraping product URLs (use only DB fields)',
        )
        parser.add_argument(
            '--scrape-timeout',
            type=int,
            default=10,
            help='Timeout in seconds for each URL scrape (default: 10)',
        )

    def scrape_url(self, url: str, timeout: int = 10) -> str:
        """
        Scrape text content from a product URL.
        Returns cleaned text content or empty string if failed.
        """
        if not url or not url.startswith(('http://', 'https://')):
            return ""
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up: remove excessive whitespace
            text = ' '.join(text.split())
            
            # Limit to reasonable length (avoid huge pages)
            MAX_SCRAPED_LENGTH = 5000
            if len(text) > MAX_SCRAPED_LENGTH:
                text = text[:MAX_SCRAPED_LENGTH] + "..."
            
            return text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return ""
        except Exception as e:
            logger.warning(f"Error parsing {url}: {e}")
            return ""

    def handle(self, *args, **options):
        client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))
        if not client.api_key:
            self.stderr.write(self.style.ERROR("OPENAI_API_KEY not configured; cannot build RAG index."))
            return

        docs = []

        # Training sections
        for section in TrainingSection.objects.filter(is_active=True):
            text_parts = [
                section.title or "",
                section.description or "",
                section.text_content or "",
            ]
            text = " ".join(p for p in text_parts if p).strip()
            if not text:
                continue
            docs.append(
                {
                    "id": f"training:{section.id}",
                    "type": "training_section",
                    "title": section.title,
                    "text": text,
                    "metadata": {
                        "score": float(section.score or 0),
                        "order": section.order,
                    },
                }
            )

        # Products (with optional URL scraping)
        skip_scraping = options.get('skip_scraping', False)
        scrape_timeout = options.get('scrape_timeout', 10)
        
        products_with_urls = Product.objects.exclude(official_url__isnull=True).exclude(official_url="")
        total_products = Product.objects.count()
        products_to_scrape = products_with_urls.count()
        
        if not skip_scraping and products_to_scrape > 0:
            self.stdout.write(
                self.style.NOTICE(
                    f"Scraping {products_to_scrape} product URLs (timeout: {scrape_timeout}s each)..."
                )
            )
        
        for p in Product.objects.all():
            text_parts = [
                p.name or "",
                p.scheme_description or "",
                p.purpose or "",
                p.eligibility or "",
            ]
            
            # Scrape official_url if available
            scraped_content = ""
            if not skip_scraping and p.official_url:
                self.stdout.write(f"  Scraping {p.official_url}...")
                scraped_content = self.scrape_url(p.official_url, timeout=scrape_timeout)
                if scraped_content:
                    self.stdout.write(
                        self.style.SUCCESS(f"    ✓ Scraped {len(scraped_content)} chars")
                    )
                else:
                    self.stdout.write(self.style.WARNING(f"    ✗ Failed to scrape"))
                time.sleep(0.5)  # Be polite to servers
            
            # Combine DB fields + scraped content
            if scraped_content:
                text_parts.append(f"\n\nOfficial website content:\n{scraped_content}")
            
            text = " ".join(p_ for p_ in text_parts if p_).strip()
            if not text:
                continue
            
            metadata = {
                "ufhs_tag": p.ufhs_tag,
                "category": p.category,
            }
            if p.official_url:
                metadata["official_url"] = p.official_url
            
            docs.append(
                {
                    "id": f"product:{p.id}",
                    "type": "product",
                    "title": p.name,
                    "text": text,
                    "metadata": metadata,
                }
            )

        if not docs:
            self.stderr.write(self.style.WARNING("No documents found to index."))
            return

        texts = [d["text"] for d in docs]
        self.stdout.write(self.style.NOTICE(f"Creating embeddings for {len(texts)} documents..."))

        resp = client.embeddings.create(
            model="text-embedding-3-large",
            input=texts,
        )
        embeddings = [item.embedding for item in resp.data]

        index_path = Path(settings.BASE_DIR) / "rag_index.jsonl"
        with index_path.open("w", encoding="utf-8") as f:
            for doc, emb in zip(docs, embeddings):
                f.write(json.dumps({"doc": doc, "embedding": emb}) + "\n")

        self.stdout.write(self.style.SUCCESS(f"RAG index built at {index_path}"))


