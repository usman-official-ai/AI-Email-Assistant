# src/utils/helpers.py
"""
Helper utility functions for the Email Assistant.
"""

import re
import os
from datetime import datetime
from typing import List, Dict

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_email_content(text: str) -> Dict[str, str]:
    """Extract email components from text."""
    lines = text.split('\n')
    email_data = {
        'subject': '',
        'body': '',
        'sender': '',
        'recipient': '',
        'signature': ''
    }
    
    subject_pattern = r'^subject:\s*(.+)$'
    from_pattern = r'^from:\s*(.+)$'
    to_pattern = r'^to:\s*(.+)$'
    
    body_lines = []
    signature_lines = []
    in_signature = False
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check for headers
        if re.match(subject_pattern, line_lower):
            email_data['subject'] = re.match(subject_pattern, line, re.I).group(1)
        elif re.match(from_pattern, line_lower):
            email_data['sender'] = re.match(from_pattern, line, re.I).group(1)
        elif re.match(to_pattern, line_lower):
            email_data['recipient'] = re.match(to_pattern, line, re.I).group(1)
        else:
            # Check for signature indicators
            if line.strip().startswith('Best') or line.strip().startswith('Sincerely') or \
               line.strip().startswith('Yours') or line.strip().startswith('Thanks') or \
               line.strip().startswith('Regards'):
                in_signature = True
            
            if in_signature:
                signature_lines.append(line)
            else:
                body_lines.append(line)
    
    email_data['body'] = '\n'.join(body_lines).strip()
    email_data['signature'] = '\n'.join(signature_lines).strip()
    
    return email_data

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def truncate_text(text: str, max_length: int = 1000, suffix: str = '...') -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix

def format_timestamp(timestamp=None) -> str:
    """Format timestamp for display."""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%B %d, %Y at %I:%M %p")

def generate_filename(prefix: str = 'email', extension: str = 'txt') -> str:
    """Generate a unique filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"