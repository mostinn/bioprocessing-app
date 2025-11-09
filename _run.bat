@echo off
REM Clear Streamlit cache
python -m streamlit cache clear

REM Run the Streamlit app
python -m streamlit run Bioprocessing_app.py
