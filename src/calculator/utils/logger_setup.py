import os
import json
import logging
import logging.config
import streamlit as st
from pathlib import Path

@st.cache_resource
def setup_logging():
    """
    Configures logging once and returns the debug logger.
    Streamlit will skip this function on every rerun after the first.
    """
    # 1. Locate the config file relative to this file
    current_dir = Path(__file__).parent.parent # Goes up to calculator/
    config_path = current_dir / "logs" / "config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    # 2. Apply the configuration
    logging.config.dictConfig(config)
    
    # 3. Get the specific logger
    logger = logging.getLogger('calculator_debug')
    
    logger.info("Logger initialized for the first time.")
    return logger

# Create a global instance that can be imported elsewhere
debugLogger = setup_logging()