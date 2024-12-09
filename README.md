# Bluesky Social Network Downloader

## Overview
This Python script provides a comprehensive tool to download and backup your Bluesky social network data. It offers a user-friendly way to archive your digital presence on Bluesky.

## Features
- Download complete profile information
- Retrieve full followers list
- Export following list
- Archive recent posts and interactions
- Save data in organized JSON format
- Timestamp-based backup directories
- Rate-limit compliant
- Secure authentication handling

## Prerequisites
- Python 3.8+
- Bluesky account

## Installation
1. Clone this repository to your local machine
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Required packages:
- atproto (v0.8.1)

## Usage
1. Ensure your virtual environment is activated
2. Run the script:
   ```bash
   python bluesky_download.py
   ```
3. When prompted:
   - Enter your Bluesky handle (e.g., user.bsky.social)
   - Provide your password
   - Wait while the script downloads your data
4. Find your downloaded data in the timestamped directory created in the script's location

## Data Structure
The downloaded data is organized in the `data` folder with the following structure:

### Files
- `followers.json` : List of accounts following you
- `following.json` : List of accounts you follow
- `posts.json` : Archive of your recent posts
- `profile.json` : Your profile information
- `following_network.json` : Extended network data

### Directories
- `following_network/`: Contains individual JSON files, one for each account that the user is following, with detailed information about that account's network

### Data Format Example
The following data (stored in `example_following.json`) follows this structure:
```json
{
  "did": "unique-identifier",
  "handle": "username.bsky.social",
  "associated": {
    "chat": {
      "allow_incoming": "all",
      "py_type": "app.bsky.actor.defs#profileAssociatedChat"
    }
  },
  "avatar": "profile-image-url",
  "created_at": "timestamp",
  "description": "user bio",
  "display_name": "User Display Name",
  "indexed_at": "timestamp",
  "labels": []
}
```

## Security Notes
- Your login credentials are only used for authentication and are never stored
- Consider using environment variables for credentials in automated scenarios
- The script uses official Bluesky API endpoints through the atproto library
- All data is stored locally in your specified directory

## Troubleshooting
Common issues and solutions:
- Authentication errors: Verify your handle and password
- Connection timeouts: Check your internet connection
- Rate limiting: The script handles rate limits automatically
- Package conflicts: Ensure you're using the correct atproto version (0.8.1)

## Disclaimer
This tool is designed for personal use and data backup purposes. Please:
- Respect Bluesky's terms of service
- Be mindful of API rate limits
- Do not use the downloaded data for unauthorized purposes
- Consider the privacy implications of storing social network data

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests.
