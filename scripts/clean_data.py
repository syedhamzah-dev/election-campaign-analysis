import os
import csv
import re
import pandas as pd
import numpy as np

raw_dir = r"c:\Users\mohdh\OneDrive\Desktop\Projects\Election Campaign Analysis\data1\raw\constituency-wise"
output_dir = r"c:\Users\mohdh\OneDrive\Desktop\Projects\Election Campaign Analysis\data1\cleaned"
output_path = os.path.join(output_dir, "constituency.csv")

years = [2004, 2009, 2014, 2019, 2024]
encodings = {
    2004: 'utf-8',
    2009: 'cp1252',
    2014: 'utf-8',
    2019: 'cp1252',
    2024: 'utf-8'
}

def standardize_state(state_name):
    if not state_name:
        return ""
    # Standardize & to and
    s = state_name.replace('&', 'and')
    # Standardize spaces
    s = re.sub(r'\s+', ' ', s)
    s = s.strip()
    
    # Dictionary of standard state names
    state_map = {
        'nct of delhi': 'Delhi',
        'delhi': 'Delhi',
        'dadra and nagar haveli': 'Dadra and Nagar Haveli',
        'daman and diu': 'Daman and Diu',
        'dadra and nagar haveli and daman and diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'andaman and nicobar islands': 'Andaman and Nicobar Islands',
        'andhra pradesh': 'Andhra Pradesh',
        'arunachal pradesh': 'Arunachal Pradesh',
        'assam': 'Assam',
        'bihar': 'Bihar',
        'chandigarh': 'Chandigarh',
        'chhattisgarh': 'Chhattisgarh',
        'goa': 'Goa',
        'gujarat': 'Gujarat',
        'haryana': 'Haryana',
        'himachal pradesh': 'Himachal Pradesh',
        'jammu and kashmir': 'Jammu and Kashmir',
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
        'puducherry': 'Puducherry',
        'punjab': 'Punjab',
        'rajasthan': 'Rajasthan',
        'sikkim': 'Sikkim',
        'tamil nadu': 'Tamil Nadu',
        'telangana': 'Telangana',
        'tripura': 'Tripura',
        'status': 'Status',
        'uttar pradesh': 'Uttar Pradesh',
        'uttarakhand': 'Uttarakhand',
        'west bengal': 'West Bengal',
        'ladakh': 'Ladakh'
    }
    
    s_key = s.lower()
    if s_key in state_map:
        return state_map[s_key]
    return s.title()

def standardize_constituency(name):
    if not name:
        return ""
    # Replace & with and
    name = name.replace('&', 'and')
    # Normalize dashes/hyphens
    name = name.replace('–', '-').replace('—', '-')
    # Remove spaces around hyphens
    name = re.sub(r'\s*-\s*', '-', name)
    # Normalize multiple spaces
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    
    # Specific corrections for spelling and truncations
    corrections = {
        'darrang-udalgu': 'Darrang-Udalguri',
        'bhiwani-mahendraga': 'Bhiwani-Mahendragarh',
        'karauli-dholp': 'Karauli-Dholpur',
        'tonk-sawai madhop': 'Tonk-Sawai Madhopur',
        'jhalawar-bar': 'Jhalawar-Baran',
        'viluppuram': 'Villupuram',
        'thoothukkudi': 'Thoothukudi',
        'gauhati': 'Guwahati',
        'nowgong': 'Nagaon',
        'nainital-udhamsingh nag': 'Nainital-Udhamsingh Nagar',
        'nainital-udhamsin': 'Nainital-Udhamsingh Nagar',
    }
    
    name_lower = name.lower()
    
    # Check for 2009 encoding corruptions and substring matches
    if 'bhiwani' in name_lower:
        if any(x in name_lower for x in ['mahe', 'ï¿½', '-', '–']):
            return 'Bhiwani-Mahendragarh'
        else:
            return 'Bhiwani'
    if 'nainital' in name_lower:
        if any(x in name_lower for x in ['udh', 'ï¿½', '-', '–']):
            return 'Nainital-Udhamsingh Nagar'
        else:
            return 'Nainital'
    if 'tonk' in name_lower:
        if any(x in name_lower for x in ['sawai', 'ï¿½', '-', '–']):
            return 'Tonk-Sawai Madhopur'
        else:
            return 'Tonk'
    if 'jhalawar' in name_lower:
        if any(x in name_lower for x in ['bar', 'ï¿½', '-', '–']):
            return 'Jhalawar-Baran'
        else:
            return 'Jhalawar'
    if 'karauli' in name_lower:
        return 'Karauli-Dholpur'
        
    for pattern, replacement in corrections.items():
        if name_lower.startswith(pattern):
            return replacement
            
    return name.title()

def standardize_type(ctype):
    if not ctype:
        return "GEN"
    c = ctype.strip().upper()
    c = c.replace('(', '').replace(')', '')
    if c in ['GEN', 'SC', 'ST']:
        return c
    return c

def standardize_party(party_name):
    if not party_name:
        return ""
    p = party_name.strip().lower()
    p = re.sub(r'\s+', ' ', p)
    
    # Standardized the party names
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
        'TMC'
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
    }
    
    if 'communist party of india (marxist' in p and 'leninist' in p:
        return 'CPI(ML)L'
    if 'cpi(ml)l' in p:
        return 'CPI(ML)L'
        
    if p in mapping:
        return mapping[p]
    
    if party_name.isupper() and len(party_name) <= 6:
        return party_name
        
    return party_name.title()

