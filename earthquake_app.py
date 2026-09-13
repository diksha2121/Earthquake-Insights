
# # Step 1 Data Retreival

import requests
import pandas as pd
from datetime import datetime


#Load Data

all_records = []
start_year = datetime.now().year - 5   
end_year = datetime.now().year

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"


for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"

        params = {
            "format": "geojson",
            "starttime": start_date,
            "endtime": end_date,
            "minmagnitude": 3
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"⚠️ Failed for {start_date}: {response.text[:200]}")
            continue

        try:
            data = response.json()
        except Exception as e:
            print(f"⚠️ JSON error for {start_date}: {e}")
            continue

        for f in data["features"]:
            p = f["properties"]
            g = f["geometry"]["coordinates"]
            all_records.append({
                "id": f.get("id"),
                "time": pd.to_datetime(p.get("time"), unit="ms"),
                "updated": pd.to_datetime(p.get("updated"), unit="ms"),
                "latitude": g[1] if g else None,
                "longitude": g[0] if g else None,
                "depth_km": g[2] if g else None,
                "mag": p.get("mag"),
                "magType": p.get("magType"),
                "place": p.get("place"),
                "status": p.get("status"),
                "tsunami": p.get("tsunami"),
                "alert": p.get("alert"),
                "felt": p.get("felt"),
                "cdi": p.get("cdi"),
                "mmi": p.get("mmi"),
                "sig": p.get("sig"),
                "net": p.get("net"),
                "code": p.get("code"),
                "ids": p.get("ids"),
                "sources": p.get("sources"),
                "types": p.get("types"),
                "nst": p.get("nst"),
                "dmin": p.get("dmin"),
                "rms": p.get("rms"),
                "gap": p.get("gap"),
                "type": p.get("type")
            })

df = pd.DataFrame(all_records)
df.shape

df.sample()

df.columns

df.info()

df.isnull().sum()

raw_df = df.copy()
#raw_df.shape

df_clean = raw_df.copy()
 

df_clean['time'].dtype


df_clean['updated'].dtype

 
# 2. Clean Text Fields

#change alert columns values to lower if values exists
df_clean['alert'].head(), df_clean['alert'].tail()


df_clean['alert'].value_counts(dropna=False)


df_clean['alert'] = df_clean['alert'].str.lower()


#check if values are converted to lower case
df_clean[df_clean['alert'].notna()]['alert'].head()


#Ensure all string fields (magType, status, type, net, sources, types) are clean
string_columns = ["magType", "status", "type", "net", "sources", "types"]
string_columns


#Loop through the columns and inspect the raw data before cleaning
for col in string_columns:
    if col in df_clean.columns:
        print(f"Raw values for: {col}")
        print(f"Missing (null) count: {df_clean[col].isna().sum()}")
        print(f"Sample unique values: {df_clean[col].unique()[:10]}")  
        print("-" * 40)


# Loop through each column to strip whitespace and covert to lowercase
for col in string_columns:
    if col in df_clean.columns:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.lower()



# Loop through each column and inspect cleaned data
for col in string_columns:
    if col in df_clean.columns:
        print(f"Cleaned values for: {col}")
        print(f"Missing (null) count: {df_clean[col].isna().sum()}")
        print(f"Sample unique values: {df_clean[col].unique()[:10]}")
        print("-" * 40)

 
# # 3. Numeric Fields

 
# Inspect missing values and types before cleaning


# List of numeric columns from task
num_columns = ['mag', 'depth_km', 'nst', 'dmin', 'rms', 'gap', 'sig']

# Check initial missing counts and types
print("=== BEFORE CLEANING ===")
for col in num_columns:
    if col in df_clean.columns:
        print(f"{col:12} | Missing: {df_clean[col].isna().sum():6d} | Type: {df_clean[col].dtype}")


# Convert all specified columns to numeric
for col in num_columns:
    if col in df_clean.columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')


df[['mag', 'depth_km', 'nst', 'dmin', 'rms', 'gap', 'sig']].dtypes


# List of columns that have missing values
missing_columns = ['nst', 'dmin', 'rms', 'gap']

# Fill missing values with 0
for col in missing_columns:
    df_clean[col] = df_clean[col].fillna(0)


