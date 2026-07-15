import os
import csv
import re
import pandas as pd
import numpy as np

# Define directories and paths
project_dir = r"c:\Users\mohdh\OneDrive\Desktop\Projects\Election Campaign Analysis"
raw_path = os.path.join(project_dir, "data", "raw", "result_by_party.csv")
cleaned_dir = os.path.join(project_dir, "data", "cleaned")
cleaned_path = os.path.join(cleaned_dir, "result_by_party_cleaned.csv")

def normalize_string(val):
    if not val:
        return ""
    # Strip whitespace
    s = val.strip()
    # Replace non-breaking space with regular space
    s = s.replace('\xa0', ' ')
    # Normalize dashes/hyphens
    s = s.replace('–', '-').replace('—', '-')
    # Normalize smart quotes to regular quotes
    s = s.replace('’', "'").replace('‘', "'")
    # Normalize multiple spaces to a single space
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

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

def standardize_party(party_name):
    p_norm = normalize_string(party_name)
    if not p_norm:
        return ""
    
    p = p_norm.lower()
    
    # Extensive mapping list derived from clean_data.py and party names list
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
        'bharat rashtra samiths': 'BRS', # typo variation
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
        'vacant': 'Vacant',
        'nominated anglo-indian': 'Nominated Anglo-Indian',
        'nominated anglo-indians': 'Nominated Anglo-Indian',
    }
    
    if 'communist party of india (marxist' in p and 'leninist' in p:
        return 'CPI(ML)L'
    if 'cpi(ml)l' in p:
        return 'CPI(ML)L'
        
    if p in mapping:
        return mapping[p]
    
    # Capitalize acronyms
    if p_norm.isupper() and len(p_norm) <= 6:
        return p_norm
        
    return p_norm.title()

