"""
Mapping between team names in database and badge file names
"""
import os
from PIL import Image
import base64
from io import BytesIO

BADGE_DIR = "./Club Badges"

# Mapping from database team names to badge filenames
TEAM_BADGE_MAP = {
    'AFC Wrexham': 'Wrexham_A.F.C._Logo.svg.png',
    'Birmingham City': 'Birmingham-City.png',
    'Blackburn Rovers': 'Blackburn_Rovers.svg.png',
    'Bristol City': 'Bristol_City_crest.svg.png',
    'Charlton Athletic': 'Charlton Logo.png',
    'Coventry City': 'Coventry_City_FC_crest.svg.png',
    'Derby County': 'Derby_County_crest.svg.png',
    'FC Middlesbrough': 'Middlesbrough_FC_crest.svg.png',
    'FC Millwall': 'Millwall_FC_crest.svg.png',
    'FC Portsmouth': 'Portsmouth_FC_logo.svg.png',
    'FC Southampton': 'FC_Southampton.svg.png',
    'FC Watford': 'Watford.svg.png',
    'Hull City': 'Hull_City_A.F.C._logo.svg.png',
    'Ipswich Town': 'Ipswich_Town.svg.png',
    'Leicester City': 'Leicester_City_crest.svg.png',
    'Norwich City': 'Norwich_City.png',
    'Oxford United': 'Oxford_United_FC_logo.svg.png',
    'Preston North End': 'Preston_North_End_FC.svg.png',
    'Queens Park Rangers': 'Queens_Park_Rangers_crest.svg.png',
    'Sheffield United': 'Sheffield_United_FC_logo.svg.png',
    'Sheffield Wednesday': 'Sheffield_Wednesday_badge.svg.png',
    'Stoke City': 'Stoke_City_FC.svg.png',
    'Swansea City': 'Swansea_City_A.F.C._logo.png',
    'West Bromwich Albion': 'West_Bromwich_Albion.svg.png',
}

def get_badge_path(team_name):
    """Get the full path to a team's badge file."""
    badge_filename = TEAM_BADGE_MAP.get(team_name)
    if badge_filename:
        path = os.path.join(BADGE_DIR, badge_filename)
        if os.path.exists(path):
            return path
    return None

def get_all_badges():
    """Get paths for all team badges as a dictionary."""
    badges = {}
    for team, filename in TEAM_BADGE_MAP.items():
        path = os.path.join(BADGE_DIR, filename)
        if os.path.exists(path):
            badges[team] = path
    return badges

def image_to_base64(image_path, size=(30, 30)):
    """Convert image to base64 for Plotly."""
    try:
        img = Image.open(image_path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None
