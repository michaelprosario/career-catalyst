"""
Main entry point for the Career Catalyst Flask application.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.presentation.app import run_app


if __name__ == '__main__':
    print("Starting Career Catalyst API...")
    run_app()