def clean_data():
    print(f"Reading raw data from: {raw_path}")
    
    # Check if raw file exists
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw CSV file not found at: {raw_path}")
        
    with open(raw_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    all_cleaned_records = []
    
    current_block_year = None
    block_counter = 0
    current_alliance = None
    
    for idx, r in enumerate(rows):
        line_num = idx + 1
        r_clean = [normalize_string(cell) for cell in r]
        
        # Check if empty row
        if not any(r_clean):
            continue
            
        first_val = r_clean[0]
        
        # 1. Detect Year Header Block
        if first_val.isdigit() and len(first_val) == 4:
            block_counter += 1
            # Correcting the year block assignments based on raw data inspection
            if block_counter == 1:
                current_block_year = 2004
            elif block_counter == 2:
                current_block_year = 2014  # Raw header says '2009', but it's 2014
            elif block_counter == 3:
                current_block_year = 2019
            elif block_counter == 4:
                current_block_year = 2024
            elif block_counter == 5:
                current_block_year = 2009  # Raw header says '2009', and it is indeed 2009
                
            current_alliance = None  # Reset alliance on new block
            print(f"Detected block {block_counter}: Year Header {first_val} -> Map to Year {current_block_year}")
            continue
            
        # 2. Skip column header rows
        # Headers contain exact terms like 'party', 'party/alliance'
        if first_val.lower() in ['party', 'party/alliance'] or 'votes' in [c.lower() for c in r_clean] or '%' in r_clean:
            continue
            
        # 3. Skip overall summary rows (Total, Valid votes, turnout, source, etc.)
        row_str = " | ".join(r_clean).lower()
        if any(term in row_str for term in ['valid votes', 'invalid/blank votes', 'total votes', 'registered voters/turnout', 'source:']):
            continue
            
        # Also skip overall total rows
        # (For non-2024 blocks, Col 0 is 'Total'. For 2024 block, Col 0 is 'Total' or Col 1 is 'Total')
        if first_val.lower() == 'total':
            continue
        if len(r_clean) > 1 and r_clean[1].lower() == 'total':
            continue
            
        # 4. Extract data based on block type
        party = None
        alliance = None
        votes = None
        pct = None
        seats = None
        
        if current_block_year != 2024:
            # Check for shifted NOTA row
            # Format in 2014/2019 NOTA: Party name is either 'None of the Above' (2014) or empty (2019)
            # but votes and % are shifted to Index 2 and Index 3. Index 4 has a control char '\x13'.
            is_nota = False
            if first_val == 'None of the Above' and len(r_clean) > 2 and r_clean[2] and not r_clean[1]:
                is_nota = True
            elif not first_val and len(r_clean) > 2 and r_clean[2] and not r_clean[1]:
                is_nota = True
                
            if is_nota:
                party = 'None of the Above'
                votes = clean_int(r_clean[2])
                pct = clean_float(r_clean[3])
                seats = 0
            # Check for shifted Nominated or Vacant row
            # Format: Col 0 is 'Nominated Anglo-Indian' or 'Vacant', Col 1-3 are empty, Col 4 has seat count.
            elif first_val in ['Nominated Anglo-Indian', 'Nominated Anglo-Indians', 'Vacant'] and not r_clean[1] and not r_clean[2] and not r_clean[3] and len(r_clean) > 4 and r_clean[4]:
                party = first_val
                votes = None
                pct = None
                seats = clean_int(r_clean[4])
            else:
                # Regular non-2024 data row
                # Index 0: Party, Index 1: Votes, Index 2: %, Index 3: Seats
                party = first_val
                votes = clean_int(r_clean[1]) if len(r_clean) > 1 else None
                pct = clean_float(r_clean[2]) if len(r_clean) > 2 else None
                seats = clean_int(r_clean[3]) if len(r_clean) > 3 else None
        else:
            # 2024 Block logic
            # Format: Col 0 (Alliance), Col 2 (Party), Col 3 (Votes), Col 4 (%), Col 5 (Seats)
            # Special check for shifted NOTA row:
            # Col 0-3 empty, Col 4 has votes, Col 5 has %, Col 6 has control char '\x13'.
            if not first_val and len(r_clean) > 5 and r_clean[4] and not r_clean[2] and not r_clean[3]:
                party = 'None of the Above'
                votes = clean_int(r_clean[4])
                pct = clean_float(r_clean[5])
                seats = 0
                alliance = None
            else:
                # Track alliance context
                # If Col 0 is a known alliance, update current_alliance
                if first_val in ['NDA', 'INDIA']:
                    current_alliance = first_val
                elif first_val:
                    # If Col 0 is populated but is not NDA/INDIA, and Col 2 is empty, 
                    # then Col 0 is actually the Party name (a standalone party).
                    # If Col 2 is not empty, then Col 0 is some other alliance.
                    if not r_clean[2]:
                        current_alliance = None
                    else:
                        current_alliance = first_val
                
                # Check for alliance total row (skip it)
                # Format: Col 1 is 'Total'
                if len(r_clean) > 1 and r_clean[1] == 'Total':
                    continue
                    
                party = r_clean[2] if r_clean[2] else first_val
                alliance = current_alliance
                votes = clean_int(r_clean[3]) if len(r_clean) > 3 else None
                pct = clean_float(r_clean[4]) if len(r_clean) > 4 else None
                seats = clean_int(r_clean[5]) if len(r_clean) > 5 else None
                
        # Clean and standardize party name
        std_party = standardize_party(party)
        
        # If party name is still blank or represents an empty row, skip it
        if not std_party:
            continue
            
        record = {
            'Year': current_block_year,
            'Party': std_party,
            'Votes': votes,
            'Percentage': pct,
            'Seats': seats
        }
        all_cleaned_records.append(record)
        
    # Convert to DataFrame
    df = pd.DataFrame(all_cleaned_records)
    
    # Save output
    os.makedirs(cleaned_dir, exist_ok=True)
    df.to_csv(cleaned_path, index=False, encoding='utf-8')
    print(f"Successfully wrote {len(df)} cleaned records to: {cleaned_path}")
    return df

if __name__ == "__main__":
    clean_data()
