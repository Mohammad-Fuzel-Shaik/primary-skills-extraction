import spacy
import re
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def is_primary_skill(term):
    non_skills = {
        'test', 'automation', 'quality', 'team', 'tools', 'ability',
        'experience', 'year', 'years', 'using', 'with', 'and', 'the',
        'of', 'in', 'to', 'for', 'a', 'or', 'other', 'knowledge',
        'proficiency', 'familiarity', 'skill', 'skills', 'job', 'title',
        'description', 'engineer', 'developer', 'analyst', 'strong',
        'communication', 'problem', 'solving', 'design', 'execute',
        'develop', 'looking', 'collaborate', 'identify', 'track',
        'improve', 'ensure', 'plan', 'coverage', 'requirement',
        'responsibility', 'preferred', 'methodology', 'methodologies'
    }

    term_lower = term.lower()
    if (len(term) < 3 or
        term_lower in non_skills or
        any(ns in term_lower.split() for ns in non_skills) or
        re.search(r'(ing|tion|ment|ship|ness)\b', term_lower)):
        return False
    return True

def extract_primary_skills_from_complete_jd(complete_jd):
    req_section = re.split(r"(?i)requirements:", complete_jd)[-1]
    req_section = re.split(r"(?i)preferred:|nice to have:", req_section)[0]

    doc = nlp(req_section)
    skills = []

    
    skill_phrases = [
        r'with ([\w\s/]+)',
        r'in ([\w\s/]+)',
        r'proficiency in ([\w\s/]+)',
        r'experience with ([\w\s/]+)',
        r'knowledge of ([\w\s/]+)'
    ]
    for pattern in skill_phrases:
        matches = re.finditer(pattern, req_section, re.IGNORECASE)
        for match in matches:
            skill = match.group(1).strip()
            for subskill in re.split(r'[,/]|\bor\b', skill):
                subskill = subskill.strip()
                if is_primary_skill(subskill):
                    skills.append(subskill.title())

    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and is_primary_skill(token.text):
            skills.append(token.text.title())


    bullets = re.findall(r'(?:•|\d+\.|-)\s*([^\n.;]+)', req_section)
    for bullet in bullets:
        bullet_doc = nlp(bullet)
        for token in bullet_doc:
            if token.pos_ in ['NOUN', 'PROPN'] and is_primary_skill(token.text):
                skills.append(token.text.title())


    skill_counts = Counter(skills)
    return [skill for skill, _ in skill_counts.most_common(15)]

complete_jd = """
Job Title: Test Automation Engineer
Job Description:
We are looking for a Test Automation Engineer with 2 years of experience (Playwright)
Responsibilities:
Develop and execute automated tests using Playwright.
Collaborate with teams to design test plans.
Identify and track bugs.
Improve test automation frameworks.
Ensure test coverage and quality.
Requirements:
2+ years of test automation experience with Playwright.
Knowledge of web and API testing.
Proficiency in JavaScript, TypeScript, or Python.
Experience with Git and CI/CD tools.
Strong problem-solving and communication skills.
Preferred:
Experience with other automation tools.
Knowledge of performance and security testing.
Familiarity with Agile/Scrum methodologies.
"""

primary_skills = extract_primary_skills_from_complete_jd(complete_jd)
print("🎯 Primary Skills:")
for skill in primary_skills:
    print(f"- {skill}")
