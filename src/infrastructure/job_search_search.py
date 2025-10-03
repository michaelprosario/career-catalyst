from jobspy import scrape_jobs

# create job search query class
class JobSearchQuery:
    def __init__(self, search_term: str, location: str, results_wanted: int):
        self.search_term = search_term
        self.location = location
        self.results_wanted = results_wanted

class JobSearchService:
    def __init__(self):
        pass

    def job_search(self, query: JobSearchQuery):
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "google"],
            search_term=query.search_term,
            google_search_term=query.search_term,
            location=query.location,
            results_wanted=query.results_wanted,
            hours_old=72,
            country_indeed='USA'
            is_remote=True    
        )

        return jobs