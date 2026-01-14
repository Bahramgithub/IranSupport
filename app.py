import streamlit as st
import boto3
import json
import uuid
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Initialize AWS clients with credentials from Streamlit secrets
bedrock = boto3.client(
    'bedrock-runtime',
    region_name=st.secrets.get("AWS_DEFAULT_REGION", "us-east-1"),
    aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY")
)
dynamodb = boto3.resource(
    'dynamodb',
    region_name=st.secrets.get("AWS_DEFAULT_REGION", "us-east-1"),
    aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY")
)

# Bot configurations with best models
BOTS = {
    "Trauma Support Counselor": {
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "system": "You are a compassionate trauma counselor specializing in supporting individuals affected by regime violence and peaceful protest suppression. Provide empathetic, professional psychological support.",
        "max_tokens": 4096,
        "context_window": 200000
    },
    "Crisis Intervention Specialist": {
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "system": "You are a crisis intervention specialist trained in acute trauma response for victims of state violence. Focus on immediate emotional stabilization and safety.",
        "max_tokens": 4096,
        "context_window": 200000
    },
    "PTSD Support Guide": {
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "system": "You are a PTSD specialist helping individuals cope with post-traumatic stress from political violence and suppression. Provide evidence-based coping strategies.",
        "max_tokens": 4096,
        "context_window": 200000
    }
}

PROMPT_TEMPLATES = {
    "en": {
        "Initial Assessment": "I've experienced trauma from recent events and need someone to talk to. Can you help me understand what I'm feeling?",
        "Coping Strategies": "I'm struggling with anxiety and flashbacks. What coping techniques can help me manage these symptoms?",
        "Safety Planning": "I'm concerned about my safety and mental wellbeing. Can you help me create a safety plan?",
        "Grief Processing": "I've lost someone due to the violence. How can I process this grief while staying safe?",
        "Community Support": "I feel isolated and alone. How can I find support while protecting myself?"
    },
    "fa": {
        "ارزیابی اولیه": "من از رویدادهای اخیر آسیب روحی دیدهام و نیاز به صحبت کردن دارم. میتوانید به من کمک کنید احساساتم را درک کنم؟",
        "راهکارهای مقابله": "من با اضطراب و فلشبک دست و پنجه نرم میکنم. چه تکنیکهایی میتواند به من در مدیریت این علائم کمک کند؟",
        "برنامهریزی امنیتی": "من نگران امنیت و سلامت روانی خودم هستم. میتوانید به من در ایجاد یک برنامه امنیتی کمک کنید؟",
        "پردازش غم و اندوه": "من عزیزی را به خاطر خشونت از دست دادهام. چگونه میتوانم این غم را پردازش کنم و در عین حال امن بمانم؟",
        "حمایت اجتماعی": "احساس انزوا و تنهایی میکنم. چگونه میتوانم حمایت پیدا کنم و در عین حال از خودم محافظت کنم؟"
    }
}

def get_or_create_user_id():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def save_interaction(user_id, bot_name, prompt, response, model, web_search):
    try:
        table = dynamodb.Table('trauma-support-logs')
        table.put_item(Item={
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'interaction_id': str(uuid.uuid4()),
            'bot_name': bot_name,
            'prompt': prompt,
            'response': response,
            'model': model,
            'web_search_enabled': web_search
        })
    except Exception as e:
        st.warning(f"Logging failed: {str(e)}")

