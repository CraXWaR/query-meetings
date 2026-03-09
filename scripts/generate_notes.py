import argparse
from database import load_transcript, insert_notes, get_meetings_without_notes, supabase
from llm_service import llm_client, validate_notes


def generate_notes_by_meeting(meeting_id):
    existing = supabase.table("notes").select("id").eq("meeting_id", meeting_id).execute()
    if existing.data:
        print(f"Meeting {meeting_id} already has notes. Skipping.")
        return True

    try:
        transcript = load_transcript(meeting_id)
    except ValueError as e:
        print(f"Error: {e}")
        return False

    raw = llm_client(transcript)

    if raw is None:
        return False

    notes = validate_notes(raw)
    insert_notes(meeting_id, notes, raw)
    print("Notes generated successfully:")
    print(notes)
    return True


def generate_all_notes():
    meetings = get_meetings_without_notes()

    if not meetings:
        print("All meetings already have notes.")
        return

    for meeting in meetings:
        result = generate_notes_by_meeting(meeting["id"])
        if not result:
            print("Stopping due to rate limit.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--meeting_id", type=str, help="ID of the meeting to process")
    parser.add_argument("--all", action="store_true", help="Process all meetings without notes")
    args = parser.parse_args()

    if args.meeting_id:
        generate_notes_by_meeting(args.meeting_id)
    elif args.all:
        generate_all_notes()
    else:
        print("Please provide --meeting_id or --all")
