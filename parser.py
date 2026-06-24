import re

try:
    import spacy
    SPACY_AVAILABLE = True
except Exception as e:
    SPACY_AVAILABLE = False
    print(f"SpaCy import failed: {e}")

def parse_resume(text: str) -> dict:
    """Parses resume text using SpaCy and Regex to extract information."""
    
    data = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "experience": "",
        "current_company": "",
        "degree": "",
        "university": "",
        "linkedin": "",
        "github": ""
    }
    
    # 1. Email extraction using Regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        data['email'] = emails[0]
        
    # 2. Phone extraction using Regex
    phone_pattern = r'\(?\b[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
    phones = re.findall(phone_pattern, text)
    if phones:
        data['phone'] = phones[0]
        
    # 3. Name extraction optimization
    # Often, the name is on the very first few non-empty lines of the resume.
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:5]:
        if line.lower() in ["resume", "cv", "curriculum vitae", "profile"]:
            continue
        # If line is 1-4 words and mostly alphabetical, it's likely the name
        words = line.split()
        if 1 <= len(words) <= 4 and all(re.match(r'^[A-Za-z\.\-]+$', w) for w in words):
            data['name'] = line.title()
            break
            
    # 3b. Fallback Name extraction using SpaCy
    if not data['name'] and SPACY_AVAILABLE:
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    data['name'] = ent.text
                    break
                    
            # 4. University extraction (SpaCy ORG)
            for ent in doc.ents:
                if ent.label_ == "ORG" and any(word in ent.text.lower() for word in ['university', 'college', 'institute']):
                    data['university'] = ent.text
                    break
                    
            # 5. Company extraction (SpaCy ORG as a fallback for current company)
            for ent in doc.ents:
                if ent.label_ == "ORG" and not any(word in ent.text.lower() for word in ['university', 'college', 'institute']):
                    data['current_company'] = ent.text
                    break
    
        except OSError:
            print("SpaCy model 'en_core_web_sm' not found. Ensure it is downloaded.")

    # 4b. Regex Fallback for University
    if not data['university']:
        university_keywords = ['university', 'college', 'institute', 'academy', 'school of']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in university_keywords):
                # Ensure the line isn't a long paragraph (typically school names are titles/headers)
                if len(line.strip()) < 80:
                    # Strip out common noise like dates (e.g., "2015-2019") or locations
                    clean_line = re.sub(r'\b(19|20)\d{2}\b', '', line).strip(" -|/,")
                    data['university'] = clean_line.title()
                    break

    # 4c. Deep Regex Fallback for University (Handles messy OCR without newlines)
    if not data['university']:
        # Look for up to 3 words before and after the keyword
        uni_pattern = r'((?:\b[A-Za-z]+\b\s+){0,3}(?:University|College|Institute|Academy)(?:\s+\b[A-Za-z]+\b){0,3})'
        match = re.search(uni_pattern, text, re.IGNORECASE)
        if match:
            clean_match = re.sub(r'\b(19|20)\d{2}\b', '', match.group(1)).strip(" -|/,")
            data['university'] = clean_match.title()

    # 6. Basic Link extraction
    linkedin_pattern = r'(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+)'
    github_pattern = r'(https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+)'
    
    linkedin = re.search(linkedin_pattern, text)
    if linkedin:
        data['linkedin'] = linkedin.group(0)
        
    github = re.search(github_pattern, text)
    if github:
        data['github'] = github.group(0)
        
    # 7. Basic Skills Keyword Matching
    # Define a predefined list of skills to look for
    common_skills = ['python', 'java', 'c++', 'c#', 'javascript', 'html', 'css', 'sql', 'machine learning', 'data analysis', 'react', 'node.js', 'aws', 'docker', 'kubernetes', 'git', 'excel', 'project management', 'agile']
    found_skills = []
    text_lower = text.lower()
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.append(skill.title())
    data['skills'] = found_skills
    
    # 8. Basic Degree Matching (Handles messy OCR variations like B. Tech, BTech, Ph.D, PhD)
    degree_patterns = {
        'B.Tech': r'\bB\.?\s*Tech\b',
        'B.Sc': r'\bB\.?\s*Sc\b',
        'B.A': r'\bB\.?\s*A\b',
        'B.E': r'\bB\.?\s*E\b',
        'M.Tech': r'\bM\.?\s*Tech\b',
        'M.Sc': r'\bM\.?\s*Sc\b',
        'M.A': r'\bM\.?\s*A\b',
        'MBA': r'\bMBA\b',
        'Ph.D': r'\bPh\.?\s*D\b',
        'Bachelor': r'\bBachelors?\b',
        'Master': r'\bMasters?\b'
    }
    for degree_name, pattern in degree_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            data['degree'] = degree_name
            break

    # 9. Experience matching (looking for e.g., "5 years")
    exp_pattern = r'(\d+)\+?\s*years?'
    exp_match = re.search(exp_pattern, text_lower)
    if exp_match:
        data['experience'] = f"{exp_match.group(1)} Years"
        
    return data
