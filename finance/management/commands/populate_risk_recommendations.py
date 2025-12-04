"""
Management command to populate risk recommendation data.
Run: python manage.py populate_risk_recommendations
"""
from django.core.management.base import BaseCommand
from finance.models import RiskRecommendation


class Command(BaseCommand):
    help = "Populate risk recommendation data based on the provided table"

    RISK_DATA = [
        # Income Stability
        {
            "risk_category": "Income Stability",
            "risk_trigger": "Income volatility > 40% or <15 days active/month",
            "risk_level": "🔴 High",
            "recommended_instruments": "Pradhan Mantri Mudra Yojana (PMMY), PM SVANidhi, Post Office Recurring Deposit (RD), Pradhan Mantri Jan-Dhan Yojana (PMJDY), Public Distribution System (PDS / ONORC)",
            "behavioral_tag": "Manage Income Volatility / Emergency Corpus",
            "intro_section": "Your income is fluctuating right now. Let's help you build a safety cushion so slow weeks don't create stress. These options can stabilise your income and help you handle lean periods better.",
            "order": 1,
        },
        {
            "risk_category": "Income Stability",
            "risk_trigger": "Low consistent income (<₹10k/month)",
            "risk_level": "🟠 Medium",
            "recommended_instruments": "Prime Minister's Employment Generation Programme (PMEGP), Pradhan Mantri Jan-Dhan Yojana (PMJDY), Post Office Recurring Deposit (RD), Public Distribution System (PDS / ONORC)",
            "behavioral_tag": "Growth Funding / Stability",
            "intro_section": "Your income is steady but on the lower side. These government-backed plans can support you with subsidised loans and short-term savings to increase your income and stability.",
            "order": 2,
        },
        {
            "risk_category": "Income Stability",
            "risk_trigger": "Stable income",
            "risk_level": "🟢 Low",
            "recommended_instruments": "Public Provident Fund (PPF), National Savings Certificate (NSC), Kisan Vikas Patra (KVP), Post Office Monthly Income Scheme (POMIS), SBI Gold Exchange Traded Scheme, National Pension System (NPS)",
            "behavioral_tag": "Long-term Asset Creation",
            "intro_section": "Great! Your income is stable. This is the best time to start building long-term wealth with safe, reliable investment options.",
            "order": 3,
        },
        # Financial Behavior
        {
            "risk_category": "Financial Behavior",
            "risk_trigger": "Outflow > inflow for 3 months",
            "risk_level": "🔴 High",
            "recommended_instruments": "Post Office Recurring Deposit (RD), Aditya Birla Sun Life Liquid Fund, Edelweiss Liquid Fund, Public Provident Fund (PPF), Pradhan Mantri Mudra Yojana (PMMY)",
            "behavioral_tag": "Build Emergency Corpus",
            "intro_section": "Your expenses have been higher than your income recently. These products can help you start saving consistently and manage cash flow better.",
            "order": 1,
        },
        {
            "risk_category": "Financial Behavior",
            "risk_trigger": "Irregular EMI payments / short-term app loans",
            "risk_level": "🔴 High",
            "recommended_instruments": "Pradhan Mantri Mudra Yojana (PMMY), Prime Minister's Employment Generation Programme (PMEGP), Pradhan Mantri Jan-Dhan Yojana (PMJDY) – Overdraft",
            "behavioral_tag": "Income Stability",
            "intro_section": "We noticed stress from loan repayments. These formal credit options give you safer, low-cost borrowing so you don't fall into debt cycles.",
            "order": 2,
        },
        {
            "risk_category": "Financial Behavior",
            "risk_trigger": "No structured savings",
            "risk_level": "🟠 Medium",
            "recommended_instruments": "Post Office Recurring Deposit (RD), Public Provident Fund (PPF), National Savings Certificate (NSC)",
            "behavioral_tag": "Savings Habit",
            "intro_section": "You're managing well, but saving regularly can make life easier. These small monthly saving plans help build a strong habit effortlessly.",
            "order": 3,
        },
        {
            "risk_category": "Financial Behavior",
            "risk_trigger": "Good savings & behavior",
            "risk_level": "🟢 Low",
            "recommended_instruments": "National Pension System (NPS), SBI Gold Exchange Traded Scheme, Post Office Monthly Income Scheme (POMIS), Public Provident Fund (PPF)",
            "behavioral_tag": "Long-term Asset Creation",
            "intro_section": "You're managing money well! Here are options to grow your wealth further and secure your future.",
            "order": 4,
        },
        # Reliability & Tenure
        {
            "risk_category": "Reliability & Tenure",
            "risk_trigger": "Low completion rate / high cancellations",
            "risk_level": "🔴 High",
            "recommended_instruments": "Pradhan Mantri Mudra Yojana (PMMY), Prime Minister's Employment Generation Programme (PMEGP), Skill Schemes, Pradhan Mantri Jan-Dhan Yojana (PMJDY)",
            "behavioral_tag": "Income Stability",
            "intro_section": "Your work pattern shows some instability. These plans can help you strengthen your income base and explore better livelihood opportunities.",
            "order": 1,
        },
        {
            "risk_category": "Reliability & Tenure",
            "risk_trigger": "New worker (<6 months) but reliable",
            "risk_level": "🟠 Medium",
            "recommended_instruments": "Pradhan Mantri Jan-Dhan Yojana (PMJDY), Pradhan Mantri Suraksha Bima Yojana (PMSBY), Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY), Ayushman Bharat – PM-JAY",
            "behavioral_tag": "Emergency Corpus / Risk",
            "intro_section": "You're doing well! Since you're newer on the platform, here are essential protection plans to keep you and your family secure.",
            "order": 2,
        },
        {
            "risk_category": "Reliability & Tenure",
            "risk_trigger": "Tenure >1 year and reliable",
            "risk_level": "🟢 Low",
            "recommended_instruments": "National Pension System (NPS), Atal Pension Yojana (APY), Public Provident Fund (PPF), Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM)",
            "behavioral_tag": "Long-term Security",
            "intro_section": "Great consistency! These long-term security schemes can help you build a strong retirement foundation.",
            "order": 3,
        },
        # Protection Readiness
        {
            "risk_category": "Protection Readiness",
            "risk_trigger": "No accident/health/life insurance",
            "risk_level": "🔴 High",
            "recommended_instruments": "Pradhan Mantri Suraksha Bima Yojana (PMSBY), Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY), Ayushman Bharat – PM-JAY, Aam Aadmi Bima Yojana (AABY), Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM), Atal Pension Yojana (APY)",
            "behavioral_tag": "Manage Risk Events",
            "intro_section": "You currently do not have any personal protection. These essential covers ensure that your income and family stay protected during emergencies.",
            "order": 1,
        },
        {
            "risk_category": "Protection Readiness",
            "risk_trigger": "Only platform insurance (on-duty cover)",
            "risk_level": "🟠 Medium",
            "recommended_instruments": "Aam Aadmi Bima Yojana (AABY), Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM), Atal Pension Yojana (APY), Pradhan Mantri Suraksha Bima Yojana (PMSBY), Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
            "behavioral_tag": "Full Protection",
            "intro_section": "You are protected only during work hours. These affordable plans protect you 24×7 — on and off duty.",
            "order": 2,
        },
        {
            "risk_category": "Protection Readiness",
            "risk_trigger": "Has full protection",
            "risk_level": "🟢 Low",
            "recommended_instruments": "National Pension System (NPS), SBI Gold Exchange Traded Scheme, Public Provident Fund (PPF), National Savings Certificate (NSC), Post Office Monthly Income Scheme (POMIS), Kisan Vikas Patra (KVP)",
            "behavioral_tag": "Wealth Building",
            "intro_section": "You're well protected — great job! Here are strong investment options to help you grow your money for the long term.",
            "order": 3,
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing risk recommendations before populating',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        clear = options.get('clear', False)

        if clear and not dry_run:
            deleted_count = RiskRecommendation.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f"Deleted {deleted_count} existing risk recommendations")
            )

        created_count = 0
        updated_count = 0

        self.stdout.write(self.style.NOTICE("Starting risk recommendation population..."))

        for data in self.RISK_DATA:
            risk_category = data["risk_category"]
            risk_trigger = data["risk_trigger"]
            risk_level = data["risk_level"]

            # Check if already exists
            existing = RiskRecommendation.objects.filter(
                risk_category=risk_category,
                risk_trigger=risk_trigger,
                risk_level=risk_level
            ).first()

            if existing:
                if not dry_run:
                    for key, value in data.items():
                        setattr(existing, key, value)
                    existing.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Updated: {risk_category} - {risk_level} - {risk_trigger[:50]}"
                    )
                )
            else:
                if not dry_run:
                    RiskRecommendation.objects.create(**data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created: {risk_category} - {risk_level} - {risk_trigger[:50]}"
                    )
                )

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✓ Created: {created_count} recommendations"))
        self.stdout.write(self.style.SUCCESS(f"✓ Updated: {updated_count} recommendations"))
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n⚠ DRY RUN MODE - No changes were made")
            )
        
        self.stdout.write("=" * 60)

