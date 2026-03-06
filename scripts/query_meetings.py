import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_meetings():
    response = supabase.table("meetings").select("id, title, meeting_date").execute()
    meetings = response.data

    if len(meetings) == 0:
        print("No meetings found in the database.")
        return

    for meeting in meetings:
        print(
            f"ID: {meeting['id']} | "
            f"Title: {meeting['title']} | "
            f"Date: {meeting['meeting_date']}"
        )


if __name__ == "__main__":
    get_meetings()