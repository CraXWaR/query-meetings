import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import docx

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_FOLDER = "data"


def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)


def extract_date_from_filename(filename):
    import re

    match = re.search(r"([A-Za-z]+) (\d{1,2})", filename)
    if match:
        month_str, day = match.group(1), int(match.group(2))
        try:
            month = datetime.strptime(month_str, "%B").month
        except ValueError:
            try:
                month = datetime.strptime(month_str, "%b").month
            except ValueError:
                return datetime.now().date()
        year = datetime.now().year
        return datetime(year, month, day).date()
    else:
        return datetime.now().date()


def ingest_meeting():
    for folder in os.listdir(DATA_FOLDER):
        folder_path = os.path.join(DATA_FOLDER, folder)
        if not os.path.isdir(folder_path):
            continue

        for file in os.listdir(folder_path):
            if not file.endswith(".docx"):
                continue

            file_path = os.path.join(folder_path, file)
            transcript = read_docx(file_path)

            title = os.path.splitext(file)[0]
            meeting_date = extract_date_from_filename(file)

            meeting_data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "meeting_date": str(meeting_date),
                "source": folder,
                "raw_transcript": transcript
            }

            supabase.table("meetings").insert(meeting_data).execute()
            print("Inserted:", title)


if __name__ == "__main__":
    ingest_meeting()