import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from django.db import transaction
from training.models import TrainingSection, TrainingQuestion, TrainingOption


# === Google Sheets Setup ===
SPREADSHEET_ID = "1gufHMamzNEWC9t1GvhqhDlBlr4LG8aNQ01sN839bGU8"
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_FILE, SCOPES
)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)


def get_sheet_df(sheet_name):
    """Read Google Sheet tab into pandas DataFrame"""
    worksheet = sh.worksheet(sheet_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} rows from '{sheet_name}'")
    return df


def run():
    print("\n=== Importing Training Content from Google Sheets ===")

    df_sections = get_sheet_df("training_sections")
    df_questions = get_sheet_df("training_questions")
    df_options = get_sheet_df("training_options")

    with transaction.atomic():
        print("\nClearing previous data...")
        TrainingOption.objects.all().delete()
        TrainingQuestion.objects.all().delete()
        TrainingSection.objects.all().delete()

        print("\nCreating Training Sections...")
        for _, row in df_sections.iterrows():
            TrainingSection.objects.create(
                id=row["id"],
                title=row["title"],
                description=row.get("description", ""),
                content_type=row["content_type"],
                language=row["language"],
                video_url=row.get("video_url"),
                audio_url=row.get("audio_url"),
                text_content=row.get("text_content"),
                score=row.get("score", 10),
                order=row.get("order", 0),
                is_active=row.get("is_active", True),
            )

        print("\nCreating Training Questions...")
        for _, row in df_questions.iterrows():
            TrainingQuestion.objects.create(
                id=row["id"],
                training_id=row["training_id"],
                question_text=row["question_text"],
                question_type=row["question_type"],
                order=row.get("order", 0),
                language=row.get("language", "en"),
            )

        print("\nCreating Training Options...")
        for _, row in df_options.iterrows():
            TrainingOption.objects.create(
                id=row["id"],
                question_id=row["question_id"],
                option_text=row["option_text"],
                is_correct=row["is_correct"],
            )

        print("\n✔ Import Completed Successfully!")


if __name__ == "__main__":
    run()
