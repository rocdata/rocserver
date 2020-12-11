# Repository of Organized Curriculums Server

The backend code for the Repository of Organized Curriculums (ROC) consists of:

- `standards` and `standards-server`: a web application for browsing and publishing
  vocabularies, curriculum standards, standards crosswalks, and content correlations data.
- `data`: the "Global" controlled vocabularies used in the system
- `doc`: general info about the project (for developers)


## Install

```bash
virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
```


## Local dev setup
```
fab reset_and_migrate
./manage.py createsuperuser
```
The superuser account is needed to access the Admin panel http://localhost:8000/admin/


## Create jurisdictions and load vocabularies
```bash
fab load_terms
```
This will create the Ghana and Honduras jurisdictions, and load all the controlled
vocabularies defined form them from the respective github repos.


## Load sample fixtures

