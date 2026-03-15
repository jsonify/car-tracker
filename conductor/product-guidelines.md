# Product Guidelines: Costco Travel Car Tracker

## Email Style
- Minimal tone — data only, no framing or conversational text
- Show search parameters (location, dates, times) at the top of the email
- Results presented as an HTML table in the order they appear on the site

## Error & Empty State Handling
- Always send an email if the scrape fails or returns no results
- Email should clearly state the issue (e.g. "Scrape failed", "No results found")

## Data Presentation
- Preserve original result ordering from the scraped page
- No sorting, deduplication, or filtering applied

## Persistence
- Each run's results saved to a local SQLite database
- Enables historical comparison and trend tracking
