"""
Django management command to seed financial products into the database.
Usage: python manage.py seed_products
"""
from django.core.management.base import BaseCommand
from finance.models import Product


class Command(BaseCommand):
    help = 'Seed financial products into the database'

    def handle(self, *args, **options):
        products_data = [
            {
                "behavioral_purpose_tag": "Build Emergency Corpus",
                "minimum_investment": "₹0",
                "eligibility": "Pradhan Mantri Jan-Dhan Yojana (PMJDY). A zero-balance savings account offering basic banking, insurance, and overdraft access for every citizen. Eligibility: Any Indian citizen (≥10 years) without existing bank account",
                "integration_type": "APISetu / Account Aggregator (AA)",
                "digital_verification_availability": "Verified API available",
                "official_url": "https://pmjdy.gov.in",
                "ufhs_tag": 300,
            },
            {
                "behavioral_purpose_tag": "Long-term Asset Creation",
                "minimum_investment": "₹500/year",
                "eligibility": "Public Provident Fund (PPF). A long-term government-backed small savings scheme with tax benefits and safe fixed returns. Eligibility: Resident Indian (15-year lock-in)",
                "integration_type": "DigiLocker (NSI issuer) / Bank FIP via AA",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://nsiindia.gov.in",
                "ufhs_tag": 500,
            },
            {
                "behavioral_purpose_tag": "Long-term Asset Creation",
                "minimum_investment": "₹1",
                "eligibility": "National Savings Certificate (NSC). A fixed-income savings bond encouraging small to medium-term savings with assured returns. Eligibility: Resident Indian (no age limit)",
                "integration_type": "DigiLocker (India Post)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://www.indiapost.gov.in",
                "ufhs_tag": 300,
            },
            {
                "behavioral_purpose_tag": "Long-term Asset Creation",
                "minimum_investment": "₹1",
                "eligibility": "Kisan Vikas Patra (KVP). A small savings certificate that doubles the deposited amount in about 9–10 years with guaranteed return. Eligibility: Resident Indian (single/joint)",
                "integration_type": "DigiLocker (India Post)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://nsiindia.gov.in",
                "ufhs_tag": 300,
            },
            {
                "behavioral_purpose_tag": "Build Emergency Corpus",
                "minimum_investment": "₹100/month",
                "eligibility": "Post Office Recurring Deposit (RD). A small monthly savings plan offering steady growth and liquidity through India Post. Eligibility: Resident Indian, individual/joint",
                "integration_type": "DigiLocker (India Post)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://www.indiapost.gov.in",
                "ufhs_tag": 500,
            },
            {
                "behavioral_purpose_tag": "Build Family Corpus",
                "minimum_investment": "₹250/year",
                "eligibility": "Sukanya Samriddhi Yojana (SSY). A high-interest savings scheme for parents to build a fund for their girl child's education or marriage. Eligibility: Girl child <10 years; parent/guardian account",
                "integration_type": "DigiLocker (NSI issuer)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://nsiindia.gov.in",
                "ufhs_tag": 500,
            },
            {
                "behavioral_purpose_tag": "Manage Income Volatility",
                "minimum_investment": "₹10,000+",
                "eligibility": "Pradhan Mantri Mudra Yojana (PMMY). Offers collateral-free loans up to ₹10 lakh to small entrepreneurs and self-employed workers. Eligibility: Non-corporate, non-farm micro-entrepreneurs",
                "integration_type": "APISetu / AA Loan Account",
                "digital_verification_availability": "API & AA verified",
                "official_url": "https://mudra.org.in",
                "ufhs_tag": 300,
            },
            {
                "behavioral_purpose_tag": "Manage Income Volatility",
                "minimum_investment": "₹10,000 (first tranche)",
                "eligibility": "PM SVANidhi. Provides affordable working capital loans to street vendors and small urban micro-entrepreneurs. Eligibility: Urban street vendors with municipal CoV",
                "integration_type": "APISetu / MyScheme API",
                "digital_verification_availability": "API verified",
                "official_url": "https://pmsvanidhi.mohua.gov.in",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Income Volatility / Growth Funding",
                "minimum_investment": "₹1 lakh project (min 5% margin)",
                "eligibility": "Prime Minister's Employment Generation Programme (PMEGP). A credit-linked subsidy scheme promoting micro-enterprises and self-employment. Eligibility: 18+, min 8th pass, unemployed youth",
                "integration_type": "APISetu (KVIC)",
                "digital_verification_availability": "API verified",
                "official_url": "https://kviconline.gov.in/pmegp",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events",
                "minimum_investment": "₹12/year",
                "eligibility": "Pradhan Mantri Suraksha Bima Yojana (PMSBY). A low-cost accidental insurance scheme providing coverage for death or disability. Eligibility: Age 18–70, linked bank account",
                "integration_type": "APISetu / DigiLocker (Certificate)",
                "digital_verification_availability": "API & DigiLocker verified",
                "official_url": "https://financialservices.gov.in/pmsby",
                "ufhs_tag": 300,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events",
                "minimum_investment": "₹330/year",
                "eligibility": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY). An affordable term life insurance policy for individuals with active bank accounts. Eligibility: Age 18–50, bank account holder",
                "integration_type": "DigiLocker (Certificate) / AA (Insurance FI Type)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://financialservices.gov.in/pmjjby",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events (Health)",
                "minimum_investment": "Free (Govt funded)",
                "eligibility": "Ayushman Bharat – PM-JAY. Provides up to ₹5 lakh per family annually for secondary and tertiary healthcare to low-income households. Eligibility: Low-income families verified via SECC",
                "integration_type": "APISetu (NHA) / ABHA ID",
                "digital_verification_availability": "API verified",
                "official_url": "https://pmjay.gov.in",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Event",
                "minimum_investment": "₹200/year",
                "eligibility": "Aam Aadmi Bima Yojana (AABY). Offers life and accident insurance coverage to low-income and informal sector workers. Eligibility: Landless household / informal worker",
                "integration_type": "DigiLocker (Certificate)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://myscheme.gov.in/schemes/aaby",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events / Retirement Buffer",
                "minimum_investment": "₹55–₹200/month",
                "eligibility": "Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM). A voluntary contributory pension plan for unorganised workers earning below ₹15,000. Eligibility: Unorganised worker (16–40 yrs) income < ₹15,000",
                "integration_type": "APISetu (PFRDA / Maandhan) / DigiLocker",
                "digital_verification_availability": "API verified",
                "official_url": "https://maandhan.in",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events / Long-term Security",
                "minimum_investment": "₹42–₹210/month",
                "eligibility": "Atal Pension Yojana (APY). A government-backed guaranteed pension scheme for workers in the informal sector. Eligibility: Age 18–40",
                "integration_type": "DigiLocker (PFRDA) / AA (Pension FIP)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://npscra.nsdl.co.in",
                "ufhs_tag": 500,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events / Income Continuity",
                "minimum_investment": "N/A",
                "eligibility": "National Social Assistance Programme (NSAP). Provides monthly financial assistance to elderly, widows, and persons with disabilities. Eligibility: BPL households 60+",
                "integration_type": "APISetu (NSAP) / PFMS",
                "digital_verification_availability": "API verified",
                "official_url": "https://nsap.nic.in",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events / Income Continuity",
                "minimum_investment": "₹500/year",
                "eligibility": "National Pension System (NPS). A market-linked retirement savings scheme offering flexible contributions and tax benefits. Eligibility: Indian citizen 18–70",
                "integration_type": "DigiLocker (PFRDA) / AA (Pension)",
                "digital_verification_availability": "DigiLocker verified",
                "official_url": "https://npscra.nsdl.co.in",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Manage Risk Events / Retirement Buffer",
                "minimum_investment": "₹55–₹200/month",
                "eligibility": "National Pension Scheme for Traders and Self-Employed Persons (NPS-Traders). A voluntary pension plan for small traders and self-employed individuals aged 18–40. Eligibility: Shopkeepers / self-employed aged 18–40",
                "integration_type": "APISetu (PFRDA / Maandhan) / DigiLocker",
                "digital_verification_availability": "API verified",
                "official_url": "https://labour.gov.in/eshram",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Build Emergency Corpus (food security)",
                "minimum_investment": "Free / subsidised",
                "eligibility": "Public Distribution System (PDS / ONORC). Provides subsidised food grains to eligible BPL and migrant households across India. Eligibility: BPL families & migrants with Ration Card",
                "integration_type": "APISetu (PDS / State Civil Supplies)",
                "digital_verification_availability": "State API available",
                "official_url": "https://nfsa.gov.in",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Long-term Asset Creation",
                "minimum_investment": "Grant-based (₹1.2–₹1.5 lakh)",
                "eligibility": "Pradhan Mantri Awas Yojana – Gramin (PMAY-G). Supports rural households in constructing safe, pucca houses with government assistance. Eligibility: Rural poor households without pucca house",
                "integration_type": "APISetu (MoRD) / PFMS",
                "digital_verification_availability": "API verified",
                "official_url": "https://pmayg.nic.in",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Build Emergency Corpus",
                "minimum_investment": "₹100",
                "eligibility": "Aditya Birla Sun Life Liquid Fund. A low-risk liquid mutual fund designed for short-term parking of money with high liquidity and stable returns. Ideal for gig workers looking for a safe, instantly redeemable alternative to savings accounts for emergency buffers. Eligibility: Any Indian adult with valid KYC and PAN",
                "integration_type": "AMFI / CAMS / KFintech APIs (future) or AA (Investment FI Type when available)",
                "digital_verification_availability": "Self-declared",
                "official_url": "https://mutualfund.adityabirlacapital.com/",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Build Emergency Corpus",
                "minimum_investment": "₹100",
                "eligibility": "Edelweiss Liquid Fund. An ultra-short duration fund investing in money-market instruments with low volatility and easy redemption. Suitable for gig workers and freelancers who want slightly better returns than savings account while remaining highly liquid. Eligibility: Any Indian resident individual with KYC",
                "integration_type": "AMFI / CAMS / KFintech APIs (future) or AA (Investment FI Type when available)",
                "digital_verification_availability": "Self-declared",
                "official_url": "https://www.edelweissmf.com/mutual-funds/liquid-fund",
                "ufhs_tag": None,
            },
            {
                "behavioral_purpose_tag": "Long-term Asset Creation",
                "minimum_investment": "₹1,000 minimum",
                "eligibility": "Post Office Monthly Income Scheme (POMIS). Government-backed scheme offering predictable monthly interest payout ideal for steady supplemental income. Great for gig workers wanting predictable monthly income from savings with very low risk and government guarantee. Eligibility: Any Indian resident individual; minors allowed through guardian",
                "integration_type": "DigiLocker (India Post) / APISetu (Small Savings)",
                "digital_verification_availability": "DigiLocker Verified",
                "official_url": "https://www.indiapost.gov.in",
                "ufhs_tag": None,
            },
        ]

        created_count = 0
        updated_count = 0

        for product_data in products_data:
            # Use combination of behavioral_purpose_tag, official_url, and minimum_investment
            # as unique identifier since multiple products can share the same URL and tag
            product, created = Product.objects.update_or_create(
                behavioral_purpose_tag=product_data["behavioral_purpose_tag"],
                official_url=product_data["official_url"],
                minimum_investment=product_data["minimum_investment"],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {product.behavioral_purpose_tag}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {product.behavioral_purpose_tag}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully processed {len(products_data)} products: '
                f'{created_count} created, {updated_count} updated'
            )
        )

