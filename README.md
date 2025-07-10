# Moodle API Client for Concordia University

This project provides a Python client for interacting with Concordia University's Moodle web services API.

## Overview

The client allows you to:
- Authenticate with your Moodle credentials
- Retrieve course information
- Access course content
- Get calendar events
- And more...

## Requirements

- Python 3.6+
- Required packages (see requirements.txt)
- Moodle API token (see setup instructions)

## Setup Instructions

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Obtain your Moodle API token:
   - Log in to your Concordia Moodle account
   - Navigate to your profile settings
   - Look for "Security keys" or "Web services" section
   - Generate a token for external services (if not available, contact your Moodle administrator)

3. Configure your credentials in the `config.py` file (see example in config_example.py)

## Usage

See examples in the `examples` directory for common use cases.
