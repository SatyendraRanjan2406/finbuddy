import datetime
import os
import pandas as pd
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from rest_framework.response import Response

# ============================================================
# 1. Google Sheets Setup
# ============================================================

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Path to Google service account JSON
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = '111Wiq4RuQJTJfkY_PdCvr5GBest-3BxpaT8YCFeZ39w'

def populate(request):
    # Authenticate
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE,
        SCOPES
    )
    gc = gspread.authorize(creds)
    # Open sheet
    sheet = gc.open_by_key(SPREADSHEET_ID)
    sheet7 = sheet.get_worksheet(7)   # 7th sheet

    worksheet = sheet7

    # Load data into DataFrame - read more columns for full product data
    data = sheet7.get("A1:K30")    # Read more rows and columns for complete data
    df = pd.DataFrame(data)
    df.columns = df.iloc[0] 
    df = df[1:]
    df = df.reset_index(drop=True)
    
    # Remove empty rows
    df = df.dropna(how='all')

    print(f"Loaded {len(df)} rows from Google Sheet")
    print("Available columns in spreadsheet:", list(df.columns))

    # ============================================================
    # 2. Map Spreadsheet Columns to Database Fields
    # ============================================================															
    # Column mapping from spreadsheet to database fields
    # Try multiple possible column name variations
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

    print("Columns normalized:", list(df2.columns))
    print(f"Processing {len(df2)} products")
    
    # Show sample of first row for debugging
    if len(df2) > 0:
        print("Sample first row data:")
        for col in df2.columns:
            print(f"  {col}: {df2.iloc[0].get(col, 'N/A')}")

    # ============================================================
    # 3. Database (PostgreSQL) Setup
    # ============================================================
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()

        # Test connection and table access
        try:
            cursor.execute("SELECT 1 FROM finance_product LIMIT 1;")
        except Exception as test_error:
            return Response(
                {"error": f"Database connection or table access issue: {str(test_error)}"},
                status=500
            )

        # UPSERT approach: Check if exists, then update or insert
        # Using official_url as the identifier (may not be unique, so we check first)
        CHECK_EXISTS_SQL = """
        SELECT id FROM finance_product WHERE official_url = %s LIMIT 1;
        """
        
        UPDATE_SQL = """
        UPDATE finance_product
        SET
            category = %s,
            name = %s,
            scheme_description = %s,
            purpose = %s,
            behavioral_purpose_tag = %s,
            minimum_investment = %s,
            eligibility = %s,
            integration_type = %s,
            digital_verification_availability = %s,
            ufhs_tag = %s,
            updated_at = NOW()
        WHERE official_url = %s;
        """
        
        INSERT_SQL = """
        INSERT INTO finance_product (
            category, name, scheme_description, purpose, 
            behavioral_purpose_tag, minimum_investment, eligibility,
            integration_type, digital_verification_availability, 
            official_url, ufhs_tag,created_at,updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # ============================================================
        # 4. Insert/Update Loop
        # ============================================================
        inserted_count = 0
        updated_count = 0
        error_count = 0

        for idx, row in df2.iterrows():
            # Use savepoint for each row to handle errors gracefully
            # Use a simple numeric savepoint name to avoid issues
            savepoint_name = f"sp_{int(idx)}"
            try:
                # Create savepoint - wrap in try/except in case transaction is aborted
                try:
                    cursor.execute(f"SAVEPOINT {savepoint_name}")
                except Exception as sp_error:
                    # If savepoint fails, transaction might be aborted - rollback and continue
                    print(f"Row {idx + 2}: Transaction error, rolling back - {str(sp_error)}")
                    conn.rollback()
                    error_count += 1
                    continue
                
                # Get values, handling missing columns
                official_url = str(row.get('official_url', '')).strip()
                
                # Required fields - validate they're not empty
                behavioral_purpose_tag = str(row.get('behavioral_purpose_tag', '')).strip()
                minimum_investment = str(row.get('minimum_investment', '')).strip()
                eligibility = str(row.get('eligibility', '')).strip()
                integration_type = str(row.get('integration_type', '')).strip()
                digital_verification_availability = str(row.get('digital_verification_availability', '')).strip()
                now = datetime.datetime.now()
                created_at = now.strftime("%Y-%m-%d %H:%M:%S")
                updated_at = now.strftime("%Y-%m-%d %H:%M:%S")
               
                # Prepare values with defaults for optional fields
                values = (
                    str(row.get('category', '')).strip() or None,
                    str(row.get('name', '')).strip() or None,
                    str(row.get('scheme_description', '')).strip() or None,
                    str(row.get('purpose', '')).strip() or None,
                    behavioral_purpose_tag,
                    minimum_investment,
                    eligibility,
                    integration_type,
                    digital_verification_availability,
                    official_url,
                    int(row.get('ufhs_tag', 0)) if row.get('ufhs_tag') and str(row.get('ufhs_tag')).strip().isdigit() else None,
                    created_at,
                    updated_at
                )
                
                # Check if product exists
                try:
                    # Ensure cursor is ready
                    if cursor.closed:
                        cursor = conn.cursor()
                    
                    cursor.execute(CHECK_EXISTS_SQL, (official_url,))
                    exists = cursor.fetchone()
                except psycopg2.InterfaceError as interface_error:
                    # Cursor might be closed, recreate it
                    print(f"Row {idx + 2}: Cursor error, recreating - {str(interface_error)}")
                    cursor.close()
                    cursor = conn.cursor()
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    error_count += 1
                    continue
                except psycopg2.ProgrammingError as prog_error:
                    # SQL syntax or table error
                    print(f"Row {idx + 2}: SQL error checking product - {str(prog_error)}")
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    error_count += 1
                    continue
                except Exception as check_error:
                    print(f"Row {idx + 2}: Error checking if product exists - {str(check_error)}")
                    # Rollback to savepoint and skip this row
                    try:
                        cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    except:
                        conn.rollback()
                    error_count += 1
                    continue
                
                try:
                    if exists:
                        # Update existing product
                        cursor.execute(UPDATE_SQL, values + (official_url,))
                        updated_count += 1
                    else:
                        # Insert new product
                        cursor.execute(INSERT_SQL, values)
                        inserted_count += 1
                    
                    # Release savepoint on success
                    cursor.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                except Exception as exec_error:
                    print(f"Row {idx + 2}: Error executing insert/update - {str(exec_error)}")
                    # Rollback to savepoint
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    error_count += 1
                    continue
                    
            except Exception as e:
                print(f"Row {idx + 2}: Error processing - {str(e)}")
                error_count += 1
                # Rollback to savepoint to continue with next row
                try:
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                except Exception as rollback_error:
                    # If rollback to savepoint fails, try full rollback
                    print(f"Row {idx + 2}: Savepoint rollback failed, doing full rollback - {str(rollback_error)}")
                    try:
                        conn.rollback()
                    except:
                        pass
                continue

        conn.commit()
        cursor.close()
        conn.close()

        result_message = (
            f"Import complete. "
            f"Inserted: {inserted_count}, "
            f"Updated: {updated_count}, "
            f"Errors: {error_count}"
        )
        print(result_message)
        
        return Response(
            {
                "message": "Finance schemes populated successfully",
                "inserted": inserted_count,
                "updated": updated_count,
                "errors": error_count,
                "total_processed": len(df2)
            },
                status=200
            )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# def populate(request):
#     # Authenticate
#     creds = ServiceAccountCredentials.from_json_keyfile_name(
#         SERVICE_ACCOUNT_FILE,
#         SCOPES
#     )
#     gc = gspread.authorize(creds)
#     # Open sheet
#     sheet = gc.open_by_key(SPREADSHEET_ID)
#     sheet7 = sheet.get_worksheet(7)   # 7th sheet

#     worksheet = sheet7

#     # Load data into DataFrame
#     data = sheet7.get("A1:K30")    # only read till column K, row 30
#     df = pd.DataFrame(data)
#     df.columns = df.iloc[0] 
#     df = df[1:]
#     df = df.reset_index(drop=True)

#     print(f"Loaded {len(df)} rows from Google Sheet")

#     # ============================================================
#     # 2. Select + Rename Columns
#     # ============================================================

#     COLUMN_MAP = {
#         'Category': 'category',
#         'Product Name / Instrument': 'name',
#         'Scheme Description': 'scheme_description',
#         'Purpose': 'purpose',
#         'Official URL': 'official_url'
#     }

#     df2 = df.rename(columns=COLUMN_MAP)

#     # Reorder to required schema
#     df2 = df2[['category', 'name', 'scheme_description', 'purpose', 'official_url']]

#     print("Columns normalized:", list(df2.columns))

#     # ============================================================
#     # 3. Database (PostgreSQL) Setup
#     # ============================================================

#     conn = psycopg2.connect(
#         dbname='otp_service',
#         user='postgres',
#         password='',
#         host='localhost',
#         port='5432'
#     )
#     cursor = conn.cursor()

#     # UPSERT query
#     UPSERT_SQL = """
#     UPDATE finance_product
#         SET
#             category = %s,
#             name = %s,
#             scheme_description = %s,
#             purpose = %s
#         WHERE official_url = %s;
#     """

#     # ============================================================
#     # 4. Insert/Update Loop
#     # ============================================================

#     for idx, row in df2.iterrows():
#         cursor.execute(UPSERT_SQL, (
#             row['category'],
#             row['name'],
#             row['scheme_description'],
#             row['purpose'],
#             row['official_url']
#         ))

#     conn.commit()
#     cursor.close()
#     conn.close()

#     print("Import complete.")
