#pipPandas Practice — CSV Exploration & Missing Values (Only topics we learned)


#PART 1 — Load the CSV
#1) Load the CSV file into a DataFrame named df.

import pandas as pd

df = pd.read_csv(r"C:\Users\User\Desktop\ספיר\אישי\קורס דאטה אנליסט אנליזה\Northwind project\Northwind Profitability & Growth Analysis using Python\Olympic.csv")  
print(df.head())

#PART 2 — Rename columns 
#1) Rename the column "Sex" to "Gender".

df2 = df.rename(columns={"Sex": "Gender"})
print(df2.head())
#2) Rename the column "Name" to "AthleteName".

df2 = df2.rename(columns={"Name": "AthleteName"})
print(df2.head())
print('------------')

#PART 3 — Detect missing values
#1) Create a boolean Series named missing_weight that marks rows where Weight is missing.

df_missing_weight = df['Weight'].isnull()
print(df_missing_weight)
print('------------')

#2) Create a DataFrame df_missing_weight that contains only the rows where Weight is missing.

df_missing_weight = df[df_missing_weight]
print(df_missing_weight)
print('------------')

#3) Create a boolean Series named has_height that marks rows where Height is NOT missing.

df_has_height = df['Height'].notnull()
print(df_has_height)
print('------------')

#4) Create a DataFrame df_has_height that contains only the rows where Height is NOT missing.

df_has_height = df[df_has_height]
print(df_has_height)
print('------------')

#PART 4 — Medal filtering 
#In the "Medal" column, many rows are missing (no medal), and some rows have values like Gold/Silver/Bronze.
#1) Create a DataFrame medalists that includes only rows where Medal is NOT missing.

df_medalists = df[df['Medal'].notnull()]
print(df_medalists)
print('------------')

#2) Create a DataFrame non_medalists that includes only rows where Medal IS missing.

df_non_medalists = df[df['Medal'].isnull()]
print(df_non_medalists)
print('------------')

#PART 5 — Fill missing values 
#1) Replace missing values in Medal with the string "No Medal".

df['Medal']= df['Medal'].fillna("No Medal")    
print(df.head())
print('------------')

#2) Replace missing values in Weight with 0.

df['Weight'].fillna(0)  
print(df.head())
print('------------')


#PART 6 — Drop missing values 
#1) Create a DataFrame df_clean where you drop rows that are missing Age OR Gender.

df_clean = df.dropna(subset=['Age', 'Gender'])
print(df_clean.head())
print('------------')

#2) Check that df_clean has no missing values in Age and Gender.

print("Missing values in Age:", df_clean['Age'].isnull().sum())
print("Missing values in Gender:", df_clean['Gender'].isnull().sum()) 
print('------------')

#PART 7 — Wrap-up workflow
#Create a DataFrame df_ready that does ALL of the following:
#- Renames Sex -> Gender and Name -> AthleteName
#- Fills missing Medal with "No Medal"
#- Fills missing Weight with 0
#- Drops rows missing Age or Gender

df_ready = df.rename(columns={"Sex": "Gender", "Name": "AthleteName"})
df_ready['Medal'] = df_ready['Medal'].fillna("No Medal")
df_ready['Weight'] = df_ready['Weight'].fillna(0)
df_ready = df_ready.dropna(subset=['Age', 'Gender'])

print(df_ready.head())