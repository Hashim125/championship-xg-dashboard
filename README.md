# Championship xG Analysis Dashboard

A Streamlit dashboard that visualizes Expected Goals (xG) statistics for the Championship league, connected to a Snowflake database.

## Features

- **Interactive Scatter Plots**:
  - xG Per 90 vs xGA Per 90
  - xG Conversion vs xGA Conversion
  - Team highlighting and trend lines

- **Team Selector**: Filter and view detailed statistics for any team

- **Comprehensive Stats**:
  - xGD (Expected Goal Difference) and Points Per Game
  - Attacking metrics (Goals, xG, Open Play xG, Set Piece metrics, etc.)
  - Defensive metrics (Goals Against, xGA, Set Piece metrics, etc.)
  - League rankings with color-coded visualization

- **Auto-refresh**: Data cached for 1 week, automatically updates when Snowflake data is updated

## Prerequisites

- Python 3.8+
- Snowflake account with access to `IMPECT_EVENTS_STAGING` table
- RSA private key for Snowflake authentication (stored in `./keys/` directory)

## Installation

1. Clone or download this repository

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Ensure your `.env` file is configured with Snowflake credentials:
```env
SNOWFLAKE_ACCOUNT=TDAPVGQ-SL30706
SNOWFLAKE_USER=HUMARJI
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=CAFC_TEST_ANALYSIS
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_PRIVATE_KEY_PATH=./keys/rsa_key_unencrypted.pem
```

4. Ensure your RSA private key is in the `./keys/` directory

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## Project Structure

```
stats-overview/
├── app.py                  # Main Streamlit application
├── database.py             # Snowflake connection and data queries
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore             # Git ignore rules
├── keys/                  # RSA keys directory (not in git)
│   └── rsa_key_unencrypted.pem
└── README.md              # This file
```

## Data Source

The dashboard pulls data from the `IMPECT_EVENTS_STAGING` table in Snowflake, which contains:
- Match events data
- xG values for shots
- Team information
- Set piece indicators
- Match results for points calculation

## Calculations

- **xG Per 90**: Expected goals normalized per 90 minutes (1 match)
- **xGA Per 90**: Expected goals against normalized per 90 minutes
- **xG Conversion**: Actual goals divided by expected goals
- **xGD**: Expected goal difference (xG - xGA)
- **Points Per Game**: Total points divided by matches played
- **Set Piece stats**: Filtered by `setPieceCategory` or `inferredSetPiece` flag

## Caching

- Data is cached for **1 week (604,800 seconds)** using Streamlit's `@st.cache_data`
- To force a refresh, restart the Streamlit app or clear the cache from the UI (hamburger menu → Clear cache)

## Troubleshooting

### Connection Issues
- Verify your Snowflake credentials in `.env`
- Ensure the RSA private key path is correct and the file exists
- Check that your Snowflake user has access to the specified database and table

### Data Not Loading
- Verify the `IMPECT_EVENTS_STAGING` table exists and contains data
- Check Snowflake warehouse is running
- Review query in `database.py` if table structure has changed

### Display Issues
- Try different browsers (Chrome recommended)
- Clear browser cache
- Check console for JavaScript errors

## License

Private - Internal use only

## Contact

For issues or questions, contact the development team.
