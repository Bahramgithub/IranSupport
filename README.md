# Trauma Support Bot - Psychological Counseling Platform

A compassionate AI-powered support system for individuals affected by regime violence and peaceful protest suppression.

## Features

- **Multiple Specialized Bots**: Trauma counselor, crisis intervention, PTSD support
- **Best-in-Class AI**: Uses Claude 3.5 Sonnet v2 (200K context, 4K+ response)
- **Prompt Templates**: Pre-configured starting points for common needs
- **Configurable**: Adjust model, context length, response length
- **Anonymous Logging**: DynamoDB tracks interactions without authentication
- **Privacy-First**: No login required, anonymous user IDs

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Key, and region (us-east-1)
```

### 3. Enable Bedrock Models
- Go to AWS Console → Bedrock → Model Access
- Request access to: `Claude 3.5 Sonnet v2`

### 4. Create DynamoDB Table
```bash
python setup_db.py
```

### 5. Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage

1. **Select a Bot**: Choose from specialized support bots in the sidebar
2. **Choose Template**: Pick a prompt template or write custom message
3. **Configure Settings**: Adjust max response length, enable web search
4. **Send Message**: Share your experience and receive support
5. **Review Response**: Read compassionate, professional guidance

## Bot Types

- **Trauma Support Counselor**: General trauma support and emotional processing
- **Crisis Intervention Specialist**: Immediate crisis response and stabilization
- **PTSD Support Guide**: Evidence-based PTSD coping strategies

## Privacy & Security

- No authentication required
- Anonymous user IDs (UUID)
- All logs stored in DynamoDB for monitoring
- Confidential conversations
- No personal data collection

## Monitoring

Query logs in DynamoDB:
```python
import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('trauma-support-logs')
response = table.scan()
print(response['Items'])
```

## Cost Considerations

- **Bedrock**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **DynamoDB**: Pay-per-request (free tier: 25 WCU, 25 RCU)
- Estimated: $0.05-0.20 per conversation

## Important Notes

⚠️ This is a support tool, NOT a replacement for professional therapy
⚠️ In immediate danger, contact local emergency services
⚠️ Ensure AWS credentials have Bedrock and DynamoDB permissions

## License

MIT - Use freely for humanitarian purposes
