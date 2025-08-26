# my-brokers
python3 -m venv venv
source venv/bin/activate войти

pip install -r requirements.txt установить


python main.py tracks/ sets/mix.mp3 --mode beats --xfade-beats 16 --playlist WorkCodingFocus
python main.py tracks/ sets/mix.mp3 --mode simple --xfade-beats 16 --playlist WorkCodingFocus

ruff format
ruff check, and check --fix