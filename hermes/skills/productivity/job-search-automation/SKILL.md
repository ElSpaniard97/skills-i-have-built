---
name: job-search-automation
description: Automated job search pipeline — analyze candidate profile, search curated job boards, filter by skills/keywords, and generate tailored recommendations with application strategy.
tags: [jobs, career, resume, linkedin, github, recruiting, automation]
---

# Job Search Automation

Systematic pipeline for finding relevant job opportunities based on a candidate's GitHub profile, resume, certifications, and experience.

## When to Use

- User asks to find/search for jobs
- User shares a resume or GitHub profile and wants job recommendations
- User mentions "job hunting", "looking for work", "career search"

## Discovery Process

### 1. Profile Analysis (First Priority)

If the user has a GitHub resume repository or profile, analyze it first:

```bash
# List user's repos to find resume/portfolio
gh repo list USERNAME --limit 50 --json name,description,url

# Clone resume repo if found
gh repo clone USERNAME/resume-repo

# Read key files
search_files(pattern="*", target="files", path="/tmp/resume-repo")
read_file("README.md")
read_file("index.html")  # if portfolio site
```

**Extract:**
- Current role and company
- Years of experience
- Technical skills (languages, frameworks, tools)
- Certifications (CompTIA, AWS, etc.)
- Domain expertise (DevOps, AI/ML, security, web)
- Projects and GitHub contributions

### 2. Job Source Strategy (Trial-Tested Approaches)

#### ✅ **Primary: Curated GitHub Job Boards (WORKS BEST)**

```bash
cd /tmp
git clone --depth 1 https://github.com/SimplifyJobs/New-Grad-Positions.git
# OR for experienced roles:
git clone --depth 1 https://github.com/SimplifyJobs/Summer2025-Internships.git
```

**Why this works:**
- Updated daily by community
- Links verified and working
- Includes company, role, location, posting date
- Markdown table format = easy to parse

#### ❌ **Avoid: Direct LinkedIn/Indeed Scraping**
- Rate limiting and anti-bot measures
- HTML structure changes frequently
- Requires authentication
- Legal/ToS concerns

#### 🤷 **Limited: GitHub Jobs API**
- Many "new grad" repos are curated manually (see above)
- GitHub native Jobs feature deprecated in 2021

### 3. Filtering and Ranking

Use Python with regex to extract and filter job listings:

```python
import re

with open('/tmp/New-Grad-Positions/README.md', 'r') as f:
    content = f.read()

# Extract job entries (company, role, location, link, age)
job_pattern = r'<tr>\s*<td><strong><a[^>]*>(.*?)</a></strong></td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>.*?href="([^"]*)".*?</td>\s*<td>(.*?)</td>'
matches = re.findall(job_pattern, content, re.DOTALL)

# Define relevant keywords based on user profile
keywords = ['Software Engineer', 'DevOps', 'AI', 'Infrastructure', 'Platform', 
            'Backend', 'Security', 'Cloud']  # Customize per user

jobs = []
for company, role, location, link, age in matches[:100]:
    # Clean HTML tags
    company = re.sub(r'<[^>]*>', '', company).strip()
    role = re.sub(r'<[^>]*>', '', role).strip()
    location = re.sub(r'</?br>|<[^>]*>', ', ', location).strip()
    age = age.strip()
    
    # Filter by keywords
    if any(kw.lower() in role.lower() for kw in keywords):
        jobs.append({
            'company': company,
            'role': role,
            'location': location,
            'link': link.split('?')[0],  # Remove tracking params
            'age': age
        })
```

### 4. Generate Recommendations

Create a structured markdown report with:

1. **Profile Summary** (extracted from their resume/GitHub)
2. **Top Matches** (10-20 best-fit roles, grouped by category):
   - AI/ML Engineering (if relevant)
   - Infrastructure/Platform/DevOps
   - General Software Engineering
   - Security (if CompTIA Security+ or similar)
3. **Application Priority Tiers**:
   - Priority 1: Perfect skill match + posted recently
   - Priority 2: Strong teams with growth potential
4. **Competitive Advantages** (what makes them stand out)
5. **Resume Talking Points** (how to frame their experience)

### 5. Delivery Format

```markdown
## 🎯 Job Search Results for [Name]

### 📊 Your Key Strengths:
- [Extract from profile]

## 🔥 TOP RECOMMENDED ROLES

### [Category 1 - e.g., "AI-Focused Positions"]
**1. Company — Role Title**
   - 📍 Location
   - 🔗 [Direct link, tracking params removed]
   - ⏰ Posted: [age]
   - ✅ Why it matches: [Specific reason]

[Repeat for top 10-20 roles across 2-4 categories]

## 🎯 APPLICATION STRATEGY
[Actionable recommendations]
```

## Pitfalls

1. **Don't guess at profile details** — always read their actual resume/GitHub if available
2. **Remove tracking parameters from job URLs** — cleaner links, better user experience
3. **Don't scrape LinkedIn/Indeed directly** — use curated repos instead
4. **Age matters** — prioritize roles posted in last 7 days
5. **FAANG indicators** — many repos mark big tech with 🔥 emoji in company name
6. **Citizenship/sponsorship markers** — 🇺🇸 = U.S. citizenship required, 🛂 = no sponsorship

## Follow-Up Offers

After delivering results, offer to:
1. Generate tailored cover letters for specific positions
2. Review/optimize resume for ATS systems
3. Set up a cron job to monitor the job board repo daily
4. Create a job application tracker in their workspace

## Example Flow

```bash
# 1. Analyze profile
gh repo clone ElSpaniard97/ezekiel-correa-resume
read_file("/tmp/ezekiel-correa-resume/README.md")
read_file("/tmp/ezekiel-correa-resume/index.html")

# 2. Clone job board
cd /tmp && git clone --depth 1 https://github.com/SimplifyJobs/New-Grad-Positions.git

# 3. Filter with Python (use execute_code or terminal heredoc)
terminal(command='python3 << EOF
import re
with open("/tmp/New-Grad-Positions/README.md") as f:
    content = f.read()
# [filtering logic as shown above]
EOF')

# 4. Format and deliver recommendations
```

## Related Skills

- `github-pages-portfolio-site` — if user needs to create/improve their online resume
- `github-repo-management` — for setting up job application tracker repos
- `recurring-report-cron` — to monitor job boards daily and auto-post new matches
