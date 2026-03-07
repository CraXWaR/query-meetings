# Meeting AI Summary

## Setup

1. Install dependencies

pip install -r requirements.txt

2. Rename `.env.example` file to `.env`

SUPABASE_URL=your_project_url  
SUPABASE_KEY=your_project_key  
GROQ_API_KEY=your_groq_api_key  

## Data

Meeting transcripts are stored in the `data/` folder as `.docx` files.

Example file name:

AI TEAM MEETING - May 22 (12 mins).docx

The script extracts:

* meeting title
* meeting date (from file name)
* transcript text

## Run ingestion

python database.py

This script reads all `.docx` files and inserts them into the `meetings` table in Supabase. Skips meetings that already exist.

## Generate notes

### Single meeting
python generate_notes.py --meeting_id <id>

### All meetings without notes
python generate_notes.py --all

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
- action_items (jsonb) — list of { text, owner, due_date }
- decisions (jsonb) — list of strings
- key_takeaways (jsonb) — list of strings
- topics (jsonb) — list of strings
- next_steps (jsonb) — list of { text, owner }
- created_at (timestamp, default now)

## Prompt Strategy

The LLM is instructed to return ONLY valid JSON with no explanation or markdown. The prompt includes the exact schema structure so the model knows what fields to populate.

If the transcript is too long (>20,000 chars), it is split into chunks, processed separately and merged into a single result.

## Output Validation

The JSON response is parsed and validated — if parsing fails (e.g. markdown fences around JSON), the response is cleaned and re-parsed. Missing fields are filled with default empty values instead of throwing an error.