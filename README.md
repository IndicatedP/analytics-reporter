# Analytics Reporter

Generate availability reports for apartment rentals.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Upload the apartment mapping file (Excel)
2. Upload the reservations file (CSV)
3. Select your desired date range
4. Click "Generate Report"
5. Download the generated Excel report

## Features

- Process reservations for any date range
- Generate reports by owner
- Include "All Apartments" combined view
- Calculate availability status (Disponible, Réservé, Surbooking)
- Calculate average prices by category
- Calculate monthly occupancy percentages