# Check missing counts and types after cleaning, filling
print("=== AFTER CLEANING ===")
for col in num_columns:
    if col in df_clean.columns:
        print(f"{col:12} | Missing: {df_clean[col].isna().sum():6d} | Type: {df_clean[col].dtype}")

 
# # 4. Add derived columns


df_clean['time'] = pd.to_datetime(df_clean['time'])
df_clean['time'].dtype


df_clean['year'] = df_clean['time'].dt.year
df_clean['month'] = df_clean['time'].dt.month
df_clean['day'] = df_clean['time'].dt.day
df_clean['day_of_week'] = df_clean['time'].dt.day_of_week


date_columns = ['time', 'year', 'month', 'day', 'day_of_week']


df_clean[date_columns].head()

 
# Create shallow/deep earthquake flag based on depth_km


df_clean['depth_km'].head()


# Function for binary depth classification
def get_depth_flag(depth):
    if depth <= 70:
        return 'Shallow'
    else:
        return 'Deep'

# Apply function to create new column depth category
df_clean['depth_category'] = df_clean['depth_km'].apply(get_depth_flag)


# Check value counts for Shallow vs Deep
print(df_clean['depth_category'].value_counts())

# Inspect depth_km alongside the new category
df_clean[['depth_km', 'depth_category']].head()

 
# Create strong/destructive flag based on mag thresholds


df_clean['mag'].head()


#Function for magnitude threshold classification
def get_mag_flag(mag):
  if mag >= 7.0:
    return 'Destructive'
  else:
    return 'Strong'


# Apply function to create new magnitude category column
df_clean['magnitude_category'] = df_clean['mag'].apply(get_mag_flag)


# Check value counts for Strong vs Destructive
print(df_clean['magnitude_category'].value_counts())

# Inspect mag alongside the new flag
df_clean[['mag', 'magnitude_category']].tail()

 
# Final Check


df_clean.shape


df_clean.info()


df_clean['tsunami'].head()


# Clean tsunami: fill missing with 0 and convert to integer
df_clean['tsunami'] = df_clean['tsunami'].fillna(0).astype(int)
df_clean['tsunami'].isnull().sum()


# Clean alert: lower case and fill missing with 'unknown'
df_clean['alert'] = df_clean['alert'].fillna('unknown').astype(str).str.lower()


df_clean['alert'].head()


df_clean[['felt', 'cdi', 'mmi']].head()


impact_cols = ['felt', 'cdi', 'mmi']


# Convert to numeric and fill missing values with 0
for col in impact_cols:
    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)


df_clean[['felt', 'cdi', 'mmi']].head()


df_clean[['felt', 'cdi', 'mmi']].isnull().sum()


df_clean.duplicated().sum()

## 5. Store Data in MySQL
from sqlalchemy import create_engine
 
DB_USER = "root"
DB_PASS = "YourSQLPassword"  
DB_HOST = "localhost"
DB_NAME = "earthquake_db"  


engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)


df_clean.to_sql(
    name="earthquakes",  
    con=engine,
    if_exists="replace",  
    index=False,  
    chunksize=10000  
)

print("Data inserted successfully!")


# # Running SQL Queries (Analyst Task)
 
# # Magnitude and Depth
 
# 1. Top 10 Strongest Earthquakes (mag)

query1 = """
    SELECT * 
    FROM earthquakes 
    ORDER BY mag DESC 
    LIMIT 10;"""
result1 = pd.read_sql(query1, engine)
print("Top 10 strongest earthquakes are:\n", result1)
 
# 2. Top 10 deepest earthquakes (depth_km)

query2 = """
    SELECT * 
    FROM earthquakes 
    ORDER BY depth_km DESC 
    LIMIT 10;"""
result2 = pd.read_sql(query2, engine)
print("The top 10 deepest earthquakes are:\n", result2)
 
# 3. Shallow earthquakes < 50 km and mag > 7.5

query3 = """
    SELECT * 
    FROM earthquakes 
    WHERE (depth_km < 50) and (mag > 7.5);"""
result3 = pd.read_sql(query3, engine)
print("Shallow earthquakes < 50km and mag>7.5 are:\n", result3)
 
