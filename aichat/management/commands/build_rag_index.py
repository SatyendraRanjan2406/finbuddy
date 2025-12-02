import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
from openai import OpenAI

from training.models import TrainingSection
from finance.models import Product


class Command(BaseCommand):
    help = "Build RAG index from TrainingSection and Product content into rag_index.jsonl"

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

        # Products
        for p in Product.objects.all():
            text_parts = [
                p.name or "",
                p.scheme_description or "",
                p.purpose or "",
                p.eligibility or "",
            ]
            text = " ".join(p_ for p_ in text_parts if p_).strip()
            if not text:
                continue
            docs.append(
                {
                    "id": f"product:{p.id}",
                    "type": "product",
                    "title": p.name,
                    "text": text,
                    "metadata": {
                        "ufhs_tag": p.ufhs_tag,
                        "category": p.category,
                    },
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


