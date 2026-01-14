import boto3
from datetime import datetime
import json

def view_logs(user_id=None, limit=50):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('trauma-support-logs')
    
    if user_id:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id),
            Limit=limit,
            ScanIndexForward=False
        )
    else:
        response = table.scan(Limit=limit)
    
    print(f"\n{'='*80}")
    print(f"TRAUMA SUPPORT BOT - INTERACTION LOGS")
    print(f"{'='*80}\n")
    
    for item in response['Items']:
        print(f"User: {item['user_id'][:12]}...")
        print(f"Time: {item['timestamp']}")
        print(f"Bot: {item['bot_name']}")
        print(f"Model: {item['model']}")
        print(f"\nPrompt:\n{item['prompt'][:200]}...")
        print(f"\nResponse:\n{item['response'][:200]}...")
        print(f"\n{'-'*80}\n")
    
    print(f"Total interactions shown: {len(response['Items'])}")

def get_user_stats():
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('trauma-support-logs')
    
    response = table.scan()
    items = response['Items']
    
    unique_users = len(set(item['user_id'] for item in items))
    total_interactions = len(items)
    
    bot_usage = {}
    for item in items:
        bot = item['bot_name']
        bot_usage[bot] = bot_usage.get(bot, 0) + 1
    
    print(f"\n{'='*80}")
    print(f"STATISTICS")
    print(f"{'='*80}")
    print(f"Unique Users: {unique_users}")
    print(f"Total Interactions: {total_interactions}")
    print(f"\nBot Usage:")
    for bot, count in bot_usage.items():
        print(f"  - {bot}: {count}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            get_user_stats()
        else:
            view_logs(user_id=sys.argv[1])
    else:
        print("Usage:")
        print("  python monitor.py              # View recent logs")
        print("  python monitor.py stats        # View statistics")
        print("  python monitor.py <user_id>    # View specific user logs")
        print()
        view_logs()
