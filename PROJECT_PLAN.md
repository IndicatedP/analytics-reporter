# Analytics Reporter - Project Plan

## Overview
Build a Python web application that generates availability reports for apartment rentals by processing reservation data and apartment mapping information.

## Data Sources

### 1. Fichier de Mapping (Apartment Mapping)
- **File**: `Fichier de mapping par appartement.xlsx`
- **Size**: 256 apartments × 7 columns
- **Key Fields**:
  - `Nom du logement` - Apartment name (links to reservations)
  - `Proprio` - Owner name (Roger, Franck, Yaacov F, Yaacov L, Rene, etc.)
  - `catégorie` - Category (studio, 1 chambre, 2 chambres, 3 chambres, 4 chambres)
  - `commission`, `CA référent`, `ménages`
- **Note**: Some apartments may appear multiple times to allow overbooking

### 2. Liste des Réservations (Reservations)
- **File**: `Liste des réservations-[dates].csv`
- **Current Sample**: 1,280 reservations (Oct 22 - Dec 31, 2025)
- **Size**: 69 columns with comprehensive booking data
- **Key Fields**:
  - `Nom du logement` - Links to mapping file
  - `Date d'arrivée` / `Date de sortie` - Check-in/out dates
  - `Statut` - Confirmée or Pré-réservation
  - `Location avec TVA` - Revenue with VAT
  - `Portail / Agent` - Booking platform

### 3. Rapport Disponibilité (Desired Output Format)
- **File**: `Rapport_disponibilite.xlsx`
- **Structure**: Multiple sheets (one per owner + one for all apartments)
- **Columns**: Date range periods + monthly summaries
- **Rows**: Summary rows (average prices) + individual apartments (availability status)

## Requirements

### Functional Requirements
1. **Upload any period of reservations** - Process CSV files for any date range
2. **Generate reports by owner** - Separate sheets for each property owner
3. **Generate all-apartments report** - Combined view of all properties
4. **Calculate availability status** - Disponible, Réservé, or Surbooking
5. **Calculate average prices** - By category (studio, 1-4 chambres) for each period
6. **Calculate occupancy rates** - Monthly percentage summaries

### Technical Requirements
1. Handle French characters and date formats
2. Support large datasets (1000+ reservations)
3. Generate Excel output with multiple sheets
4. User-friendly interface for file upload and date selection
5. Validate input data and handle errors gracefully

## Technology Stack

- **Language**: Python 3.x
- **Data Processing**: pandas, openpyxl
- **Web Framework**: Streamlit (for UI)
- **Date Handling**: datetime, python-dateutil
- **File Handling**: CSV and Excel (XLSX) formats

## Architecture

### Project Structure
```
analytics-reporter/
├── app.py                      # Main Streamlit application
├── modules/
│   ├── data_loader.py          # Load and validate input files
│   ├── period_generator.py     # Generate date range periods
│   ├── availability_engine.py  # Calculate availability status
│   ├── analytics.py            # Calculate prices and metrics
│   └── report_generator.py     # Generate Excel reports
├── utils/
│   ├── validators.py           # Input validation
│   └── formatters.py           # Excel formatting helpers
├── tests/                      # Unit tests
├── requirements.txt
└── README.md
```

### Core Modules

#### 1. Data Loader (`data_loader.py`)
**Responsibilities**:
- Load apartment mapping from Excel
- Load reservations from CSV (with proper encoding for French characters)
- Validate required columns exist
- Join/merge reservation data with apartment mapping

**Key Functions**:
```python
def load_mapping_file(filepath) -> pd.DataFrame
def load_reservations_file(filepath) -> pd.DataFrame
def merge_data(mapping, reservations) -> pd.DataFrame
def validate_data(df) -> bool
```

#### 2. Period Generator (`period_generator.py`)
**Responsibilities**:
- Generate 3-4 day periods based on user-specified date range
- Generate monthly summary periods
- Handle month boundaries and edge cases

