"""
PROJECT MICRO-GIG: Instagram Metrics Reporter
Architecture: Production-grade web scraping and reporting system
Purpose: Fulfill $5 Fiverr contracts for social media metric reporting
Features:
- Robust error handling with exponential backoff
- Type-hinted with comprehensive logging
- Firestore state management for job tracking
- PDF report generation with visualizations
- Client-specific configuration via Firebase
"""

import logging
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
from dataclasses import dataclass, asdict
import hashlib

# Third-party imports
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use

# Firebase for state management
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1.base_query import FieldFilter
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase unavailable - running in local mode only")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('micro_gig_scraper.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    """Configuration for scraping job with validation"""
    target_username: str
    days_back: int = 30
    metrics: Tuple[str, ...] = ('followers', 'engagement_rate', 'post_count', 'reach')