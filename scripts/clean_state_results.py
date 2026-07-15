import csv
import re
import os
import pandas as pd

# Raw and output file paths
raw_file_path = r"c:\Users\mohdh\OneDrive\Desktop\Projects\Election Campaign Analysis\data\raw\result_by_stae&ut(with alliance).csv"
output_file_path = r"c:\Users\mohdh\OneDrive\Desktop\Projects\Election Campaign Analysis\data\cleaned\result_by_state_cleaned.csv"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

# Canonical map for State / UT names
states_uts_map = {
    'andaman and nicobar islands': 'Andaman and Nicobar Islands',
    'andaman & nicobar islands': 'Andaman and Nicobar Islands',
    'andaman & nicobar': 'Andaman and Nicobar Islands',
    'andhra pradesh': 'Andhra Pradesh',
    'arunachal pradesh': 'Arunachal Pradesh',
    'assam': 'Assam',
    'bihar': 'Bihar',
    'chandigarh': 'Chandigarh',
    'chhattisgarh': 'Chhattisgarh',
    'dadra and nagar haveli': 'Dadra and Nagar Haveli',
    'dadra & nagar haveli': 'Dadra and Nagar Haveli',
    'dadra and nagar haveli and daman and diu': 'Dadra and Nagar Haveli and Daman and Diu',
    'daman and diu': 'Daman and Diu',
    'daman & diu': 'Daman and Diu',
    'delhi': 'Delhi',
    'nct of delhi': 'Delhi',
    'national capital territory of delhi': 'Delhi',
    'goa': 'Goa',
    'gujarat': 'Gujarat',
    'haryana': 'Haryana',
    'himachal pradesh': 'Himachal Pradesh',
    'jammu and kashmir': 'Jammu and Kashmir',
    'jammu & kashmir': 'Jammu and Kashmir',
    'jharkhand': 'Jharkhand',
    'karnataka': 'Karnataka',
    'kerala': 'Kerala',
    'lakshadweep': 'Lakshadweep',
    'madhya pradesh': 'Madhya Pradesh',
    'maharashtra': 'Maharashtra',
    'manipur': 'Manipur',
    'meghalaya': 'Meghalaya',
    'mizoram': 'Mizoram',
    'nagaland': 'Nagaland',
    'odisha': 'Odisha',
    'orissa': 'Odisha',
    'puducherry': 'Puducherry',
    'pondicherry': 'Puducherry',
    'punjab': 'Punjab',
    'rajasthan': 'Rajasthan',
    'sikkim': 'Sikkim',
    'tamil nadu': 'Tamil Nadu',
    'telangana': 'Telangana',
    'tripura': 'Tripura',
    'uttar pradesh': 'Uttar Pradesh',
    'uttarakhand': 'Uttarakhand',
    'uttaranchal': 'Uttarakhand',
    'west bengal': 'West Bengal',
    'ladakh': 'Ladakh'
}

def clean_int(val):
    if not val:
        return None
    val_clean = re.sub(r'[^\d-]', '', val.strip())
    if not val_clean:
        return None
    try:
        return int(val_clean)
    except ValueError:
        return None

def clean_float(val):
    if not val:
        return None
    val_clean = re.sub(r'[^\d\.-]', '', val.strip())
    if not val_clean:
        return None
    try:
        return float(val_clean)
    except ValueError:
        return None