# 4. Average depth per continent.

query4 = 'SELECT "Data is insufficient" as note;'
result4 = pd.read_sql(query4, engine)
print("Average depth per continent\n", result4)
 
# 5. Average magnitude per magnitude type (magType)


query5 = """
    SELECT magType, AVG(mag) AS avg_mag 
    FROM earthquakes 
    GROUP BY magType;"""
result5 = pd.read_sql(query5, engine)
print("Average magnitude per magnitude type:\n", result5)
 
# # Time Analysis
 
# 6. Year with most earthquakes

query6 = """
    SELECT year, COUNT(*) AS total_earthquakes 
    FROM earthquakes 
    GROUP BY year 
    ORDER BY total_earthquakes DESC 
    LIMIT 1;"""
result6 = pd.read_sql(query6, engine)
print("Year with most earthquakes is:\n", result6)
 
# 7. Month with highest number of earthquakes

query7 = """
    SELECT month, COUNT(*) AS total_earthquakes 
    FROM earthquakes 
    GROUP BY month 
    ORDER BY total_earthquakes DESC 
    LIMIT 1;"""
result7 = pd.read_sql(query7, engine)
print('Month with highest number of earthquakes is:\n', result7)
 
# 8. Day of week with most earthquakes

query8 = ("""
    SELECT day_of_week, COUNT(*) AS total_earthquakes
    FROM earthquakes 
    GROUP BY `day_of_week` 
    ORDER BY total_earthquakes DESC 
    LIMIT 1;""")
result8 = pd.read_sql(query8, engine)
print('Day of week with most earthquakes is:\n', result8)
 
# 9. Count of earthquakes per hour of day

query9 = """
    SELECT HOUR(time) AS hour, COUNT(*) AS earthquakes_per_hour
    FROM earthquakes
    GROUP BY hour
    ORDER BY hour ASC;"""
result9 = pd.read_sql(query9, engine)
print("Count of earthquakes per hour:\n", result9)
 
# 10.   Most active reporting network (net)

query10 = """
    SELECT net, count(*) AS total_count
    FROM earthquakes
    GROUP BY net
    ORDER BY total_count DESC
    LIMIT 1"""
result10 = pd.read_sql(query10, engine)
print("The most active reporting network(net) is:\n", result10)
 
# # Casualties & Economic Loss
 
# 11.  Top 5 places with highest casualties

query11 = """
    SELECT place, SUM(felt) AS casualties
    FROM earthquakes
    GROUP BY place
    ORDER BY casualties DESC
    LIMIT 5;"""
result11 = pd.read_sql(query11, engine)
print("Top 5 places with highest casualties are:\n", result11)
 
# 12.  Total estimated economic loss per continent

query12 = '''SELECT "Data is insufficient" AS note;'''
result12 = pd.read_sql(query12, engine)
print("Total estimated economic loss per continent", result12)
 
# 13.  Average economic loss by alert level

query13 = """
    SELECT alert, COUNT(*) AS count
    FROM earthquakes
    GROUP BY alert;"""
result13 = pd.read_sql(query13, engine)
print("Average economic loss by alert level:\n", result13)
 
# # Event Type & Quality Metrics
 
# 14.  Count of reviewed vs automatic earthquakes (status)

query14 = """
    SELECT status, COUNT(*) AS total_count
    FROM earthquakes
    GROUP BY status;"""
result14 = pd.read_sql(query14, engine)
print("Count of reviewed vs automatic earthquakes(status):\n", result14)
 
# 15.  Count by earthquake type (type)

query15 = """
    SELECT type, COUNT(*) AS total_count
    FROM earthquakes
    GROUP BY type;"""
result15 = pd.read_sql(query15, engine)
print("Count by earthquake type (type):\n", result15)
 
# 16.  Number of earthquakes by data type (types)

query16 = """
    SELECT types, COUNT(*) AS total_count
    FROM earthquakes
    GROUP BY types;"""
result16 = pd.read_sql(query16, engine)
print("Number of earthquakes by datatype (types):\n", result16)
 
# 17.  Average RMS and gap per continent

query17 = """SELECT 'Data not available' AS note;"""
result17 = pd.read_sql(query17, engine)
print("Average RMS and gap per continent:\n", result17)
 
