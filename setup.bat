@echo off
echo 🚀 Setting up AI Email Assistant...

echo.
echo 📦 Creating virtual environment...
python -m venv venv

echo.
echo 📦 Activating virtual environment...
call venv\Scripts\activate

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 📝 Creating .env file from example...
copy .env.example .env

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo 1. Edit .env file and add your Groq API key
echo 2. Run: streamlit run app.py
echo.
pause