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
SERVICE_ACCOUNT_FILE = "/Users/satyendra/otp_twilio_backend/graphic-mason-479110-d6-a120ba88825f.json"

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

    # Load data into DataFrame
    data = sheet7.get("A1:K30")    # only read till column K, row 30
    df = pd.DataFrame(data)
    df.columns = df.iloc[0] 
    df = df[1:]
    df = df.reset_index(drop=True)

    print(f"Loaded {len(df)} rows from Google Sheet")

    # ============================================================
    # 2. Select + Rename Columns
    # ============================================================

    COLUMN_MAP = {
        'UFHS Tag':'ufhs_tag',
        'Official URL': 'official_url'
    }

    df2 = df.rename(columns=COLUMN_MAP)

    # Reorder to required schema
    df2 = df2[['ufhs_tag', 'official_url']]

    print("Columns normalized:", list(df2.columns))

    # ============================================================
    # 3. Database (PostgreSQL) Setup
    # ============================================================
    try:
        conn = psycopg2.connect(
            dbname='otp_service',
            user='postgres',
            password='',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()

        # UPSERT query
        UPSERT_SQL = """
        UPDATE finance_product
            SET
                ufhs_tag = %s
            WHERE official_url = %s;
        """

        # ============================================================
        # 4. Insert/Update Loop
        # ============================================================

        for idx, row in df2.iterrows():
            cursor.execute(UPSERT_SQL, (
                row['ufhs_tag'],
                row['official_url']
            ))

        conn.commit()
        cursor.close()
        conn.close()

        print("Import complete.")
        return Response(
                {"message": "Finance schemes populated successfully"},
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
