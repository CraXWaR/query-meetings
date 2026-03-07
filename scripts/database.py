import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import docx
import re

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_date_from_filename(filename):
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
        return datetime(datetime.now().year, month, day).date()
    return datetime.now().date()


def ingest_meeting(data_folder):
    for folder in os.listdir(data_folder):
        folder_path = os.path.join(data_folder, folder)
        if not os.path.isdir(folder_path):
            continue
        for file in os.listdir(folder_path):
            if not file.endswith(".docx"):
                continue
            title = os.path.splitext(file)[0]
            existing = supabase.table("meetings").select("id").eq("title", title).execute()
            if existing.data:
                print(f"Skipping (already exists): {title}")
                continue
            transcript = read_docx(os.path.join(folder_path, file))
            supabase.table("meetings").insert({
                "id": str(uuid.uuid4()),
                "title": title,
                "meeting_date": str(extract_date_from_filename(file)),
                "source": folder,
                "raw_transcript": transcript
            }).execute()
            print("Inserted:", title)


def load_transcript(meeting_id):
    response = supabase.table("meetings").select("raw_transcript").eq("id", meeting_id).execute()
    if not response.data:
        raise ValueError(f"Meeting with id {meeting_id} not found.")
    return response.data[0]["raw_transcript"]


def insert_notes(meeting_id, notes):
    supabase.table("notes").insert({
        "id": str(uuid.uuid4()),
        "meeting_id": meeting_id,
        "summary": notes["summary"],
        "action_items": notes["action_items"],
        "decisions": notes["decisions"],
        "key_takeaways": notes["key_takeaways"],
        "topics": notes["topics"],
        "next_steps": notes["next_steps"],
    }).execute()
    print(f"Notes inserted for meeting: {meeting_id}")


def get_meetings():
    response = supabase.table("meetings").select("id, title, meeting_date").execute()
    if not response.data:
        print("No meetings found in the database.")
        return
    for meeting in response.data:
        print(f"ID: {meeting['id']} | Title: {meeting['title']} | Date: {meeting['meeting_date']}")


def get_meetings_without_notes():
    meetings = supabase.table("meetings").select("id").execute()
    existing_notes = supabase.table("notes").select("meeting_id").execute()
    existing_ids = {n["meeting_id"] for n in existing_notes.data}
    return [m for m in meetings.data if m["id"] not in existing_ids]


if __name__ == "__main__":
    data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
    ingest_meeting(data_folder)
