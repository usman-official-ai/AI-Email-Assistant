# 📧 AI Email Assistant Pro

<div align="center">

![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-API-FF6B6B?style=for-the-badge&logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)  

  <img width="1536" height="1024" alt="ChatGPT Image Jul 25, 2026, 05_31_04 PM" src="https://github.com/user-attachments/assets/34b7f796-64fb-438b-8738-f93cd7aa0609" />    
  


**An intelligent AI-powered Email Assistant that helps you write, improve, and reply to emails professionally using Groq's high-performance API.**

[![Deployed on Streamlit](https://img.shields.io/badge/Deployed_on-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ai-email-assistant-abnystr7pekwavbwfwtxuu.streamlit.app/)

</div>

---

## 🌐 Live Demo

**👉 [Click here to try the live demo](https://ai-email-assistant-abnystr7pekwavbwfwtxuu.streamlit.app/)**

---

## 📌 Table of Contents

- [🌟 Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [⚙️ Configuration](#️-configuration)
- [🔧 Tech Stack](#-tech-stack)
- [📊 System Status](#-system-status)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Features

### ✍️ Email Writing & Reply Generation
- **Generate Professional Replies** - Accept Meeting, Decline Politely, Request Info, Thank You, Follow-up
- **Smart Suggestions** - AI-powered context-aware responses

### 🔧 Grammar & Spelling Correction
- Fix grammar errors
- Correct spelling mistakes
- Improve sentence structure
- Fix punctuation issues

### 🎭 Tone Conversion
| Tone | Description |
|------|-------------|
| Professional | Business formal |
| Formal | Highly professional |
| Friendly | Warm and approachable |
| Polite | Respectful and courteous |
| Confident | Assertive and sure |
| Apologetic | Sincere and humble |
| Persuasive | Convincing and compelling |

### 📏 Length Options
- **Short** - Concise version
- **Medium** - Balanced (60-70% of original)
- **Detailed** - Expanded version

### 📌 Subject Line Generator
- Automatically generate 3-5 relevant subject lines
- Professional and engaging suggestions

### 💡 Improvement Suggestions
- Grammar improvements
- Readability improvements
- Tone suggestions
- Missing information
- Professional wording recommendations

### 🌐 Translation
- Translate emails to 10+ languages
- Preserve professional tone

### 📊 Sentiment Analysis
- Analyze email sentiment
- Emotional tone detection
- Key emotional indicators
- Suggested response approach

### 📤 Export Options
- **Copy to Clipboard** - One-click copy
- **TXT Download** - Plain text export
- **PDF Download** - Professional PDF format

### 🎨 UI Features
- **Dark Theme** - Professional dark mode
- **Responsive Design** - Works on all devices
- **API Status Indicator** - Real-time connection status
- **Quick Templates** - Ready-to-use email templates

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API Key ([Get it here](https://console.groq.com))

### Installation

#### Method 1: Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/usman-official-ai/AI-Email-Assistant.git
cd AI-Email-Assistant

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
echo GROQ_API_KEY=your_api_key_here > .env

# 6. Run the application
streamlit run app.py
```

#### Method 2: Deploy on Streamlit Cloud

1. Fork this repository
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Add secrets:
   ```toml
   GROQ_API_KEY = "your_api_key_here"
   ```
6. Click "Deploy"

**Your app will be live at:** `https://ai-email-assistant-abnystr7pekwavbwfwtxuu.streamlit.app/`

---

## 📁 Project Structure

```
AI-Email-Assistant/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # Documentation
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore file
│
├── src/                     # Source code
│   ├── __init__.py
│   ├── email_utils.py      # Groq API integration
│   ├── prompts.py          # System prompts
│   │
│   └── utils/              # Utility modules
│       ├── __init__.py
│       ├── pdf_export.py   # PDF generation
│       └── helpers.py      # Helper functions
│
└── assets/                 # Images and assets
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Model Configuration
DEFAULT_MODEL=llama-3.3-70b-versatile
MAX_TOKENS=2048
TEMPERATURE=0.7
```

### Available Models

| Model | Model ID | Best For |
|-------|----------|----------|
| Llama 3.3 70B | `llama-3.3-70b-versatile` | Best quality, complex tasks |
| Llama 3.1 8B | `llama-3.1-8b-instant` | Fast response, good quality |
| Llama 3 70B | `llama3-70b-8192` | High quality |
| Llama 3 8B | `llama3-8b-8192` | Fastest, simple tasks |
| Gemma 2 9B | `gemma2-9b-it` | General purpose |

---

## 🔧 Tech Stack

| Technology | Description |
|------------|-------------|
| [Streamlit](https://streamlit.io/) | Web application framework |
| [Groq API](https://groq.com/) | High-performance AI inference |
| [Python](https://python.org/) | Backend programming language |
| [ReportLab](https://www.reportlab.com/) | PDF generation |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable management |

### Python Packages

```txt
streamlit==1.28.0
groq==0.4.2
python-dotenv==1.0.0
reportlab==4.0.4
pyperclip==1.8.2
requests==2.31.0
```

---

## 📊 System Status

| Component | Status |
|-----------|--------|
| Groq API | ✅ Connected |
| PDF Export | ✅ Available |
| TXT Export | ✅ Available |
| Copy Feature | ✅ Available |
| Dark Theme | ✅ Active |

### API Rate Limits

- **Free Tier:** 30 requests per minute
- **Daily Limit:** 300 requests per day
- **Wait Time:** 5-10 minutes if limit exceeded

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/usman-official-ai/AI-Email-Assistant/issues)
- **Live Demo**: [Streamlit App](https://ai-email-assistant-abnystr7pekwavbwfwtxuu.streamlit.app/)

---

<div align="center">

**Made with ❤️ by [Usman]**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/usman-official-ai)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/usman-official-ai)

</div>

---

## ⭐ Features Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Email Assistant Pro                   │
├─────────────────────────────────────────────────────────────┤
│  ✍️ Write & Reply    │  🛠️ Improve Email    │  📌 Subject  │
│  ───────────────────  │  ───────────────────  │  ──────────  │
│  • Generate Email    │  • Fix Grammar       │  • Generate   │
│  • Generate Reply    │  • Change Tone       │    Subject    │
│  • 5 Reply Types     │  • Adjust Length     │    Lines      │
│  • Quick Templates   │  • Get Suggestions   │              │
├─────────────────────────────────────────────────────────────┤
│                      📤 Export Options                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  📋 Copy   │  │  📄 TXT    │  │  📑 PDF    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
├─────────────────────────────────────────────────────────────┤
│                    ⚙️ Settings & Features                    │
│  • 5 AI Models      • Dark/Light Theme   • Rate Limit Info  │
│  • Tone Options     • Length Options     • API Status       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Commands

```bash
# Run locally
streamlit run app.py

# Deploy on Streamlit Cloud
# Push to GitHub → Connect to Streamlit Cloud → Add Secrets → Deploy

# Check API Status
# View sidebar → API Status section

# Change Model
# Sidebar → Model Selection → Choose model
```

---

**Happy Email Writing! ✉️**