# 18.  Events with high station coverage

query18 = """
    SELECT *
    FROM earthquakes
    WHERE nst > 50;"""
result18 = pd.read_sql(query18, engine)
print("Events with high station coverage are:\n", result18)
 
# # Tsunamis & Alerts 
 
# 19.  Number of tsunamis triggered per year

query19 = """
    SELECT year, SUM(tsunami) AS total_tsunamis
    FROM earthquakes
    GROUP BY year;"""
result19 = pd.read_sql(query19, engine)
print("Number of tsunamis triggered per year:\n", result19)
 
# 20.  Count earthquakes by alert levels (red, orange, etc.)

query20 = """
    SELECT alert, COUNT(*) AS earthquake_count
    FROM earthquakes
    GROUP BY alert;"""
result20 = pd.read_sql(query20, engine)
print("Total count of earthquakes by alert levels:\n", result20)
 
# # Seismic Pattern & Trends Analysis
 
# 21. The top 5 countries with the highest average magnitude of earthquakes in the past 5 years

query21 = """
    SELECT place, AVG(mag) AS avg_magnitude
    FROM earthquakes
    GROUP BY place
    ORDER BY avg_magnitude DESC
    LIMIT 5;"""
result21 = pd.read_sql(query21, engine)
print("The top 5 countries with the highest average magnitude of earthquakes in the past 5 years are:\n", result21)
 
# 22.Countries that have experienced both shallow and deep earthquakes within the same month

query22 = """
    SELECT place
    FROM earthquakes
    GROUP BY place, YEAR(time), MONTH(time)
    HAVING SUM(depth_km < 70) > 0 AND SUM(depth_km > 300) > 0;"""
result22 = pd.read_sql(query22, engine)
print("The places that have experienced both shallow and deep earthquakes within the same month are:\n", result22)
 
# 23.Computing the year-over-year growth rate in the total number of earthquakes globally

query23 = """
    SELECT 
        year,
        total,
        LAG(total) OVER (ORDER BY year) AS previous_year,
        ROUND(((total - LAG(total) OVER (ORDER BY year)) / LAG(total) OVER (ORDER BY year)) * 100, 2) AS growth_rate
    FROM (
        SELECT year, COUNT(*) AS total
        FROM earthquakes
        GROUP BY year
    ) AS yearly;
"""

result23 = pd.read_sql(query23, engine)
print("The year-over-year growth rate is:\n", result23)
 
# 24. List the 3 most seismically active regions by combining both frequency and average magnitude

query24 = """
    SELECT place, COUNT(*) AS frequency, AVG(mag) AS avg_mag, (COUNT(*) * AVG(mag)) AS seismic_score
    FROM earthquakes
    GROUP BY place
    ORDER BY seismic_score DESC
    LIMIT 3;"""
result24 = pd.read_sql(query24, engine)
print("The 3 most seismically active regions are:\n", result24)
 
# # Depth, Location & Distance-Based  Analysis
 
# 25. The average depth of earthquakes within ±5° latitude range of the equator for each country

query25 = """
    SELECT place, AVG(depth_km) AS avg_depth
    FROM earthquakes
    WHERE latitude BETWEEN -5 AND 5
    GROUP BY place;"""
result25 = pd.read_sql(query25, engine)
print("The average depth of earthquakes within ±5° latitude range of the equator for each country is:\n", result25)
 
# 26. Countries having the highest ratio of shallow to deep earthquakes

query26 = """
    SELECT place,
        SUM(depth_km < 70) AS shallow,
        SUM(depth_km > 300) AS deep,
        SUM(depth_km < 70) / NULLIF(SUM(depth_km > 300), 0) AS ratio
    FROM earthquakes
    GROUP BY place
    ORDER BY ratio DESC;"""
result26 = pd.read_sql(query26, engine)
print("Countries having the highest ratio of shallow to deep earthquakes\n:", result26)
 
# 27. The average magnitude difference between earthquakes with tsunami alerts and those without

