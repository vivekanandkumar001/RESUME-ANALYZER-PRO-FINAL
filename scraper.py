# scraper.py
import requests
import xml.etree.ElementTree as ET
import json
import os
import re
from html import unescape

# --- RSS FEED URL ---
# !!! जरूरी: यहाँ अपनी असली RSS फ़ीड URL डालें !!!
RSS_FEED_URL = 'https://rss.app/feeds/tFMWbVUElCPJMM1b.xml' # <-- यहाँ बदलें (Example URL)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_keywords(description):
    text = description.lower()
    keywords = set()
    common_skills = [ # इस लिस्ट को और बढ़ाएं
        'python', 'react', 'javascript', 'java', 'sql', 'aws', 'docker', 'machine learning',
        'data analysis', 'api', 'django', 'flask', 'node', 'html', 'css', 'ai',
        'deep learning', 'nlp', 'pytorch', 'tensorflow', 'cloud', 'azure', 'gcp',
        'kubernetes', 'git', 'rest', 'graphql', 'typescript', 'vue', 'angular',
        'c++', 'c#', 'ruby', 'php', 'seo', 'sem', 'google analytics'
    ]
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            keywords.add(skill.title())
    return list(keywords)[:7]

def load_existing_jobs(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if not content: return []
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Existing {filepath} corrupted, ignoring.")
            return []
        except Exception as e:
            print(f"⚠️ Warning: Could not read existing {filepath}: {e}")
            return []
    return []

def parse_rss_feed():
    if 'YOUR_RSS_FEED_URL_HERE' in RSS_FEED_URL: # Safety check agar default value reh gayi ho
        print("❌ Error: Please update the RSS_FEED_URL in scraper.py.")
        return

    print(f"Fetching RSS feed from: {RSS_FEED_URL}")
    try:
        response = requests.get(RSS_FEED_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        print("Feed fetched successfully.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Could not fetch RSS feed. {e}")
        # Exit with error code so GitHub Action knows it failed potentially
        exit(1)


    newly_scraped_jobs = []
    try:
        xml_content = response.content
        root = ET.fromstring(xml_content)
        print("Parsing XML...")
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        print(f"Found {len(items)} items in the feed.")

        for item in items:
            title_elem = item.find('title')
            description_elem = item.find('description') or item.find('summary')
            # Link bhi nikalne ki koshish karein
            link_elem = item.find('link')
            link = link_elem.text.strip() if link_elem is not None and link_elem.text is not None else None


            if title_elem is not None and title_elem.text is not None and \
               description_elem is not None and description_elem.text is not None:
                title = title_elem.text.strip()
                description_raw = description_elem.text.strip()
                description_text = re.sub(r'<[^>]+>', '', description_raw)
                description_text = unescape(description_text)
                description_text = re.sub(r'\s+', ' ', description_text).strip()
                description = " ".join(description_text.split()[:100]) + ("..." if len(description_text.split()) > 100 else "")
                keywords = extract_keywords(title + " " + description)

                if keywords:
                    job_data = {
                        "title": title,
                        "description": description,
                        "keywords": keywords
                    }
                    if link: # Agar link mila hai toh add karein
                        job_data["link"] = link
                    newly_scraped_jobs.append(job_data)
            # else:
            #     print("Skipping item: missing title/description.")

    except ET.ParseError as e:
        print(f"❌ Error: Could not parse XML. {e}")
        exit(1) # Exit with error code
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        exit(1) # Exit with error code

    output_dir = "data_resume"
    output_path = os.path.join(output_dir, "jobs.json")
    os.makedirs(output_dir, exist_ok=True)

    existing_jobs = load_existing_jobs(output_path)
    # Use title + first part of description for uniqueness to handle similar titles
    existing_keys = { (job.get('title',"").lower().strip(), job.get('description',"")[:50].lower().strip()) for job in existing_jobs }

    added_count = 0
    jobs_to_save = list(existing_jobs) # Start with existing jobs

    for new_job in newly_scraped_jobs:
        job_key = (new_job.get('title',"").lower().strip(), new_job.get('description',"")[:50].lower().strip())
        if job_key not in existing_keys and new_job.get('description'):
            jobs_to_save.append(new_job)
            existing_keys.add(job_key)
            added_count += 1

    print(f"\nFetched {len(newly_scraped_jobs)} potential jobs, Added {added_count} new unique jobs.")

    # Save the combined list
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(jobs_to_save, f, indent=4, ensure_ascii=False)
        print(f"✅ Success! Total {len(jobs_to_save)} unique jobs saved to {output_path}.")
    except Exception as e:
        print(f"❌ Error: Could not save file. {e}")
        exit(1) # Exit with error code

if __name__ == "__main__":
    parse_rss_feed()