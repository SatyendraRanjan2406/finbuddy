"""
Django management command to populate products from Google Sheets.
Usage: python manage.py populate_products
"""
import datetime
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.core.management.base import BaseCommand
from django.db import transaction
from finance.models import Product


class Command(BaseCommand):
    help = 'Populate products from Google Sheets into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sheet-index',
            type=int,
            default=7,
            help='Index of the worksheet to read (default: 7)',
        )
        parser.add_argument(
            '--range',
            type=str,
            default='A1:K30',
            help='Range to read from spreadsheet (default: A1:K30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be inserted/updated without making changes',
        )

    def handle(self, *args, **options):
        sheet_index = options.get('sheet_index', 7)
        range_str = options.get('range', 'A1:K30')
        dry_run = options.get('dry_run', False)

        # Google Sheets Setup
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
        SPREADSHEET_ID = '111Wiq4RuQJTJfkY_PdCvr5GBest-3BxpaT8YCFeZ39w'

        if not SERVICE_ACCOUNT_FILE:
            self.stdout.write(
                self.style.ERROR('SERVICE_ACCOUNT_FILE environment variable not set')
            )
            return

        try:
            # Authenticate
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                SERVICE_ACCOUNT_FILE,
                SCOPES
            )
            gc = gspread.authorize(creds)
            
            # Open sheet
            sheet = gc.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.get_worksheet(sheet_index)

            # Load data into DataFrame
            data = worksheet.get(range_str)
            df = pd.DataFrame(data)
            df.columns = df.iloc[0]
            df = df[1:]
            df = df.reset_index(drop=True)
            
            # Remove empty rows
            df = df.dropna(how='all')

            self.stdout.write(f"Loaded {len(df)} rows from Google Sheet")
            self.stdout.write(f"Available columns: {list(df.columns)}")

            # Column mapping from spreadsheet to database fields
            COLUMN_MAP = {
                'Category': 'category',
                'Product Name / Instrument': 'name',
                'Scheme Description': 'scheme_description',
                'Purpose': 'purpose',
                'Behavioral Purpose Tag': 'behavioral_purpose_tag',
                'Minimum Investment / Contribution': 'minimum_investment',
                'Eligibility': 'eligibility',
                'Integration Type (for FinBuddy)': 'integration_type',
                'Digital Verification Availability': 'digital_verification_availability',
                'Official URL': 'official_url',
                'UFHS Tag': 'ufhs_tag',
            }
            
            # Rename columns that exist in the dataframe (case-insensitive matching)
            df_columns_upper = {col.upper(): col for col in df.columns}
            available_columns = {}
            for map_key, map_value in COLUMN_MAP.items():
                if map_key in df.columns:
                    available_columns[map_key] = map_value
                elif map_key.upper() in df_columns_upper:
                    available_columns[df_columns_upper[map_key.upper()]] = map_value
            
            df2 = df.rename(columns=available_columns)
            
            # Select only the columns we need (that exist in the dataframe)
            required_columns = [col for col in COLUMN_MAP.values() if col in df2.columns]
            df2 = df2[required_columns]
            
            # Fill missing values with empty strings
            df2 = df2.fillna('')

            self.stdout.write(f"Columns normalized: {list(df2.columns)}")
            self.stdout.write(f"Processing {len(df2)} products")

            # Process products
            inserted_count = 0
            updated_count = 0
            error_count = 0
            skipped_count = 0

            for idx, row in df2.iterrows():
                try:
                    # Get values, handling missing columns
                    official_url = str(row.get('official_url', '')).strip()
                    
                    # Required fields - validate they're not empty
                    behavioral_purpose_tag = str(row.get('behavioral_purpose_tag', '')).strip()
                    minimum_investment = str(row.get('minimum_investment', '')).strip()
                    eligibility = str(row.get('eligibility', '')).strip()
                    integration_type = str(row.get('integration_type', '')).strip()
                    digital_verification_availability = str(row.get('digital_verification_availability', '')).strip()
                    
                    # Validate required fields
                    if not official_url:
                        self.stdout.write(
                            self.style.WARNING(f"Row {idx + 2}: Skipping - no official_url")
                        )
                        skipped_count += 1
                        continue
                    
                    if not behavioral_purpose_tag:
                        self.stdout.write(
                            self.style.WARNING(f"Row {idx + 2}: Skipping - no behavioral_purpose_tag")
                        )
                        skipped_count += 1
                        continue
                    
                    if not minimum_investment:
                        self.stdout.write(
                            self.style.WARNING(f"Row {idx + 2}: Skipping - no minimum_investment")
                        )
                        skipped_count += 1
                        continue
                    
                    if not eligibility:
                        self.stdout.write(
                            self.style.WARNING(f"Row {idx + 2}: Skipping - no eligibility")
                        )
                        skipped_count += 1
                        continue
                    
                    if not integration_type:
                        self.stdout.write(
                            self.style.WARNING(f"Row {idx + 2}: Skipping - no integration_type")
                        )
                        skipped_count += 1
                        continue
                    
                    if not digital_verification_availability:
                        self.stdout.write(
                            self.style.WARNING(f"Row {idx + 2}: Skipping - no digital_verification_availability")
                        )
                        skipped_count += 1
                        continue
                    
                    # Prepare ufhs_tag
                    ufhs_tag = None
                    ufhs_tag_val = row.get('ufhs_tag', '')
                    if ufhs_tag_val and str(ufhs_tag_val).strip().isdigit():
                        ufhs_tag = int(ufhs_tag_val)
                    
                    # Check if product exists
                    product = Product.objects.filter(official_url=official_url).first()
                    
                    if product:
                        # Update existing product
                        if not dry_run:
                            product.category = str(row.get('category', '')).strip() or None
                            product.name = str(row.get('name', '')).strip() or None
                            product.scheme_description = str(row.get('scheme_description', '')).strip() or None
                            product.purpose = str(row.get('purpose', '')).strip() or None
                            product.behavioral_purpose_tag = behavioral_purpose_tag
                            product.minimum_investment = minimum_investment
                            product.eligibility = eligibility
                            product.integration_type = integration_type
                            product.digital_verification_availability = digital_verification_availability
                            product.ufhs_tag = ufhs_tag
                            product.save()
                        
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Updated: {product.name or official_url} (Row {idx + 2})")
                        )
                    else:
                        # Insert new product
                        if not dry_run:
                            product = Product.objects.create(
                                category=str(row.get('category', '')).strip() or None,
                                name=str(row.get('name', '')).strip() or None,
                                scheme_description=str(row.get('scheme_description', '')).strip() or None,
                                purpose=str(row.get('purpose', '')).strip() or None,
                                behavioral_purpose_tag=behavioral_purpose_tag,
                                minimum_investment=minimum_investment,
                                eligibility=eligibility,
                                integration_type=integration_type,
                                digital_verification_availability=digital_verification_availability,
                                official_url=official_url,
                                ufhs_tag=ufhs_tag,
                            )
                        
                        inserted_count += 1
                        product_name = str(row.get('name', '')).strip() or official_url
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Inserted: {product_name} (Row {idx + 2})")
                        )
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Row {idx + 2}: Error - {str(e)}")
                    )
                    continue

            # Summary
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS(f"✓ Inserted: {inserted_count} products"))
            self.stdout.write(self.style.SUCCESS(f"✓ Updated: {updated_count} products"))
            if skipped_count > 0:
                self.stdout.write(self.style.WARNING(f"⚠ Skipped: {skipped_count} rows (missing required fields)"))
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f"✗ Errors: {error_count} rows"))
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING("\n⚠ DRY RUN MODE - No changes were made")
                )
            
            self.stdout.write("=" * 60)

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Service account file not found: {SERVICE_ACCOUNT_FILE}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )


