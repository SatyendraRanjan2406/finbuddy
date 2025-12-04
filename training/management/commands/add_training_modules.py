"""
Django management command to add training modules with video URLs.
Usage: python manage.py add_training_modules
"""

from django.core.management.base import BaseCommand
from training.models import TrainingSection


class Command(BaseCommand):
    help = 'Add training modules with video URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing modules before adding new ones',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clear_existing = options['clear']

        # Training modules data
        modules = [
            {
                'title': 'Module 1',
                'description': 'Financial Literacy Module 1 - Introduction to Personal Finance',
                'language': 'en',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+1_HD1080.mp4',
                'order': 1,
                'score': 10.0,
            },
            {
                'title': 'Module 2',
                'description': 'Financial Literacy Module 2 - Understanding Savings and Investments',
                'language': 'en',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+2_HD1080.mp4',
                'order': 2,
                'score': 10.0,
            },
            {
                'title': 'Module 3',
                'description': 'Financial Literacy Module 3 - Banking and Financial Services',
                'language': 'en',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+3_HD1080+.mp4',
                'order': 3,
                'score': 10.0,
            },
            {
                'title': 'Module 4',
                'description': 'Financial Literacy Module 4 - Insurance and Protection',
                'language': 'en',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+4_HD1080.mp4',
                'order': 4,
                'score': 10.0,
            },
            {
                'title': 'Module 5',
                'description': 'Financial Literacy Module 5 - Credit and Loans',
                'language': 'en',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+5_HD1080.mp4',
                'order': 5,
                'score': 10.0,
            },
            {
                'title': 'Module 6',
                'description': 'Financial Literacy Module 6 - Financial Planning and Budgeting',
                'language': 'en',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+6_HD1080.mp4',
                'order': 6,
                'score': 10.0,
            },
            {
                'title': 'Module 1 (Tamil)',
                'description': 'Financial Literacy Module 1 - Introduction to Personal Finance (Tamil)',
                'language': 'ta',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/Module+1_HD1080_Tamil.mp4',
                'order': 7,
                'score': 10.0,
            },
            {
                'title': 'What is a Savings Account',
                'description': 'Learn about savings accounts and how they work',
                'language': 'en',
                'video_url': 'https://finmitratraining.s3.ap-south-1.amazonaws.com/What_is_a_Savings_Account_.mp4',
                'order': 8,
                'score': 10.0,
            },
        ]

        if clear_existing:
            if not dry_run:
                deleted_count = TrainingSection.objects.filter(
                    title__in=[m['title'] for m in modules]
                ).delete()[0]
                self.stdout.write(
                    self.style.WARNING(f'Deleted {deleted_count} existing training sections')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Would delete existing training sections with matching titles')
                )

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for module_data in modules:
            title = module_data['title']
            language = module_data['language']
            
            # Check if module already exists
            existing = TrainingSection.objects.filter(
                title=title,
                language=language
            ).first()

            if existing:
                if not dry_run:
                    # Update existing module
                    for key, value in module_data.items():
                        setattr(existing, key, value)
                    existing.content_type = 'video'  # Set content type since we have video
                    existing.is_active = True
                    existing.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Updated: {title} ({language})')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Would update: {title} ({language})')
                    )
            else:
                if not dry_run:
                    # Create new module
                    module_data['content_type'] = 'video'  # Set content type since we have video
                    module_data['is_active'] = True
                    TrainingSection.objects.create(**module_data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {title} ({language})')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Would create: {title} ({language})')
                    )

        # Summary
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Summary:'))
            self.stdout.write(f'  Created: {created_count}')
            self.stdout.write(f'  Updated: {updated_count}')
            self.stdout.write(f'  Total modules: {created_count + updated_count}')
        self.stdout.write('='*60)