**Key Functions**:
```python
def generate_periods(start_date, end_date, period_days=3) -> List[Tuple[date, date]]
def generate_monthly_periods(start_date, end_date) -> List[Tuple[str, date, date]]
def format_period_label(start, end) -> str  # e.g., "22/10 - 25/10"
```

#### 3. Availability Engine (`availability_engine.py`)
**Responsibilities**:
- Determine availability status for each apartment in each period
- Detect overbooking situations
- Calculate occupancy percentages for monthly summaries

**Key Functions**:
```python
def get_availability_status(apartment, period, reservations) -> str
def detect_overbooking(apartment, period, reservations) -> bool
def calculate_occupancy_rate(apartment, month_periods, reservations) -> float
```

**Logic**:
- "Disponible": No reservations overlap with period
- "Réservé": Exactly one reservation overlaps with period
- "Surbooking": Multiple reservations overlap with period

#### 4. Analytics Calculator (`analytics.py`)
**Responsibilities**:
- Calculate average prices by category for each period
- Handle different VAT scenarios
- Aggregate revenue metrics

**Key Functions**:
```python
def calculate_average_price(category, period, reservations) -> float
def get_category_reservations(category, period, reservations) -> pd.DataFrame
```

#### 5. Report Generator (`report_generator.py`)
**Responsibilities**:
- Create Excel workbook with multiple sheets
- Generate one sheet per owner
- Generate "All Apartments" combined sheet
- Format cells and apply styling

**Key Functions**:
```python
def create_report(merged_data, periods, owners) -> openpyxl.Workbook
def create_owner_sheet(wb, owner, apartments, periods, reservations)
def create_all_apartments_sheet(wb, apartments, periods, reservations)
def format_sheet(worksheet)
```

**Sheet Structure**:
```
Row 1: Headers                | Type | Period 1 | Period 2 | ... | Month Summary |
Row 2: Prix moyen - studio    | ...  | 150.00   | 160.00   | ... | 155.00       |
Row 3: Prix moyen - 1 chambre | ...  | 250.00   | 270.00   | ... | 260.00       |
...
Row N: Apartment Name         | ...  | Réservé  | Disponible| ... | 80.5%        |
```

## User Interface (Streamlit)

### Layout
```
┌────────────────────────────────────────────────┐
│  Analytics Reporter                            │
│  Generate availability reports for apartments  │
├────────────────────────────────────────────────┤
│                                                │
│  Step 1: Upload Mapping File                  │
│  📁 [Choose File: *.xlsx]                      │
│  ✓ Loaded: 256 apartments                     │
│                                                │
│  Step 2: Upload Reservations File             │
│  📁 [Choose File: *.csv]                       │
│  ✓ Loaded: 1,280 reservations                 │
│                                                │
│  Step 3: Select Date Range                    │
│  From: [📅 Oct 22, 2025]                       │
│  To:   [📅 Dec 31, 2025]                       │
│                                                │
│  [🔄 Generate Report]                          │
│                                                │
│  ✓ Report generated successfully!             │
│  📥 [Download Report.xlsx]                     │
│                                                │
└────────────────────────────────────────────────┘
```

### Features
- File upload widgets with validation
- Date range pickers with sensible defaults
- Progress indicators during report generation
- Download button for generated Excel file
- Error messages and validation feedback

## Implementation Plan

### Phase 1: Project Setup (Week 1)
**Tasks**:
- [ ] Set up Python virtual environment
- [ ] Install dependencies (pandas, openpyxl, streamlit, python-dateutil)
- [ ] Create project directory structure
- [ ] Initialize git repository
- [ ] Set up requirements.txt

**Deliverable**: Project scaffold ready for development

### Phase 2: Core Data Processing (Week 2-3)
**Tasks**:
- [ ] Implement `data_loader.py`
  - [ ] Load mapping file
  - [ ] Load reservations CSV with French character support
  - [ ] Validate data structure
  - [ ] Merge datasets
