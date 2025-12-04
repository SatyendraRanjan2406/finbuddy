from django.core.management.base import BaseCommand
from training.models import TrainingSection

MODULES = [
    {
        "title": "Module 1",
        "description": "Financial Health: Module 1",
        "video_url": "https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+1_HD1080.mp4",
        "language": "en",
        "order": 1,
    },
    {
        "title": "Module 2",
        "description": "Financial Health: Module 2",
        "video_url": "https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+2_HD1080.mp4",
        "language": "en",
        "order": 2,
    },
    {
        "title": "Module 3",
        "description": "Financial Health: Module 3",
        "video_url": "https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+3_HD1080+.mp4",
        "language": "en",
        "order": 3,
    },
    {
        "title": "Module 4",
        "description": "Financial Health: Module 4",
        "video_url": "https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+4_HD1080.mp4",
        "language": "en",
        "order": 4,
    },
    {
        "title": "Module 1 (Tamil)",
        "description": "Financial Health: Module 1 (Tamil)",
        "video_url": "https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+1_HD1080_Tamil.mp4",
        "language": "ta",
        "order": 5,
    },
    {
        "title": "What is a Savings Account?",
        "description": "Explainer: What is a Savings Account?",
        "video_url": "https://finmitratraining.s3.ap-south-1.amazonaws.com/What_is_a_Savings_Account_.mp4",
        "language": "en",
        "order": 6,
    },
]

class Command(BaseCommand):
    help = "Seed training modules with video URLs"

    def handle(self, *args, **options):
        for module in MODULES:
            obj, created = TrainingSection.objects.get_or_create(
                title=module["title"],
                defaults={
                    "description": module["description"],
                    "video_url": module["video_url"],
                    "language": module["language"],
                    "order": module["order"],
                    "content_type": "video",
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {obj.title}"))
