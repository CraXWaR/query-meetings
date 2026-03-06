# Meeting Ingestion Task

## Setup

1. Install dependencies

pip install -r requirements.txt

2. Create `.env` file

SUPABASE_URL=your_project_url
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
