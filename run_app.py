#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def run_streamlit_app():
    """Run the bioprocessing streamlit app"""
    try:
        # Change to the app directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(app_dir)
        
        # Run streamlit using python module syntax
        cmd = [sys.executable, "-m", "streamlit", "run", "Bioprocessing_app.py"]
        
        print("Starting Bioprocessing Simulation App...")
        print("The app will open in your default web browser.")
        print("Press Ctrl+C to stop the app.")
        
        # Run the command
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running the app: {e}")
        print("Make sure streamlit is installed: pip install streamlit")
    except KeyboardInterrupt:
        print("\nApp stopped by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_streamlit_app()