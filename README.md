# SMTP Automation 

This is a simple interface to automate sending client emails with weekly hours attached as a CSV.

## Requirements

* The current setup reads a Google Sheet into BigQuery with the following headers
  * `Period`
  * `Date` - Day the contracting hours were completed
  * `Hours` - Float value (e.g., `1.5`)
  * `Category` - Required by one of my clients, e.g, `Application Development`
  * `Purpose` - Short summary of what was being worked on
  * `Accomplished` - Short summary of what was successfully 
* This source code queries the BigQuery table into a CSV file
* The CSV is attached to an email sent with an SMTP server of your choice

## Runtime

If you're running locally, rename `env.template` to `dev.env`, and execute `docker compose up --build`