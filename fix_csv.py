import pandas as pd

# Load your database
df = pd.read_csv("shl_full_database.csv")

def enrich_description(row):
    name = str(row['Assessment Name']).lower()
    desc = str(row['Description']).lower()
    
    # If the name has 'Java' but the description doesn't, add it.
    # We do this for common technical keywords.
    keywords = ['java', 'python', 'sql', 'c++', '.net', 'data science', 'javascript', 'automata']
    
    extra_context = []
    for k in keywords:
        if k in name and k not in desc:
            extra_context.append(k)
            
    if extra_context:
        return f"{row['Description']} Keywords: {' '.join(extra_context)}"
    return row['Description']

# Apply the fix
df['Description'] = df.apply(enrich_description, axis=1)

# Save it back (you can overwrite or save as new)
df.to_csv("shl_full_database.csv", index=False)
print("CSV Fixed! Descriptions now contain essential keywords from Test Names.")