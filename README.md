# groccad
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


## Load global vocabularies

```
./manage.py loadterms data/terms/TermRelationKinds.yml
```



## Load sample fixtures



Admin http://localhost:8000/admin/