query27 = """
    SELECT 
        (SELECT AVG(mag) FROM earthquakes WHERE tsunami = 1) AS tsunami_avg,
        (SELECT AVG(mag) FROM earthquakes WHERE tsunami = 0) AS no_tsunami_avg,
        (SELECT AVG(mag) FROM earthquakes WHERE tsunami = 1) -
        (SELECT AVG(mag) FROM earthquakes WHERE tsunami = 0) AS avg_mag_difference;"""
result27 = pd.read_sql(query27, engine)
print('The average magnitude difference between earthquakes with tsunami alerts and those without:\n', result27)
 
# 28. Using the gap and rms columns, identify events with the lowest data reliability (highest average error margins)

query28 = """
    SELECT * 
    FROM earthquakes
    ORDER BY gap DESC, rms DESC
    LIMIT 20;"""
result28 = pd.read_sql(query28, engine)
print("Events with lowest data reliability are:\n", result28)
 
# 29. Pairs of consecutive earthquakes (by time) that occurred within 50 km of each other and within 1 hour

query29 = """SELECT 'Data insufficient' AS note;"""
result29 = pd.read_sql(query29, engine)
print("Pairs of consecutive earthquakes (by time) that occurred within 50 km of each other and within 1 hour:\n", result29)
 
# 30.  The regions with the highest frequency of deep-focus earthquakes (depth > 300 km)

query30 = """
    SELECT place, COUNT(*) AS deep_count
    FROM earthquakes
    WHERE depth_km > 300
    GROUP BY place
    ORDER BY deep_count DESC;"""
result30 = pd.read_sql(query30, engine)
print("The regions with the highest frequency of deep-focus earthquakes (depth > 300 km):\n", result30)
 
# Mapping all the queries to a dictionary

queries = {
    "Task 1: Top 10 Strongest Earthquakes": query1,
    "Task 2: Top 10 Deepest Earthquakes": query2,
    "Task 3: Shallow earthquakes < 50 km and mag > 7.5": query3,
    "Task 4: Average depth per continent": query4,
    "Task 5: Average magnitude per magnitude type": query5,
    "Task 6: Year with the most earthquakes": query6,
    "Task 7: Month with the highest number of earthquakes": query7,
    "Task 8: Day of week with most earthquakes": query8,
    "Task 9: Count of earthquakes per hour of day": query9,
    "Task 10: Most active reporting network": query10,
    "Task 11: Top 5 Places with Highest Casualties": query11,
    "Task 12: Total estimated economic loss per continent": query12,
    "Task 13: Average Economic Loss by Alert Level": query13,
    "Task 14: Count of reviewed vs automatic earthquakess": query14,
    "Task 15: Count by earthquake type (type)": query15,
    "Task 16: Number of earthquakes by data type (types)": query16,
    "Task 17: Average RMS and gap per continent": query17,
    "Task 18: Events with high station coverage": query18,
    "Task 19: Number of tsunamis triggered per year": query19,
    "Task 20: Count earthquakes by alert levels": query20,
    "Task 21: The top 5 countries with the highest average magnitude of earthquakes": query21,
    "Task 22: Countries that have experienced both shallow and deep earthquakes within the same month": query22,
    "Task 23: Year-Over-Year Growth Rate": query23,
    "Task 24: Top 3 Most Seismically Active Regions": query24,
    "Task 25: The average depth of earthquakes within ±5° latitude range of the equator": query25,
    "Task 26: Countries having the highest ratio of shallow to deep earthquakes": query26,
    "Task 27: Average magnitude difference between earthquakes with tsunami alerts and those without.": query27,
    "Task 28: Events with the lowest data reliability": query28,
    "Task 29: Pairs of consecutive earthquakes (by time) that occurred within 50 km of each other and within 1 hour": query29,
    "Task 30: The regions with the highest frequency of deep-focus earthquakes": query30
}
 
# # Streamlit UI
import streamlit as st

st.title("Earthquake Data Analysis Dashboard")
st.write("Select any problem statement (1-30) to run the corresponding SQL query.")
task = st.selectbox("Choose Task Number", list(queries.keys()))

if st.button("Run Query"):
    selected_query = queries[task]
    df = pd.read_sql(str(selected_query), engine)
    st.subheader(f"Results for: {task}")
    st.dataframe(df, use_container_width=True)