def normalize_string(val):
    if not val:
        return ""
    # Decode Unicode characters and clean smart punctuation/non-breaking spaces
    s = val.strip()
    s = s.replace('\xa0', ' ')
    s = s.replace('â\x80\x83', ' ')
    s = s.replace('\x80\x93', '-')
    s = s.replace('â\x80\x93', '-')
    s = s.replace('â\x80\x99', "'")
    s = s.replace('â\x80\x98', "'")
    s = s.replace('’', "'")
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def standardize_party(party_name):
    # Strip bracketed or parenthesized alliance suffixes, handling optional closing parenthesis
    cleaned_name = re.sub(r'\s*\(\s*(NDA|UPA|INDIA|LF|LDF|UDF|Third Front|Others)\s*\)?\s*$', '', party_name, flags=re.IGNORECASE)
    # Strip any trailing control characters or mojibake (like â or Â)
    cleaned_name = re.sub(r'[\sÂâ\x80-\xff]+$', '', cleaned_name)
    cleaned_name = normalize_string(cleaned_name)
    
    # Strip again in case of smart spaces or order anomalies
    cleaned_name = re.sub(r'\s*\(\s*(NDA|UPA|INDIA|LF|LDF|UDF|Third Front|Others)\s*\)?\s*$', '', cleaned_name, flags=re.IGNORECASE)
    cleaned_name = re.sub(r'[\sÂâ\x80-\xff]+$', '', cleaned_name)
    cleaned_name = normalize_string(cleaned_name)
    p = cleaned_name.lower()
    
    # Comprehensive party mapping consistent with clean_data.py
    mapping = {

        'indian national congress': 'INC',
        'inc': 'INC',
        'bharatiya janata party': 'BJP',
        'bjp': 'BJP',
        'ysr congress party': 'YSRCP',
        'ysrcp': 'YSRCP',
        'yrscp': 'YSRCP',
        'telugu desam party': 'TDP',
        'tdp': 'TDP',
        'telangana rashtra samithi': 'TRS',
        'trs': 'TRS',
        'bharat rashtra samithi': 'BRS',
        'brs': 'BRS',
        'communist party of india (marxist)': 'CPI(M)',
        'cpi(m)': 'CPI(M)',
        'communist party of india': 'CPI',
        'cpi': 'CPI',
        'dravida munnetra kazhagam': 'DMK',
        'dmk': 'DMK',
        'all india anna dravida munnetra kazhagam': 'AIADMK',
        'aiadmk': 'AIADMK',
        'all india trinamool congress': 'TMC',
        'trinamool congress': 'TMC',
        'tmc': 'TMC',
        'bahujan samaj party': 'BSP',
        'bsp': 'BSP',
        'janata dal (united)': 'JD(U)',
        'jd(u)': 'JD(U)',
        'janata dal (secular)': 'JD(S)',
        'jd(s)': 'JD(S)',
        'rashtriya janata dal': 'RJD',
        'rjd': 'RJD',
        'samajwadi party': 'SP',
        'sp': 'SP',
        'shiv sena': 'SS',
        'ss': 'SS',
        'nationalist congress party': 'NCP',
        'ncp': 'NCP',
        'shiromani akali dal': 'SAD',
        'sad': 'SAD',
        'lok janshakti party': 'LJP',
        'ljp': 'LJP',
        'jharkhand mukti morcha': 'JMM',
        'jmm': 'JMM',
        'aam aadmi party': 'AAP',
        'aap': 'AAP',
        'independent': 'IND',
        'ind': 'IND',
        'independents': 'IND',
        'all india forward bloc': 'AIFB',
        'all india majlis-e-ittehadul muslimeen': 'AIMIM',
        'aimim': 'AIMIM',
        'all india united democratic front': 'AIUDF',
        'aiudf': 'AIUDF',
        'asom gana parishad': 'AGP',
        'agp': 'AGP',
        'biju janata dal': 'BJD',
        'bjd': 'BJD',
        'jammu & kashmir national conference': 'JKNC',
        'jammu and kashmir national conference': 'JKNC',
        'jknc': 'JKNC',
        'jammu and kashmir peoples democratic party': 'JKPDP',
        'jkpdp': 'JKPDP',
        'rashtriya lok dal': 'RLD',
        'rld': 'RLD',
        'revolutionary socialist party': 'RSP',
        'rsp': 'RSP',
        'sikkim democratic front': 'SDF',
        'sdf': 'SDF',
        'sikkim krantikari morcha': 'SKM',
        'skm': 'SKM',
        'viduthalai chiruthaigal katchi': 'VCK',
        'vck': 'VCK',
        'none of the above': 'None of the Above',
        'nota': 'None of the Above',
    }
    
    if 'communist party of india (marxist' in p and 'leninist' in p:
        return 'CPI(ML)L'
    if 'cpi(ml)l' in p:
        return 'CPI(ML)L'
        
    if p in mapping:
        return mapping[p]
        
    if cleaned_name.isupper() and len(cleaned_name) <= 6:
        return cleaned_name
        
    return cleaned_name.title()

# Read the rawStacked CSV file using CP1252/latin1
with open(raw_file_path, 'r', encoding='latin1') as f:
    rows = list(csv.reader(f))

# Using a dict to merge duplicate records dynamically across multi-table states
all_records_dict = {}

def add_record(year, state, party, votes=None, pct=None, seats=None):
    key = (year, state, party)
    if key not in all_records_dict:
        all_records_dict[key] = {
            'Year': int(year),
            'State_UT': state,
            'Party_Alliance': party,
            'Votes_Received': votes,
            'Vote_Share_Percentage': pct,
            'Seats_Won': seats
        }
    else:
        est = all_records_dict[key]
        if est['Votes_Received'] is None:
            est['Votes_Received'] = votes
        if est['Vote_Share_Percentage'] is None:
            est['Vote_Share_Percentage'] = pct
        if est['Seats_Won'] is None:
            est['Seats_Won'] = seats

current_year = None
block_counter = 0

