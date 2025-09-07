# my-brokers Setup
python3 -m venv venv
source venv/bin/activate войти
pip install -r requirements.txt установить

# commands
ruff format
ruff check, and check --fix
python main.py


# Check
langChain посмотреть

# в корне проекта
python3.11 -m venv .venv_clean
source .venv_clean/bin/activate
pip install --upgrade pip
pip install torch==2.7.1 torchaudio==2.7.1
pip install "git+https://github.com/2noise/ChatTTS.git"

pip unintall transformers
pip install transformers==4.53.2