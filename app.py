"""
Analytics Reporter - Streamlit Application
Generate availability reports for apartment rentals.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import load_mapping_file, load_reservations_file, merge_data, DataLoaderError
from modules.period_generator import generate_periods, generate_monthly_periods
from modules.report_generator import create_report, save_to_bytes


# Page config
st.set_page_config(
    page_title="Analytics Reporter",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Analytics Reporter")
st.markdown("""
Generate availability reports for apartment rentals.
Upload your mapping and reservations files, select a date range, and download the generated report.
""")

st.divider()

# Initialize session state
if 'mapping_df' not in st.session_state:
    st.session_state.mapping_df = None
if 'reservations_df' not in st.session_state:
    st.session_state.reservations_df = None
if 'merged_df' not in st.session_state:
    st.session_state.merged_df = None
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False


# Step 1: Upload Mapping File
st.header("Step 1: Upload Mapping File")
mapping_file = st.file_uploader(
    "Choose apartment mapping file (Excel)",
    type=['xlsx', 'xls'],
    help="Upload the Excel file containing apartment information and owner details"
)

if mapping_file is not None:
    try:
        with st.spinner("Loading mapping file..."):
            # Save uploaded file temporarily
            temp_mapping_path = f"/tmp/mapping_{mapping_file.name}"
            with open(temp_mapping_path, 'wb') as f:
                f.write(mapping_file.getbuffer())

            # Load mapping
            st.session_state.mapping_df = load_mapping_file(temp_mapping_path)

        st.success(f"✓ Loaded {len(st.session_state.mapping_df)} apartments")

        # Show preview
        with st.expander("Preview mapping data"):
            st.dataframe(st.session_state.mapping_df.head(10))
            st.write(f"**Owners:** {st.session_state.mapping_df['Proprio'].nunique()}")
            st.write(f"**Categories:** {', '.join(map(str, st.session_state.mapping_df['catégorie'].dropna().unique()))}")

    except DataLoaderError as e:
        st.error(f"Error loading mapping file: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

st.divider()

# Step 2: Upload Reservations File
st.header("Step 2: Upload Reservations File")
reservations_file = st.file_uploader(
    "Choose reservations file (CSV)",
    type=['csv'],
    help="Upload the CSV file containing reservation data"
)

if reservations_file is not None:
    try:
        with st.spinner("Loading reservations file..."):
            # Save uploaded file temporarily
            temp_res_path = f"/tmp/reservations_{reservations_file.name}"
            with open(temp_res_path, 'wb') as f:
                f.write(reservations_file.getbuffer())

            # Load reservations
            st.session_state.reservations_df = load_reservations_file(temp_res_path)

        st.success(f"✓ Loaded {len(st.session_state.reservations_df)} reservations")

        # Show date range
        date_col = 'Date d\'arrivée'
        sortie_col = 'Date de sortie'
        min_date = st.session_state.reservations_df[date_col].min()
        max_date = st.session_state.reservations_df[sortie_col].max()

        st.info(f"📅 Reservation date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

        # Show preview
        with st.expander("Preview reservations data"):
            preview_cols = ['Nom du logement', 'Date d\'arrivée', 'Date de sortie', 'Statut', 'Location avec TVA']
            available_cols = [col for col in preview_cols if col in st.session_state.reservations_df.columns]
            st.dataframe(st.session_state.reservations_df[available_cols].head(10))
            st.write(f"**Unique apartments:** {st.session_state.reservations_df['Nom du logement'].nunique()}")
            st.write(f"**Status breakdown:** {st.session_state.reservations_df['Statut'].value_counts().to_dict()}")

    except DataLoaderError as e:
        st.error(f"Error loading reservations file: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

st.divider()

# Step 3: Merge data if both files are loaded
if st.session_state.mapping_df is not None and st.session_state.reservations_df is not None:
    if st.session_state.merged_df is None:
        with st.spinner("Merging data..."):
            try:
                st.session_state.merged_df, _ = merge_data(
                    st.session_state.mapping_df,
                    st.session_state.reservations_df
                )
                st.success("✓ Data merged successfully")
            except Exception as e:
                st.error(f"Error merging data: {str(e)}")

# Step 4: Select Date Range
st.header("Step 3: Select Date Range")

if st.session_state.reservations_df is not None:
    # Get min/max dates from reservations
    date_col = 'Date d\'arrivée'
    sortie_col = 'Date de sortie'
    min_date = st.session_state.reservations_df[date_col].min().date()
    max_date = st.session_state.reservations_df[sortie_col].max().date()

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "From",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            help="Start date for the report"
        )

    with col2:
        end_date = st.date_input(
            "To",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            help="End date for the report"
        )

    # Validate date range
    if start_date > end_date:
        st.error("Error: Start date must be before or equal to end date")
    else:
        st.info(f"Selected period: {(end_date - start_date).days + 1} days")

else:
    st.warning("Please upload reservations file first to select date range")
    start_date = None
    end_date = None

st.divider()

# Step 5: Generate Report
st.header("Step 4: Generate Report")

if st.session_state.merged_df is not None and start_date is not None and end_date is not None:
    if st.button("🔄 Generate Report", type="primary", use_container_width=True):
        try:
            with st.spinner("Generating report... This may take a moment."):
                # Generate periods
                progress_bar = st.progress(0)
                st.text("Generating date periods...")
                periods = generate_periods(start_date, end_date, period_days=3)
                monthly_periods = generate_monthly_periods(start_date, end_date)
                progress_bar.progress(30)

                st.text(f"Creating report with {len(periods)} periods and {len(monthly_periods)} months...")

                # Create report
                wb = create_report(
                    st.session_state.merged_df,
                    st.session_state.mapping_df,
                    periods,
                    monthly_periods
                )
                progress_bar.progress(90)

                # Save to bytes
                st.text("Preparing download...")
                buffer = save_to_bytes(wb)
                st.session_state.report_buffer = buffer
                st.session_state.report_generated = True
                progress_bar.progress(100)

            st.success("✓ Report generated successfully!")

        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

    # Show download button if report is generated
    if st.session_state.report_generated and hasattr(st.session_state, 'report_buffer'):
        st.divider()
        st.subheader("📥 Download Report")

        # Generate filename
        filename = f"Rapport_disponibilite_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.xlsx"

        st.download_button(
            label="📥 Download Excel Report",
            data=st.session_state.report_buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.info(f"Report includes {len(st.session_state.mapping_df['Proprio'].unique())} owner sheets + 1 combined sheet")

else:
    st.warning("Please complete all previous steps before generating report")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
Analytics Reporter v1.0<br>
For support or issues, contact your administrator
</div>
""", unsafe_allow_html=True)
