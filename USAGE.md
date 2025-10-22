# Usage Guide - Analytics Reporter

## Quick Start

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Web Interface (Recommended)

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Your browser will open automatically at `http://localhost:8501`

3. Follow the steps in the web interface:
   - Upload apartment mapping file (Excel)
   - Upload reservations file (CSV)
   - Select date range
   - Click "Generate Report"
   - Download the generated Excel file

#### Option 2: Command Line (For Testing)

Run the test script:
```bash
python3 test_full_report.py
```

This will generate a report using the sample data files and save it as `Rapport_disponibilite_GENERATED.xlsx`.

## File Formats

### Input File 1: Apartment Mapping (Excel)

Required columns:
- `Nom du logement` - Apartment name
- `Proprio` - Owner name
- `catégorie` - Category (studio, 1 chambre, 2 chambres, etc.)

Optional columns:
- `commission`
- `CA référent`
- `ménages`

### Input File 2: Reservations (CSV)

Required columns:
- `Nom du logement` - Apartment name (must match mapping file)
- `Date d'arrivée` - Check-in date (format: DD/MM/YYYY)
- `Date de sortie` - Check-out date (format: DD/MM/YYYY)
- `Statut` - Status (Confirmée, Pré-réservation)
- `Location avec TVA` - Price with VAT
- `nuits` - Number of nights

The file should have a header row with column names on line 2 (line 1 is typically a title).

### Output: Availability Report (Excel)

The generated report contains:
- **Multiple sheets**: One per owner + one "All Apartments" combined sheet
- **Summary rows**: Average prices by category for each period
- **Apartment rows**: Availability status for each apartment and period

#### Column Structure:
- Column A: Type (apartment name or category)
- Date period columns: e.g., "22/10 - 25/10"
- Monthly summary columns: e.g., "October 2025 - Mois complet"

#### Cell Values:
- **For summary rows**: Average price per night (numeric)
- **For apartment rows**:
  - `Disponible` - No reservations
  - `Réservé` - One reservation
  - `Surbooking` - Multiple overlapping reservations
  - Monthly columns show occupancy percentage (e.g., "75.0%")

## Configuration

### Period Length

By default, the application generates 3-day periods. You can modify this in the code:

```python
periods = generate_periods(start_date, end_date, period_days=3)
```

Change `period_days=3` to your desired period length (e.g., `period_days=4` for 4-day periods).

## Troubleshooting

### "Missing required columns" error

Ensure your input files have all required columns with exact names (case-sensitive).

### "Reservations without owner information" warning

This means some apartments in the reservations file are not found in the mapping file. The report will still be generated, but these reservations won't be assigned to an owner.

### Web app doesn't start

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

Check that port 8501 is not in use by another application.

### Report generation is slow

For large datasets (5000+ reservations), report generation may take 1-2 minutes. This is normal.

## Examples

### Example 1: Generate report for October 2025

1. Upload mapping file
2. Upload reservations file (any file containing October 2025 data)
3. Set date range: From 2025-10-01 to 2025-10-31
4. Click "Generate Report"

### Example 2: Generate report for specific owner

The application automatically creates separate sheets for each owner. After downloading the report, you can:
1. Open the Excel file
2. Navigate to the sheet for the specific owner (e.g., "Roger", "Franck")
3. View/analyze that owner's apartments

## Advanced Usage

### Programmatic Usage

You can also use the modules programmatically in your own Python scripts:

```python
from modules.data_loader import load_and_prepare_data
from modules.period_generator import generate_periods, generate_monthly_periods
from modules.report_generator import create_report
from datetime import date

# Load data
merged, mapping = load_and_prepare_data(
    'Fichier de mapping par appartement.xlsx',
    'Liste des réservations.csv'
)

# Generate periods
start = date(2025, 10, 22)
end = date(2025, 12, 31)
periods = generate_periods(start, end)
monthly = generate_monthly_periods(start, end)

# Create report
wb = create_report(merged, mapping, periods, monthly, 'output_report.xlsx')
```

## Support

For issues or questions:
1. Check this usage guide
2. Review the PROJECT_PLAN.md file
3. Contact your administrator
