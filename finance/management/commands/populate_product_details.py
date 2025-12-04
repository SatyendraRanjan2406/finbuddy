"""
Management command to populate product details based on product name mapping.
Run: python manage.py populate_product_details
"""
from django.core.management.base import BaseCommand
from finance.models import Product


class Command(BaseCommand):
    help = "Populate product details field based on product name mapping"

    # Product name to details mapping
    PRODUCT_DETAILS_MAPPING = {
        "Pradhan Mantri Jan-Dhan Yojana (PMJDY)": "PMJDY is a zero-balance bank account with a RuPay card, insurance benefits, and access to small overdrafts. It benefits you by giving a safe place for your earnings, helping you build financial history, and allowing access to an emergency overdraft when income drops.",
        "Public Provident Fund (PPF)": "PPF is a long-term government-backed savings scheme with guaranteed returns and tax benefits. It helps you by forcing long-term disciplined savings and growing a safe corpus for future needs, ideal when your income becomes stable.",
        "National Savings Certificate (NSC)": "NSC is a secure 5-year fixed-return savings certificate. It gives you predictable, government-backed growth, making it useful for medium-term goals like education or emergencies.",
        "Kisan Vikas Patra (KVP)": "KVP doubles your money in a fixed period (approx 9–10 years). It helps you by offering safe long-term growth and building funds for major future expenses.",
        "Post Office Recurring Deposit (RD)": "The Post Office RD lets you save a small fixed amount monthly. It helps you create an emergency fund even when income is inconsistent, making it perfect for gig workers facing fluctuating cash flow.",
        "Sukanya Samriddhi Yojana (SSY)": "SSY is a high-interest savings scheme for parents of a girl child. It helps you secure your daughter's future by building a large, safe fund for education or marriage.",
        "Pradhan Mantri Mudra Yojana (PMMY)": "PMMY provides collateral-free loans to small entrepreneurs. It helps you by funding essential tools, vehicle repairs, or business upgrades—useful during emergencies or when you need to boost earnings—but should be taken only if necessary.",
        "PM SVANidhi": "PM SVANidhi offers working-capital loans to street vendors. It benefits you by giving access to stock or daily capital when income is unstable, helping stabilise earnings.",
        "Prime Minister's Employment Generation Programme (PMEGP)": "PMEGP is a subsidy-linked credit scheme for micro-enterprises. It helps you start or upgrade a small business and improve income stability if gig earnings are insufficient.",
        "Pradhan Mantri Suraksha Bima Yojana (PMSBY)": "PMSBY is an accidental death and disability insurance scheme. It protects your family financially if an accident impacts your ability to work—a major risk for gig workers on the road.",
        "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)": "PMJJBY is an affordable life insurance scheme. It ensures your family gets financial support if something happens to you, making it essential for dependents.",
        "Ayushman Bharat – PM-JAY": "PM-JAY offers ₹5 lakh annual health coverage for eligible families. It protects you from the heavy cost of hospitalisation, ensuring medical emergencies don't wipe out your savings.",
        "Aam Aadmi Bima Yojana (AABY)": "AABY is life and accident insurance for informal workers. It gives extra protection for people in high-risk jobs, ensuring coverage even when platform-provided insurance is limited.",
        "Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM)": "PM-SYM is a contributory pension scheme for unorganised workers. It benefits you by ensuring you have a reliable monthly income after age 60, reducing dependence on gig income later in life.",
        "Atal Pension Yojana (APY)": "APY is a government pension scheme that pays a guaranteed amount post-retirement. It helps you plan financial security for old age with small monthly contributions.",
        "National Social Assistance Programme (NSAP)": "NSAP provides financial assistance to elderly, widows, and persons with disabilities. It helps families by ensuring vulnerable members have a basic income safety net.",
        "National Pension System (NPS)": "NPS is a voluntary retirement-saving system with market-linked returns. It helps you build a long-term pension corpus with higher returns over time, ideal when aiming for better retirement security.",
        "National Pension Scheme for Traders and Self-Employed Persons (NPS-Traders)": "This is a voluntary pension program for traders and self-employed workers. It benefits gig workers doing small independent business by providing a stable pension after 60.",
        "Public Distribution System (PDS / ONORC)": "PDS/ONORC provides subsidised food grains, accessible nationwide for migrant workers. It helps you lower monthly household expenses, freeing money for savings or emergencies.",
        "Pradhan Mantri Awas Yojana – Gramin (PMAY-G)": "PMAY-G supports construction of rural homes with government assistance. It helps you secure long-term housing stability and reduces future rental burden.",
        "Aditya Birla Sun Life Liquid Fund": "This low-risk mutual fund offers high liquidity with stable returns. It helps you park emergency savings safely and withdraw quickly whenever gig income dips.",
        "Edelweiss Liquid Fund": "A highly liquid mutual fund focused on capital protection. It helps you manage short-term cash needs without depending on costly borrowing.",
        "Post Office Monthly Income Scheme (POMIS)": "POMIS pays monthly interest on your deposit. It benefits you by creating a stable secondary income stream, helpful during quiet work periods.",
        "SBI Gold Exchange Traded Scheme (Gold ETF)": "This ETF allows you to invest in gold digitally. It benefits you by protecting your savings from inflation and offering easy liquidity without storing physical gold.",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update products even if they already have details',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        updated_count = 0
        not_found = []
        skipped = []

        self.stdout.write(self.style.NOTICE("Starting product details population..."))

        for product_name, details_text in self.PRODUCT_DETAILS_MAPPING.items():
            # Try to find product by exact name match
            products = Product.objects.filter(name__iexact=product_name)
            
            if not products.exists():
                # Try partial match (in case name has extra spaces or slight variations)
                products = Product.objects.filter(name__icontains=product_name.split('(')[0].strip())
            
            if products.exists():
                for product in products:
                    # Skip if details already exist and --force not used
                    if product.details and not force:
                        skipped.append(f"{product.name} (ID: {product.id})")
                        continue
                    
                    if not dry_run:
                        product.details = details_text
                        product.save(update_fields=['details'])
                    
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Updated: {product.name} (ID: {product.id})"
                        )
                    )
            else:
                not_found.append(product_name)

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✓ Updated: {updated_count} products"))
        
        if skipped:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ Skipped (already have details, use --force to update): {len(skipped)}"
                )
            )
            if not dry_run:
                for item in skipped[:5]:  # Show first 5
                    self.stdout.write(f"  - {item}")
                if len(skipped) > 5:
                    self.stdout.write(f"  ... and {len(skipped) - 5} more")
        
        if not_found:
            self.stdout.write(
                self.style.ERROR(f"✗ Not found in database: {len(not_found)}")
            )
            for name in not_found[:10]:  # Show first 10
                self.stdout.write(f"  - {name}")
            if len(not_found) > 10:
                self.stdout.write(f"  ... and {len(not_found) - 10} more")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n⚠ DRY RUN MODE - No changes were made")
            )
        
        self.stdout.write("=" * 60)

