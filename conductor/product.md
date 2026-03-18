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
- Collapse results to best (cheapest) price per vehicle category for clean comparison
- Compare current best price against a configured holding price for a specific vehicle type
- Countdown to pick-up date shown in each booking's email banner ("X days" or "Today is your booking day!")
- Expired bookings automatically removed from config after pick-up date passes; monitoring pauses with a one-time notification when no bookings remain

## Delivery
- Runs on a twice-weekly schedule
- Sends an HTML-formatted email with results

## Data Per Vehicle
- Vehicle name / category (e.g. Economy, SUV, Minivan)
- Total price for the rental period
- Price per day
- Price change vs. prior run (per category)

## Configuration
- Search parameters stored in a config file (JSON or YAML)
- Config includes: location, dates, times, email settings, schedule
- Optional holding price pair: holding_price + holding_vehicle_type for savings tracking
- Config can be updated remotely via iMessage — send a natural-language message
  (e.g. "update holding price to 375") to update holding fields; changes are
  auto-committed and pushed so the next cron run picks them up automatically
