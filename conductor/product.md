# Initial Concept

Scrape https://www.costcotravel.com/rental-cars when given a pick-up location, pick-up date, pick-up time, drop-off date, and drop-off time. Return a list of all vehicles and their current prices based on the search criteria.

# Product Guide: Costco Travel Car Tracker

## Vision
A scheduled scraping tool that monitors Costco Travel rental car prices
and delivers results via email on a twice-weekly basis.

## Target User
Personal use — single user running automated price checks.

## Core Functionality
- Scrape https://www.costcotravel.com/rental-cars with configurable search parameters
- Search inputs: pick-up location, pick-up date/time, drop-off date/time
- Extract all available vehicles and their pricing

## Delivery
- Runs on a twice-weekly schedule
- Sends an HTML-formatted email with results

## Data Per Vehicle
- Vehicle name / category (e.g. Economy, SUV, Minivan)
- Total price for the rental period
- Price per day

## Configuration
- Search parameters stored in a config file (JSON or YAML)
- Config includes: location, dates, times, email settings, schedule
