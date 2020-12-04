# GROCCAD
Backend code for the Global Registry of Open Content and Curriculum Alignment Database (GROCCAD)

`standards-server` = a reusable Django app for serving the contents of a standards repo



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