# Regex patterns for state header detection and 2009 fraction row parsing
state_pattern = re.compile(r'^([A-Za-z0-9\s&,-]+?)\s*\((\d+)\)$')
fraction_pattern = re.compile(r'^(\d+)\s*/\s*(\d+)\s*\(?([\d\.]+)%?\)?')

# UTs to skip in the 2004 general state summary table to avoid double-counting
uts_2004_to_skip = ['andaman and nicobar islands', 'chandigarh', 'national capital territory of delhi', 'lakshadweep']

idx = 0
while idx < len(rows):
    line_num = idx + 1
    r_clean = [normalize_string(c) for c in rows[idx]]
    
    if not any(r_clean):
        idx += 1
        continue
        
    first_val = r_clean[0]
    
    # Year block detection
    if first_val in ['2004', '2009', '2014', '2019', '2024']:
        block_counter += 1
        current_year = int(first_val)
        current_state = None
        current_state_seats = None
        col_indices = {}
        last_key = None
        idx += 1
        continue
        
    if current_year is None:
        idx += 1
        continue

    # Skip footnotes and general narrative lines
    if any(term in first_val.lower() for term in ['main article:', 'source:']):
        idx += 1
        continue

    # Block 2004: Parse state-by-state summary table (lines 7 to 41)
    if current_year == 2004 and line_num >= 7 and line_num <= 41:
        state_key = first_val.lower()
        if state_key in states_uts_map and state_key not in uts_2004_to_skip:
            state_canonical = states_uts_map[state_key]
            upa = clean_int(r_clean[2])
            nda = clean_int(r_clean[3])
            lf = clean_int(r_clean[4])
            others = clean_int(r_clean[5])
            
            alliances = [('UPA', upa), ('NDA', nda), ('Left Front', lf), ('Others', others)]
            for alliance_name, seats in alliances:
                if seats is not None and seats >= 0:
                    add_record(2004, state_canonical, alliance_name, seats=seats)
            idx += 1
            continue

    # State header detection (e.g. "Goa (2)" or "Uttar Pradesh (80)")
    match = state_pattern.match(first_val)
    if match:
        name_part = normalize_string(match.group(1)).lower()
        if name_part in states_uts_map:
            current_state = states_uts_map[name_part]
            current_state_seats = int(match.group(2))
            col_indices = {}
            last_key = None
            idx += 1
            continue

    # Parse tables inside active State section
    if current_state:
        # Check if header row by looking at cells stripped of brackets/notes
        r_clean_no_notes = [re.sub(r'\[.*?\]', '', c).strip().lower() for c in r_clean]
        
        # Robust exact match list for header cells (added 'parties' and 'party')
        header_keywords = ['party', 'parties', 'name of party', 'parties/ alliance', 'parties and coalitions', 'alliance/party', 'parties/alliance', 'alliance / party']
        is_header = any(cell in header_keywords for cell in r_clean_no_notes)
            
        if is_header:
            next_row = None
            if idx + 1 < len(rows):
                next_row = [normalize_string(c) for c in rows[idx+1]]
            
            # Combine if next row matches exact sub-header labels (prevents data row matching)
            next_row_no_notes = [re.sub(r'\[.*?\]', '', c).strip().lower() for c in next_row] if next_row else []
            sub_header_keywords = ['won', 'contested', 'votes', '%', '+/â', '+/-', 'changes', '±pp']
            
            if any(cell in sub_header_keywords for cell in next_row_no_notes):
                combined_headers = []
                for c1, c2 in zip(r_clean, next_row):
                    combined_headers.append((c1 + " " + c2).strip().lower())
                idx += 2  # skip the sub-header row too
            else:
                combined_headers = [c.lower() for c in r_clean]
                idx += 1
                
            combined_headers_clean = [re.sub(r'\[.*?\]', '', h).strip().lower() for h in combined_headers]
            
            # Detect key column indices
            col_indices = {}
            
            # Seats won index
            for c_idx, h in enumerate(combined_headers_clean):
                if 'seats won' in h or 'won' in h:
                    col_indices['seats'] = c_idx
                    break
            if 'seats' not in col_indices:
                for c_idx, h in enumerate(combined_headers_clean):
                    if 'seats' in h:
                        col_indices['seats'] = c_idx
                        break
            
            # Vote share index
            for c_idx, h in enumerate(combined_headers_clean):
                if '%' in h or 'vote share' in h:
                    col_indices['pct'] = c_idx
                    break
            if 'pct' not in col_indices:
                for c_idx, h in enumerate(combined_headers_clean):
                    if 'share' in h:
                        col_indices['pct'] = c_idx
                        break
                        
            # Votes received index
            for c_idx, h in enumerate(combined_headers_clean):
                if 'votes' in h and 'share' not in h and '%' not in h:
                    col_indices['votes'] = c_idx
                    break
            continue
            
        # Skip processing of data rows if headers have not been detected yet (ignores pre-header summary lists)
        if not col_indices:
            idx += 1
            continue

        # Skip total/turnout summary rows
        row_str = " | ".join(r_clean).lower()
        if any(term in row_str for term in ['total', 'valid votes', 'invalid/blank votes', 'turnout', 'votes cast', 'registered voters']):
            idx += 1
            continue
            
        # Find first non-empty cell in first 4 columns, ignoring dash placeholders
        first_non_empty = ""
        for cell in r_clean[:4]:
            if cell and cell not in ['-', '—', '–']:
                first_non_empty = cell
                break
                
        # Skip if row is a list of parties like "BJP (9)" or "INC (2)"
        if first_non_empty and re.match(r'^[A-Za-z0-9]+\s*\(\d+\)$', first_non_empty):
            idx += 1
            continue
            
        # Check if 2009 fraction row
        frac_match = fraction_pattern.match(first_val)
        if current_year == 2009 and frac_match:
            seats_won = int(frac_match.group(1))
            pct = float(frac_match.group(3))
            
            if last_key in all_records_dict:
                est = all_records_dict[last_key]
                est['Vote_Share_Percentage'] = pct
                if est['Seats_Won'] is None:
                    est['Seats_Won'] = seats_won
            idx += 1
            continue
            
        party_name = first_non_empty
        if not party_name:
            idx += 1
            continue
            
        # Standardize party name
        std_party = standardize_party(party_name)
        if std_party.lower() in ['total', 'registered voters']:
            idx += 1
            continue
            
        # Extract values using detected column mappings
        seats_won = None
        if 'seats' in col_indices and col_indices['seats'] < len(r_clean):
            seats_won = clean_int(r_clean[col_indices['seats']])
            
        pct = None
        if 'pct' in col_indices and col_indices['pct'] < len(r_clean):
            pct = clean_float(r_clean[col_indices['pct']])
            # If 2014 or 2019 has decimal fractions, convert them to percentages
            if current_year in [2014, 2019] and pct is not None and pct < 1.0:
                pct = pct * 100
                
        votes = None
        if 'votes' in col_indices and col_indices['votes'] < len(r_clean):
            votes = clean_int(r_clean[col_indices['votes']])
            
        # Merge duplicate record dynamically or create new
        add_record(current_year, current_state, std_party, votes=votes, pct=pct, seats=seats_won)
        last_key = (current_year, current_state, std_party)
        idx += 1
    else:
        idx += 1