def clean_int(val):
    if not val:
        return None
    val_clean = re.sub(r'[^\d]', '', val.strip())
    if not val_clean:
        return None
    return int(val_clean)

def clean_float(val):
    if not val:
        return None
    val_clean = re.sub(r'[^\d\.]', '', val.strip())
    if not val_clean:
        return None
    return float(val_clean)

def parse_votes_pct(val):
    if not val:
        return None, None
    val = val.strip()
    match = re.match(r'^([\d,]+)\s*\(([\d\.]+)%\)$', val)
    if match:
        votes = clean_int(match.group(1))
        pct = clean_float(match.group(2))
        return votes, pct
    else:
        return clean_int(val), None

def clean_name(val):
    if not val:
        return None
    val = re.sub(r'\s+', ' ', val.strip())
    if val == '' or val == '-':
        return None
    return val

# Main execution pipeline
print("Starting campaign data cleaning and consolidation...")

all_records = []
type_lookup = {} # populated from 2019

for year in years:
    path = os.path.join(raw_dir, f"{year}.csv")
    print(f"Reading {year}.csv using encoding {encodings[year]}...")
    
    with open(path, 'r', encoding=encodings[year], errors='replace') as f:
        reader = csv.reader(f)
        header1 = next(reader)
        header2 = next(reader)
        
        state = None
        for row_idx, r in enumerate(reader, start=3):
            if not r:
                continue
            
            # Forward-fill state (Col 0)
            s_cell = r[0].strip()
            if s_cell:
                state = s_cell
            
            if not state:
                raise ValueError(f"State column is empty and could not be filled at line {row_idx} in {year}.csv")
                
            state_std = standardize_state(state)
            const_no = int(r[1].strip())
            const_name = standardize_constituency(r[2])
            
            # Initializing target fields
            ctype = "GEN"
            winner_cand = None
            winner_party = None
            winner_votes = None
            winner_pct = None
            runner_cand = None
            runner_party = None
            runner_votes = None
            runner_pct = None
            margin_votes = None
            
            # Parse based on year layout
            if year in [2004, 2009, 2014]:
                ctype = standardize_type(r[3])
                winner_cand = clean_name(r[4])
                winner_party = standardize_party(r[6])
                winner_votes = clean_int(r[7])
                
                runner_cand = clean_name(r[8])
                runner_party = standardize_party(r[10])
                runner_votes = clean_int(r[11])
                
                margin_votes = clean_int(r[12])
                
            elif year == 2019:
                ctype = standardize_type(r[3])
                winner_cand = clean_name(r[4])
                winner_party = standardize_party(r[5])
                winner_votes, winner_pct = parse_votes_pct(r[6])
                
                runner_cand = clean_name(r[7])
                runner_party = standardize_party(r[8])
                runner_votes, runner_pct = parse_votes_pct(r[9])
                
                margin_votes = clean_int(r[10])
                
                # Build type lookup
                lookup_key = (state_std.lower(), const_name.lower())
                type_lookup[lookup_key] = ctype
                type_lookup[const_name.lower()] = ctype
                
            elif year == 2024:
                winner_cand = clean_name(r[3])
                winner_party = standardize_party(r[5])
                winner_pct = clean_float(r[6])
                winner_votes = clean_int(r[7])
                
                runner_cand = clean_name(r[8])
                runner_party = standardize_party(r[10])
                runner_votes = clean_int(r[11])
                runner_pct = clean_float(r[12])
                
                margin_votes = clean_int(r[13])
                
                # Handle 2024 type resolution
                if state_std.lower() == 'assam':
                    # Post-2023 Assam Delimitation reservations
                    # Kokrajhar (No. 1) -> ST, Diphu (No. 6) -> ST, Karimganj (No. 7) -> SC, others -> GEN
                    if const_no == 1:
                        ctype = "ST"
                    elif const_no == 6:
                        ctype = "ST"
                    elif const_no == 7:
                        ctype = "SC"
                    else:
                        ctype = "GEN"
                else:
                    # Look up from 2019 cleaned data
                    lookup_key = (state_std.lower(), const_name.lower())
                    if lookup_key in type_lookup:
                        ctype = type_lookup[lookup_key]
                    elif const_name.lower() in type_lookup:
                        ctype = type_lookup[const_name.lower()]
                    else:
                        ctype = "GEN" # default fallback
                        
            # Record dictionary
            record = {
                'Year': year,
                'State': state_std,
                'Constituency_No': const_no,
                'Constituency_Name': const_name,
                'Constituency_Type': ctype,
                'Winner_Candidate': winner_cand,
                'Winner_Party': winner_party,
                'Winner_Votes': winner_votes,
                'Winner_Percentage': winner_pct,
                'Runner_up_Candidate': runner_cand,
                'Runner_up_Party': runner_party,
                'Runner_up_Votes': runner_votes,
                'Runner_up_Percentage': runner_pct,
                'Margin_Votes': margin_votes
            }
            all_records.append(record)

# Convert to DataFrame
df_final = pd.DataFrame(all_records)
print(f"Total processed records: {len(df_final)}")

# Save to destination
os.makedirs(output_dir, exist_ok=True)
df_final.to_csv(output_path, index=False, encoding='utf-8')
print(f"Cleaned dataset written successfully to: {output_path}")