- [ ] Implement `period_generator.py`
  - [ ] Generate 3-4 day periods
  - [ ] Generate monthly periods
  - [ ] Format period labels
- [ ] Implement `availability_engine.py`
  - [ ] Check reservation overlaps
  - [ ] Detect overbooking
  - [ ] Calculate occupancy rates
- [ ] Write unit tests for core modules

**Deliverable**: Core data processing modules with tests

### Phase 3: Analytics & Reporting (Week 3-4)
**Tasks**:
- [ ] Implement `analytics.py`
  - [ ] Calculate average prices by category
  - [ ] Handle edge cases (no reservations, missing data)
- [ ] Implement `report_generator.py`
  - [ ] Create workbook with multiple sheets
  - [ ] Generate owner-specific sheets
  - [ ] Generate "All Apartments" sheet
  - [ ] Apply formatting and styling
- [ ] Test with sample data files

**Deliverable**: Fully functional report generation

### Phase 4: Web Interface (Week 4)
**Tasks**:
- [ ] Create Streamlit app (`app.py`)
- [ ] Implement file upload widgets
- [ ] Implement date range pickers
- [ ] Add generate button with progress indicator
- [ ] Add download functionality
- [ ] Add error handling and user feedback
- [ ] Style the interface

**Deliverable**: Complete web application

### Phase 5: Testing & Refinement (Week 5)
**Tasks**:
- [ ] End-to-end testing with provided sample files
- [ ] Test edge cases:
  - [ ] Overbooking scenarios
  - [ ] Missing apartments in mapping
  - [ ] Invalid date ranges
  - [ ] Large datasets (performance)
- [ ] User acceptance testing
- [ ] Bug fixes and refinements
- [ ] Documentation (README, user guide)

**Deliverable**: Production-ready application

## Key Algorithms

### 1. Period Generation Algorithm
```
Input: start_date, end_date, period_length (default 3 days)
Output: List of (start, end) tuples

1. Initialize current_date = start_date
2. While current_date <= end_date:
   a. period_end = min(current_date + period_length - 1 day, end_date)
   b. Add (current_date, period_end) to periods list
   c. current_date = period_end + 1 day
3. Return periods list
```

### 2. Availability Status Algorithm
```
Input: apartment, period, reservations
Output: "Disponible" | "Réservé" | "Surbooking"

1. Filter reservations for this apartment
2. Count overlapping reservations:
   - Overlaps if: (reservation_start <= period_end) AND (reservation_end >= period_start)
3. If count == 0: return "Disponible"
4. If count == 1: return "Réservé"
5. If count > 1: return "Surbooking"
```

### 3. Average Price Calculation
```
Input: category, period, reservations
Output: average_price (float or NaN)

1. Filter reservations for apartments of this category
2. Filter for reservations overlapping with period
3. If no reservations: return NaN
4. Calculate: sum(Location avec TVA) / count(reservations)
5. Return average_price
```

## Dependencies

```txt
pandas>=2.0.0
openpyxl>=3.1.0
streamlit>=1.28.0
python-dateutil>=2.8.0
```

## Success Criteria

1. ✅ Application can process any date range of reservations
2. ✅ Reports are generated with one sheet per owner
3. ✅ Reports include an "All Apartments" combined sheet
4. ✅ Availability status is correctly calculated (Disponible, Réservé, Surbooking)
5. ✅ Average prices are calculated by category for each period
6. ✅ Monthly occupancy percentages are calculated
7. ✅ Output format matches the example Rapport_disponibilite.xlsx
8. ✅ User can upload files and download generated report
9. ✅ Application handles French characters correctly
10. ✅ Performance is acceptable for datasets up to 5,000 reservations

## Future Enhancements (Post-MVP)

- Export to PDF format
- Email report delivery
- Scheduled report generation
- Multi-language support
- Advanced filtering (by portal, by category, etc.)
- Revenue analytics dashboard
- Mobile-responsive interface
- API for programmatic access
