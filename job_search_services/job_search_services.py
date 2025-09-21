import csv
from jobspy import scrape_jobs

def job_search(search_term, location, results_wanted):
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "google"],
        search_term=search_term,
        google_search_term=search_term,
        location=location,
        results_wanted=results_wanted,
        hours_old=72,
        country_indeed='USA'    
    )

    return jobs

#print(f"Found {len(jobs)} jobs")
#print(jobs.head())
#jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel