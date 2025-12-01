"""
Django management command to seed training sections with mixed content (video + text).
Usage: python manage.py seed_mixed_sections
"""
from django.core.management.base import BaseCommand
from training.models import TrainingSection, TrainingQuestion, TrainingOption


class Command(BaseCommand):
    help = 'Seed training sections with mixed content (video + text)'

    def handle(self, *args, **options):
        mixed_sections_data = [
            {
                "title": "Introduction to Digital Banking",
                "description": "Learn the basics of digital banking with video tutorials and detailed text guides",
                "content_type": "mixed",
                "language": "en",
                "video_url": "https://example.com/videos/digital-banking-intro.mp4",
                "audio_url": None,
                "text_content": """
# Introduction to Digital Banking

Digital banking has revolutionized the way we manage our finances. This comprehensive guide will help you understand:

## Key Concepts
1. **Online Banking**: Access your account 24/7 from anywhere
2. **Mobile Banking**: Manage finances on the go with your smartphone
3. **Digital Payments**: UPI, wallets, and other payment methods
4. **Security**: Best practices to keep your account safe

## Benefits
- Convenience: Bank anytime, anywhere
- Speed: Instant transactions
- Cost-effective: Lower fees than traditional banking
- Transparency: Real-time balance and transaction history

## Getting Started
To begin using digital banking, you'll need:
- A smartphone or computer
- Internet connection
- Bank account with digital banking enabled
- Secure login credentials

Start your journey to financial freedom today!
                """,
                "score": 15.0,
                "order": 1,
                "is_active": True,
                "questions": [
                    {
                        "text": "What are the main benefits of digital banking?",
                        "type": "mcq_multiple",
                        "options": [
                            {"text": "24/7 access to your account", "is_correct": True},
                            {"text": "Instant transactions", "is_correct": True},
                            {"text": "Lower fees", "is_correct": True},
                            {"text": "Requires physical branch visits", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Which device do you need for digital banking?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "Only a desktop computer", "is_correct": False},
                            {"text": "Smartphone or computer with internet", "is_correct": True},
                            {"text": "Only a tablet", "is_correct": False},
                            {"text": "None of the above", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Describe how digital banking has helped you or someone you know manage finances better.",
                        "type": "input",
                        "options": []
                    }
                ]
            },
            {
                "title": "Understanding UPI Payments",
                "description": "Master UPI payments with step-by-step video guide and comprehensive text documentation",
                "content_type": "mixed",
                "language": "en",
                "video_url": "https://example.com/videos/upi-payments-guide.mp4",
                "audio_url": None,
                "text_content": """
# Understanding UPI Payments

Unified Payments Interface (UPI) is India's revolutionary payment system that allows instant money transfers.

## What is UPI?
UPI is a real-time payment system developed by the National Payments Corporation of India (NPCI). It enables instant money transfers between bank accounts using a mobile app.

## How UPI Works
1. **Create UPI ID**: Link your bank account to a UPI app
2. **Set PIN**: Create a secure 4-6 digit UPI PIN
3. **Send Money**: Enter recipient's UPI ID or scan QR code
4. **Enter Amount**: Specify the amount to transfer
5. **Authenticate**: Enter your UPI PIN to complete transaction

## Popular UPI Apps
- Google Pay
- PhonePe
- Paytm
- BHIM
- Amazon Pay

## Safety Tips
- Never share your UPI PIN with anyone
- Verify recipient details before sending money
- Use secure networks for transactions
- Enable two-factor authentication
- Check transaction history regularly

## Advantages
- Instant transfers
- 24/7 availability
- No need for bank account details
- Works with any bank
- Free of charge
                """,
                "score": 20.0,
                "order": 2,
                "is_active": True,
                "questions": [
                    {
                        "text": "What does UPI stand for?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "Unified Payment Interface", "is_correct": True},
                            {"text": "Universal Payment Integration", "is_correct": False},
                            {"text": "United Payment Infrastructure", "is_correct": False},
                            {"text": "Unique Payment Identifier", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Which of the following are popular UPI apps?",
                        "type": "mcq_multiple",
                        "options": [
                            {"text": "Google Pay", "is_correct": True},
                            {"text": "PhonePe", "is_correct": True},
                            {"text": "Paytm", "is_correct": True},
                            {"text": "WhatsApp", "is_correct": False},
                        ]
                    },
                    {
                        "text": "What should you never share with anyone regarding UPI?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "Your UPI ID", "is_correct": False},
                            {"text": "Your UPI PIN", "is_correct": True},
                            {"text": "Your phone number", "is_correct": False},
                            {"text": "Your bank name", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Explain the steps to send money using UPI in your own words.",
                        "type": "input",
                        "options": []
                    }
                ]
            },
            {
                "title": "Savings and Investment Basics",
                "description": "Learn about savings and investments through video lessons and detailed reading material",
                "content_type": "mixed",
                "language": "en",
                "video_url": "https://example.com/videos/savings-investment-basics.mp4",
                "audio_url": None,
                "text_content": """
# Savings and Investment Basics

Building wealth starts with understanding the difference between saving and investing.

## Savings vs Investments

### Savings
- Money set aside for short-term goals
- Low risk, low returns
- Easily accessible
- Examples: Savings account, fixed deposits

### Investments
- Money put to work for long-term growth
- Higher risk, higher potential returns
- May have lock-in periods
- Examples: Mutual funds, stocks, bonds

## Types of Savings Accounts
1. **Regular Savings Account**: Basic account with interest
2. **High-Yield Savings Account**: Higher interest rates
3. **Fixed Deposit (FD)**: Locked amount for fixed period
4. **Recurring Deposit (RD)**: Regular monthly deposits

## Investment Options for Beginners
1. **Mutual Funds**: Professionally managed funds
2. **Systematic Investment Plan (SIP)**: Regular investments
3. **Public Provident Fund (PPF)**: Government-backed savings
4. **National Pension Scheme (NPS)**: Retirement planning

## Key Principles
- Start early to benefit from compound interest
- Diversify your investments
- Invest according to your risk tolerance
- Review and adjust your portfolio regularly
- Never invest money you might need immediately

## Emergency Fund
Always maintain an emergency fund covering 3-6 months of expenses in a savings account.
                """,
                "score": 25.0,
                "order": 3,
                "is_active": True,
                "questions": [
                    {
                        "text": "What is the main difference between savings and investments?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "Savings are for long-term, investments for short-term", "is_correct": False},
                            {"text": "Savings are low risk/low return, investments are higher risk/higher return", "is_correct": True},
                            {"text": "There is no difference", "is_correct": False},
                            {"text": "Savings require more money", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Which of these are types of savings accounts?",
                        "type": "mcq_multiple",
                        "options": [
                            {"text": "Regular Savings Account", "is_correct": True},
                            {"text": "Fixed Deposit", "is_correct": True},
                            {"text": "Recurring Deposit", "is_correct": True},
                            {"text": "Stock Trading Account", "is_correct": False},
                        ]
                    },
                    {
                        "text": "How many months of expenses should an emergency fund cover?",
                        "type": "mcq_single",
                        "options": [
                            {"text": "1-2 months", "is_correct": False},
                            {"text": "3-6 months", "is_correct": True},
                            {"text": "12 months", "is_correct": False},
                            {"text": "No emergency fund needed", "is_correct": False},
                        ]
                    },
                    {
                        "text": "Describe your current savings strategy and how you plan to improve it.",
                        "type": "input",
                        "options": []
                    }
                ]
            }
        ]

        created_count = 0
        updated_count = 0

        for section_data in mixed_sections_data:
            questions_data = section_data.pop("questions")

            # Create or update Training Section
            training_section, created = TrainingSection.objects.update_or_create(
                title=section_data["title"],
                language=section_data.get("language", "en"),
                defaults=section_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created training: {training_section.title}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"↻ Updated training: {training_section.title}"))

            # Create or update Questions
            for index, q in enumerate(questions_data, start=1):
                question, q_created = TrainingQuestion.objects.update_or_create(
                    training=training_section,
                    question_text=q["text"],
                    defaults={
                        "question_type": q["type"],
                        "order": index,
                        "language": section_data.get("language", "en")
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
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Added question: {q['text'][:50]}..."))
                else:
                    self.stdout.write(self.style.WARNING(f"  ↻ Updated question: {q['text'][:50]}..."))

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ DONE — {created_count} created, {updated_count} updated."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"✓ All sections have video + text content (has_video: true, has_audio: false, has_text: true)"
        ))

