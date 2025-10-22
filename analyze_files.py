#!/usr/bin/env python3
"""
Script to analyze the three input files and understand their structure
"""
import pandas as pd
import sys

def analyze_mapping_file(filepath):
    """Analyze the apartment mapping file"""
    print("\n" + "="*80)
    print("1. FICHIER DE MAPPING (Apartment Mapping File)")
    print("="*80)

    # Try reading all sheets
    try:
        excel_file = pd.ExcelFile(filepath)
        print(f"\nSheets found: {excel_file.sheet_names}")

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"\nColumns:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")

            print(f"\nFirst 3 rows:")
            print(df.head(3).to_string())

            # Check for duplicates
            if 'Nom du logement' in df.columns or any('nom' in str(col).lower() for col in df.columns):
                apartment_col = [col for col in df.columns if 'nom' in str(col).lower() and 'logement' in str(col).lower()]
                if apartment_col:
                    duplicates = df[apartment_col[0]].value_counts()
                    print(f"\nApartment occurrence count (showing duplicates):")
                    print(duplicates[duplicates > 1].head(10))
    except Exception as e:
        print(f"Error reading mapping file: {e}")

def analyze_reservations_file(filepath):
    """Analyze the reservations CSV file"""
    print("\n" + "="*80)
    print("2. LISTE DES RÉSERVATIONS (Reservations List)")
    print("="*80)

    try:
        # Read CSV with proper handling of French characters
        df = pd.read_csv(filepath, skiprows=1)  # Skip the first row which is just "Liste des réservations"

        print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"\nColumns ({len(df.columns)} total):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")

        print(f"\nDate range of reservations:")
        date_col = "Date d'arrivée"
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce')
            print(f"  From: {df[date_col].min()}")
            print(f"  To: {df[date_col].max()}")

        print(f"\nReservation statuses:")
        if "Statut" in df.columns:
            print(df["Statut"].value_counts())

        print(f"\nPortals/Agents:")
        if "Portail / Agent" in df.columns:
            print(df["Portail / Agent"].value_counts())

        print(f"\nSample reservation (first row):")
        print(df.head(1).T.to_string())

        print(f"\nUnique apartments in reservations:")
        if "Nom du logement" in df.columns:
            print(f"  Total unique apartments: {df['Nom du logement'].nunique()}")
            print(f"  Sample apartment names:")
            print(df['Nom du logement'].value_counts().head(10))

    except Exception as e:
        print(f"Error reading reservations file: {e}")
        import traceback
        traceback.print_exc()

def analyze_report_file(filepath):
    """Analyze the availability report file (desired output)"""
    print("\n" + "="*80)
    print("3. RAPPORT DISPONIBILITÉ (Availability Report - Desired Output)")
    print("="*80)

    try:
        excel_file = pd.ExcelFile(filepath)
        print(f"\nSheets found: {excel_file.sheet_names}")

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"\nColumns:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")

            print(f"\nFirst 5 rows:")
            print(df.head(5).to_string())

            print(f"\nLast 5 rows:")
            print(df.tail(5).to_string())

    except Exception as e:
        print(f"Error reading report file: {e}")

if __name__ == "__main__":
    base_path = "/Users/apupkin/Documents/Projects/Analytics Reporter"

    mapping_file = f"{base_path}/Fichier de mapping par appartement.xlsx"
    reservations_file = f"{base_path}/Liste des réservations-22-10-2025-31-10-2025.csv"
    report_file = f"{base_path}/Rapport_disponibilite.xlsx"

    analyze_mapping_file(mapping_file)
    analyze_reservations_file(reservations_file)
    analyze_report_file(report_file)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
