# Meeting Ingestion Task

## Setup

1. Install dependencies

pip install -r requirements.txt

2. Rename `.env.example` file to `.env`

SUPABASE_URL=your_project_url <br />
SUPABASE_KEY=your_project_key

## Data

Meeting transcripts are stored in the `data/` folder as `.docx` files.

Example file name:

AI TEAM MEETING - May 22 (12 mins).docx

The script extracts:

* meeting title
* meeting date (from file name)
* transcript text

## Run ingestion

python ingest_meetings.py

This script reads all `.docx` files and inserts them into the `meetings` table in Supabase.

## Query meetings

python query_meetings.py

This prints the meeting id, title and date from the database.

## Database Schema

### meetings

- id (uuid, primary key)
- title (text, required)
- meeting_date (date, required)
- source (text, required)
- raw_transcript (text, required)
- created_at (timestamp, default now)

### notes

- id (uuid, primary key)
- meeting_id (uuid, fk → meetings.id)
- summary (text)
- action_items (jsonb)
- key_takeaways (jsonb)
- topics (jsonb)
- next_steps (jsonb)
- created_at (timestamp, default now)