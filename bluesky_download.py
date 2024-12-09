import os
import json
import time
from datetime import datetime
from atproto import Client, models

def get_follows_for_user(client, username):
    """Helper function to get follows for a specific user"""
    follows = []
    cursor = None
    try:
        while True:
            params = {'actor': username, 'limit': 100}
            if cursor:
                params['cursor'] = cursor
            response = client.app.bsky.graph.get_follows(params)
            follows.extend([follow.model_dump() for follow in response.follows])
            if not response.cursor:
                break
            cursor = response.cursor
            time.sleep(0.5)  # Rate limiting
    except Exception as e:
        print(f"Error fetching follows for {username}: {str(e)}")
    return follows

def download_bluesky_network(username, password, output_dir=None):
    """
    Download social network data from Bluesky.
    
    :param username: Your Bluesky username (handle)
    :param password: Your Bluesky password
    :param output_dir: Directory to save downloaded data (defaults to ./bluesky_data)
    """
    # Create client and login
    client = Client()
    client.login(username, password)

    # Get profile information
    profile = client.app.bsky.actor.get_profile({'actor': username})
    
    # Determine output directory
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"./bluesky_data"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "following_network"), exist_ok=True)

    # Save profile information
    with open(os.path.join(output_dir, "profile.json"), "w", encoding="utf-8") as f:
        json.dump(profile.model_dump(), f, indent=2, ensure_ascii=False)

    # Download followers
    followers = []
    cursor = None
    while True:
        params = {'actor': username, 'limit': 100}
        if cursor:
            params['cursor'] = cursor
        response = client.app.bsky.graph.get_followers(params)
        followers.extend([follower.model_dump() for follower in response.followers])
        if not response.cursor:
            break
        cursor = response.cursor
    
    with open(os.path.join(output_dir, "followers.json"), "w", encoding="utf-8") as f:
        json.dump(followers, f, indent=2, ensure_ascii=False)

    # Download following
    following = []
    cursor = None
    while True:
        params = {'actor': username, 'limit': 100}
        if cursor:
            params['cursor'] = cursor
        response = client.app.bsky.graph.get_follows(params)
        following.extend([follow.model_dump() for follow in response.follows])
        if not response.cursor:
            break
        cursor = response.cursor
    
    with open(os.path.join(output_dir, "following.json"), "w", encoding="utf-8") as f:
        json.dump(following, f, indent=2, ensure_ascii=False)

    # Download following network (who your follows follow)
    print("\nDownloading following network (this may take a while)...")
    following_network = {}
    for i, follow in enumerate(following, 1):
        handle = follow['handle']
        output_file = os.path.join(output_dir, "following_network", f"{handle}.json")
        
        if os.path.exists(output_file):
            print(f"Skipping {i}/{len(following)}: {handle} (already exists)")
        else:
            print(f"Processing {i}/{len(following)}: {handle}")
            following_network[handle] = get_follows_for_user(client, handle)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(following_network[handle], f, indent=2, ensure_ascii=False)
            time.sleep(1)  # Rate limiting between users

    # Save complete following network
    with open(os.path.join(output_dir, "following_network.json"), "w", encoding="utf-8") as f:
        json.dump(following_network, f, indent=2, ensure_ascii=False)

    # Download recent posts
    posts = []
    cursor = None
    while True:
        params = {'actor': username, 'limit': 100}
        if cursor:
            params['cursor'] = cursor
        response = client.app.bsky.feed.get_author_feed(params)
        posts.extend([post.model_dump() for post in response.feed])
        if not response.cursor:
            break
        cursor = response.cursor
        if len(posts) >= 500:  # Limit to last 500 posts to avoid too much data
            break
    
    with open(os.path.join(output_dir, "posts.json"), "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    print(f"\nBluesky data downloaded to: {output_dir}")
    print(f"Files created:")
    print(f"- profile.json")
    print(f"- followers.json ({len(followers)} followers)")
    print(f"- following.json ({len(following)} following)")
    print(f"- following_network/ ({len(following)} files, one per following)")
    print(f"- following_network.json (complete network)")
    print(f"- posts.json ({len(posts)} posts)")

def main():
    print("Welcome to Bluesky Network Downloader!")
    print("\nNOTE: Your username should be in the format 'handle.bsky.social'")
    print("For example, if your handle is 'alice', enter 'alice.bsky.social'")
    print("If you have a custom domain, use that instead (e.g., 'alice.example.com')\n")
    
    username = input("Enter your Bluesky handle (e.g., username.bsky.social): ").strip()
    password = input("Enter your Bluesky App Password (create one at Settings > App Passwords): ").strip()

    download_bluesky_network(username, password)

if __name__ == "__main__":
    main()
