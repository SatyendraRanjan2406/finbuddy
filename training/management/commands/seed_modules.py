"""
Django management command to seed training modules into the database.
Usage: python manage.py seed_modules
"""
from django.core.management.base import BaseCommand
from training.models import TrainingSection, TrainingQuestion, TrainingOption


class Command(BaseCommand):
    help = 'Seed training modules into the database'

    def handle(self, *args, **options):
        modules_data = [
            {
                "title": "Basics of Banking",
                "description": "Understanding savings accounts & UPI",
                "content_type": "text",
                "questions": [
                    {
                        "text": "What is a minimum balance?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "The maximum amount you can deposit", "is_correct": False},
                            {"text": "The minimum amount you must keep in your account", "is_correct": True},
                            {"text": "The interest rate on your account", "is_correct": False},
                            {"text": "The transaction limit per day", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Which of the following are features of a savings account?",
                        "type": "mcq_multiple",
                        "options": [
                            {"text": "Interest on deposits", "is_correct": True},
                            {"text": "Unlimited withdrawals", "is_correct": False},
                            {"text": "Debit card facility", "is_correct": True},
                            {"text": "No minimum balance requirement", "is_correct": False},
                        ]
                    },
                    {
                        "text": "What is UPI?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "A type of bank account", "is_correct": False},
                            {"text": "Unified Payment Interface for instant money transfers", "is_correct": True},
                            {"text": "A credit card", "is_correct": False},
                            {"text": "A loan product", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Explain in your own words: Why is it important to maintain a minimum balance in your savings account?",
                        "type": "input",
                        "options": []
                    },
                    {
                        "text": "Upload a screenshot of your UPI transaction history (optional)",
                        "type": "file",
                        "options": []
                    },
                ]
            },
            {
                "title": "Digital Payments & Safety",
                "description": "Safe digital transactions",
                "content_type": "text",
                "questions": [
                    {
                        "text": "How can you identify a scam?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "If someone asks for your OTP", "is_correct": True},
                            {"text": "If they offer you money", "is_correct": False},
                            {"text": "If they call from a bank", "is_correct": False},
                            {"text": "If they send an email", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Which of these are red flags for online scams?",
                        "type": "mcq_multiple",
                        "options": [
                            {"text": "Urgent requests for personal information", "is_correct": True},
                            {"text": "Asking for OTP or password", "is_correct": True},
                            {"text": "Too good to be true offers", "is_correct": True},
                            {"text": "Verified payment apps", "is_correct": False},
                        ]
                    },
                    {
                        "text": "What should you do if you receive a suspicious payment link?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "Click it immediately", "is_correct": False},
                            {"text": "Ignore and delete it", "is_correct": True},
                            {"text": "Share it with friends", "is_correct": False},
                            {"text": "Forward it to verify", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Describe a situation where you might have encountered a payment scam. How did you handle it?",
                        "type": "input",
                        "options": []
                    },
                    {
                        "text": "Upload a screenshot of a legitimate payment app interface to show you can identify safe apps",
                        "type": "file",
                        "options": []
                    },
                ]
            },
        ]

        created_count = 0
        updated_count = 0

        for module in modules_data:
            questions_data = module.pop("questions")

            # Create or update Training Section
            training_section, created = TrainingSection.objects.update_or_create(
                title=module["title"],
                defaults=module
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created training: {training_section.title}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"↻ Updated training: {training_section.title}"))

            # ---- CREATE OR UPDATE QUESTIONS ----
            for index, q in enumerate(questions_data, start=1):

                question, q_created = TrainingQuestion.objects.update_or_create(
                    training=training_section,
                    question_text=q["text"],
                    defaults={
                        "question_type": q["type"],
                        "order": index,
                        "language": "en"
                    }
                )

                # Clear old options
                if q["type"] in ["mcq_single", "mcq_multiple"]:
                    TrainingOption.objects.filter(question=question).delete()

                    # Add new options
                    for opt in q["options"]:
                        TrainingOption.objects.create(
                            question=question,
                            option_text=opt["text"],
                            is_correct=opt.get("is_correct", False)
                        )

                if q_created:
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Added question: {q['text']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  ↻ Updated question: {q['text']}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ DONE — {created_count} created, {updated_count} updated."
        ))
