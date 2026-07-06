python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python -m radgram.cli init-db
python -m radgram.cli serve