# Convert list of dicts to DataFrame
all_records = list(all_records_dict.values())
df_final = pd.DataFrame(all_records)

# Ensure columns are sorted and clean types
df_final['Year'] = df_final['Year'].astype(int)
df_final['Seats_Won'] = df_final['Seats_Won'].astype('Int64') # Nullable Integer
df_final['Votes_Received'] = df_final['Votes_Received'].astype('Int64') # Nullable Integer

# Reorder columns
df_final = df_final[['Year', 'State_UT', 'Party_Alliance', 'Votes_Received', 'Vote_Share_Percentage', 'Seats_Won']]

print("\n--- Running Verification Assertions ---")

# 1. Year Ranges Check
assert set(df_final['Year'].unique()) == {2004, 2009, 2014, 2019, 2024}, "Invalid Year range!"

# 2. State/UT Canonical Check
invalid_states = [s for s in df_final['State_UT'].unique() if s not in states_uts_map.values()]
assert len(invalid_states) == 0, f"Found invalid state names: {invalid_states}"

# 3. Sum of Seats Won per Year Check (Lok Sabha total seats checks)
seat_sums = df_final.groupby('Year')['Seats_Won'].sum().to_dict()
print(f"Seat Sums per Year: {seat_sums}")

expected_seats = {
    2004: 543,
    2009: 519, # Matches raw source table contents (contains raw Wikipedia typo of 519)
    2014: 543,
    2019: 543,
    2024: 542  # Missing uncontested Surat seat which is not in the raw file
}

for yr, exp in expected_seats.items():
    assert seat_sums[yr] == exp, f"Year {yr} seat sum {seat_sums[yr]} does not match expected {exp}!"

# 4. Null value checks for keys
assert df_final['Year'].isnull().sum() == 0, "Null values found in 'Year'!"
assert df_final['State_UT'].isnull().sum() == 0, "Null values found in 'State_UT'!"
assert df_final['Party_Alliance'].isnull().sum() == 0, "Null values found in 'Party_Alliance'!"

print("All assertions passed successfully!")

# Save to cleaned file path as UTF-8
df_final.to_csv(output_file_path, index=False, encoding='utf-8')
print(f"Successfully exported clean tidy data to: {output_file_path}")
