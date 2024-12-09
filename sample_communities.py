import os
import json
import csv
import random
import time
from datetime import datetime
from atproto import Client, models
from collections import defaultdict

def load_community_data(csv_file):
    """Load and group handles by community from the CSV file"""
    community_members = defaultdict(list)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            community_id = int(row['Community'])
            handle = row['Handle']
            community_members[community_id].append(handle)
    return community_members

def get_recent_posts(client, handle, limit=5):
    """Get recent posts from a specific user"""
    try:
        response = client.app.bsky.feed.get_author_feed({'actor': handle, 'limit': limit})
        posts = []
        for feed_view in response.feed:
            post = feed_view.post
            post_data = {
                'handle': handle,
                'text': post.record.text,
                'created_at': post.record.created_at,
                'likes': post.like_count if hasattr(post, 'like_count') else 0,
                'reposts': post.repost_count if hasattr(post, 'repost_count') else 0,
            }
            posts.append(post_data)
        return posts
    except Exception as e:
        print(f"Error fetching posts for {handle}: {str(e)}")
        return []

def sample_community_posts(username, password, community_data_file, output_file='output_data/community_posts.json'):
    """Sample recent posts from each community"""
    # Create client and login
    client = Client()
    client.login(username, password)
    
    # Load community data
    community_members = load_community_data(community_data_file)
    
    # Sample posts from each community
    community_posts = {}
    for community_id, members in community_members.items():
        print(f"\nProcessing community {community_id}")
        community_posts[community_id] = []
        
        # Randomly sample up to 5 members
        sampled_members = random.sample(members, min(5, len(members)))
        
        # Get posts from each sampled member
        for handle in sampled_members:
            print(f"  Fetching posts from {handle}")
            posts = get_recent_posts(client, handle)
            if posts:
                community_posts[community_id].extend(posts)
            time.sleep(0.5)  # Rate limiting
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save the results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(community_posts, f, indent=2, ensure_ascii=False)
    
    print(f"\nCommunity posts have been saved to {output_file}")
    
    # Print summary statistics
    print("\nSummary:")
    for community_id, posts in community_posts.items():
        print(f"Community {community_id}: {len(posts)} posts from {len(set(p['handle'] for p in posts))} members")

def main():
    # You need to replace these with your Bluesky credentials
    username = input("Enter your Bluesky handle (e.g., username.bsky.social): ").strip()
    password = input("Enter your Bluesky App Password (create one at Settings > App Passwords): ").strip()

    # Input and output files
    community_data_file = 'output_data/nodes_info.csv'
    output_file = 'output_data/community_posts.json'
    
    # Run the sampling
    sample_community_posts(username, password, community_data_file, output_file)

if __name__ == "__main__":
    main()
