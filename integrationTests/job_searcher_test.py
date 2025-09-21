
import os
import sys


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from job_search_services import job_search_services

jobs = job_search_services.job_search("software tester", "Tampa, FL", 30 )
#print(f"Found {len(jobs)} jobs")
#print(jobs)

## write current job opportunities to csv file in my_data
jobs.to_csv("../my_data/jobs.csv", index=False)

