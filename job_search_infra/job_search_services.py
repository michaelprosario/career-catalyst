import csv
from jobspy import scrape_jobs

def get_job_list_markdown(jobs_df) -> str:
    """
    Convert a jobs DataFrame to markdown format.
    
    Args:
        jobs_df: DataFrame with columns: title, job_url, company, location, date_posted, is_remote, description
    
    Returns:
        str: Markdown formatted string of job listings
    """
    if jobs_df.empty:
        return "No jobs found."
    
    markdown_content = []
    markdown_content.append("# Job Search Results\n")
    
    for index, job in jobs_df.iterrows():
        # Create job title as link if URL exists
        if job.get('job_url'):
            title_link = f"[{job['title']}]({job['job_url']})"
        else:
            title_link = job['title']
        
        markdown_content.append(f"## {title_link}")
        markdown_content.append(f"**Company:** {job['company']}")
        markdown_content.append(f"**Location:** {job['location']}")
        markdown_content.append(f"**JobLink:** {job['job_url']}")
        
        # Handle remote indicator
        if job.get('is_remote'):
            markdown_content.append("**Remote:** Yes")
        
        if job.get('date_posted'):
            markdown_content.append(f"**Date Posted:** {job['date_posted']}")
        
        # Add description if available
        #if job.get('description'):
        #    markdown_content.append(f"**Description:**\n{job['description']}")
        
        markdown_content.append("---\n")  # Separator between jobs
    
    return "\n".join(markdown_content)

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