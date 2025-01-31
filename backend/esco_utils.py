import pandas as pd

def load_esco_skills(file_path="skills_en.csv"):
    """
    Load the ESCO skills dataset and extract skill names.
    """
    # Load the CSV file
    df = pd.read_csv('/home/abdullah/Desktop/resume-parser-job-matcher/backend/data/ESCO dataset - v1.2.0 - classification - en - csv')
    
    # Extract the 'preferredLabel' column (skill names)
    skills = set(df['preferredLabel'].str.lower().dropna().unique())
    
    return skills

def load_esco_skills_with_synonyms(file_path="skills.csv"):
    """
    Load the ESCO skills dataset with synonyms.
    """
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Create a mapping of preferred labels to alternative labels
    skill_mapping = {}
    for _, row in df.iterrows():
        preferred_label = row['preferredLabel'].lower()
        alt_labels = [label.lower() for label in row['altLabels'].split(';')] if pd.notna(row['altLabels']) else []
        skill_mapping[preferred_label] = alt_labels
    
    return skill_mapping