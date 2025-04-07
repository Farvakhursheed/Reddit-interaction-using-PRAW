import praw
import time
from datetime import datetime
import random
from config import *


class RedditEngagementBot:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent=USER_AGENT
        )
        
        self.subreddits = ['test', 'Python']
        self.keywords = ['health', 'wellness', 'medicine']
        self.min_post_age = 30
        self.max_post_age = 86400
        self.comment_delay = 30
        
        self.responses = [
            "That's an interesting perspective on {topic}! Have you considered...",
            "Thanks for sharing about {topic}. From what I've learned...",
            "Regarding {topic}, many people find it helpful to..."
        ]
        
    def monitor_subreddits(self):
        """Monitor configured subreddits for relevant discussions"""
        while True:
            try:
                for subreddit_name in self.subreddits:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    print(f"\nChecking r/{subreddit_name}...")
                    
                    for submission in subreddit.new(limit=10):
                        self.process_submission(submission)
                    
                    time.sleep(self.comment_delay)
                
                time.sleep(300)
                
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(600)
    
    def process_submission(self, submission):
        """Process a submission to determine if we should comment"""
        post_age = datetime.utcnow().timestamp() - submission.created_utc
        if post_age < self.min_post_age or post_age > self.max_post_age:
            return
        
        content = f"{submission.title} {submission.selftext}".lower()
        matched_keywords = [kw for kw in self.keywords if kw in content]
        
        if not matched_keywords:
            return
        
        print(f"Found relevant post: {submission.title}")
        print(f"URL: https://reddit.com{submission.permalink}")
        print(f"Matched keywords: {', '.join(matched_keywords)}")
        
        if not self.has_commented(submission):
            self.post_comment(submission, matched_keywords[0])
    
    def has_commented(self, submission):
        """Check if we've already commented on this post"""
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if comment.author == self.reddit.user.me():
                return True
        return False
    
    def post_comment(self, submission, topic):
        """Post a comment to the submission"""
        try:
            response_template = random.choice(self.responses)
            response = response_template.format(topic=topic)
            
            comment = submission.reply(response)
            print(f"Posted comment: {response[:50]}...")
            print(f"Comment URL: https://reddit.com{comment.permalink}")
            
            time.sleep(self.comment_delay)
            
        except praw.exceptions.APIException as e:
            if e.error_type == "RATELIMIT":
                delay = self.parse_ratelimit_message(str(e))
                print(f"Hit rate limit. Waiting {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"API Error: {e}")
    
    @staticmethod
    def parse_ratelimit_message(message):
        """Extract wait time from rate limit message"""
        import re
        matches = re.search(r"wait (\d+) (minutes|seconds)", message)
        if matches:
            value, unit = matches.groups()
            return int(value) * 60 if unit == "minutes" else int(value)
        return 60

if __name__ == "__main__":
    bot = RedditEngagementBot()
    bot.monitor_subreddits()