def call_bedrock(prompt, bot_config, max_tokens, web_search, language, conversation_history):
    system_prompt = bot_config["system"]
    if language == "fa":
        system_prompt += " Respond in Persian/Farsi language."
    
    messages = conversation_history + [{"role": "user", "content": prompt}]
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages,
        "system": system_prompt
    }
    
    response = bedrock.invoke_model(
        modelId=bot_config["model"],
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text']

def main():
    st.set_page_config(page_title="Trauma Support Bot", page_icon="🤝", layout="wide")
    
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #B3E5FC 0%, #81D4FA 50%, #4FC3F7 100%);
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #E1F5FE;
    }
    header[data-testid="stHeader"] {
        background-color: #0288D1;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #01579B !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    user_id = get_or_create_user_id()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'display_messages' not in st.session_state:
        st.session_state.display_messages = []
    
    # Sidebar configuration
    with st.sidebar:
        language = st.radio("Language / زبان", ["English", "فارسی"], horizontal=True)
        lang_code = "en" if language == "English" else "fa"
        
        st.header("⚙️ Configuration" if lang_code == "en" else "⚙️ تنظیمات")
        st.divider()
        
        selected_bot = st.selectbox("Select Support Bot" if lang_code == "en" else "انتخاب ربات حمایتی", list(BOTS.keys()))
        bot_config = BOTS[selected_bot]
        
        st.subheader("Model Settings" if lang_code == "en" else "تنظیمات مدل")
        
        model_override = st.text_input("Model ID (optional)" if lang_code == "en" else "شناسه مدل (اختیاری)", value=bot_config["model"])
        max_tokens = st.slider("Max Response Length" if lang_code == "en" else "حداکثر طول پاسخ", 1000, 8000, bot_config["max_tokens"], 500)
        web_search = st.checkbox("Enable Web Search" if lang_code == "en" else "فعالسازی جستجوی وب", value=False)
        
        st.divider()
        st.info(f"**Context Window:** {bot_config['context_window']:,} tokens" if lang_code == "en" else f"**پنجره متنی:** {bot_config['context_window']:,} توکن")
        st.caption(f"User ID: {user_id[:8]}..." if lang_code == "en" else f"شناسه کاربر: {user_id[:8]}...")
    
    st.title("🤝 Trauma Support Bot - Psychological Counseling Platform" if lang_code == "en" else "🤝 ربات حمایت روانی - پلتفرم مشاوره روانشناسی")
    st.markdown("*Compassionate AI-powered support for individuals affected by regime violence and peaceful protest suppression*" if lang_code == "en" else "*حمایت هوشمند و دلسوزانه برای افراد آسیبدیده از خشونت رژیم و سرکوب تظاهرات مسالمتآمیز*")
    
    # Main chat area
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("📝 Prompt Templates / قالبهای پیام")
        templates = PROMPT_TEMPLATES[lang_code]
        selected_template = st.selectbox(
            "Choose a starting point" if lang_code == "en" else "انتخاب نقطه شروع",
            ["Custom" if lang_code == "en" else "سفارشی"] + list(templates.keys())
        )
        
        custom_label = "Custom" if lang_code == "en" else "سفارشی"
        if selected_template != custom_label:
            template_text = templates[selected_template]
            st.text_area(
                "Template Preview" if lang_code == "en" else "پیشنمایش قالب",
                template_text, height=150, disabled=True
            )
            if st.button("Use Template" if lang_code == "en" else "استفاده از قالب", use_container_width=True):
                st.session_state.temp_prompt = template_text
                st.rerun()
    
    with col1:
        st.subheader("💬 Conversation" if lang_code == "en" else "💬 گفتگو")
        
        for msg in st.session_state.display_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        user_prompt = st.chat_input(
            "Share what you're experiencing..." if lang_code == "en" else "تجربه خود را به اشتراک بگذارید..."
        )
        
        if 'temp_prompt' in st.session_state:
            user_prompt = st.session_state.temp_prompt
            del st.session_state.temp_prompt
        
        if user_prompt:
            st.session_state.display_messages.append({"role": "user", "content": user_prompt})
            
            with st.chat_message("user"):
                st.markdown(user_prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..." if lang_code == "en" else "در حال فکر کردن..."):
                    try:
                        bot_config_copy = bot_config.copy()
                        bot_config_copy["model"] = model_override
                        
                        response = call_bedrock(user_prompt, bot_config_copy, max_tokens, web_search, lang_code, st.session_state.conversation_history)
                        
                        st.markdown(response)
                        
                        st.session_state.conversation_history.append({"role": "user", "content": user_prompt})
                        st.session_state.conversation_history.append({"role": "assistant", "content": response})
                        st.session_state.display_messages.append({"role": "assistant", "content": response})
                        
                        save_interaction(user_id, selected_bot, user_prompt, response, model_override, web_search)
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    st.divider()
    if lang_code == "en":
        st.markdown("""
        ### 🔒 Privacy & Safety
        - All conversations are confidential and logged anonymously
        - No authentication required - your privacy is protected
        - This is a support tool, not a replacement for professional therapy
        - In case of immediate danger, please contact local emergency services
        """)
    else:
        st.markdown("""
        ### 🔒 حریم خصوصی و امنیت
        - تمام گفتگوها محرمانه و به صورت ناشناس ثبت میشوند
        - نیازی به احراز هویت نیست - حریم خصوصی شما محافظت میشود
        - این یک ابزار حمایتی است، نه جایگزین درمان حرفهای
        - در صورت خطر فوری، با خدمات اورژانس محلی تماس بگیرید
        """)

if __name__ == "__main__":
    main()
