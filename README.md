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


### Create jurisdictions and load vocabularies
```bash
fab load_terms
```
This will create the Ghana and Honduras jurisdictions, and load all the controlled
vocabularies defined form them from the respective github repos.


### Load sample fixtures
```bash
fab load_devfixtures
```
This will load some sample data from `data/fixtures/` that allows to "exercise"
the API endpoints.



## Local production-like setup (docker-compose on localhost)
```
fab dcbuild
fab dcup
```
This will spin up a docker container you can access at http://localhost:8000/

Use `fab dclogs:'-f'` to see what's going on.



## Production setup (docker-compose on remote host)

Check that the `PROUCTION_DOCKER_HOST` variable is set correctly in `fabfile.py`
then simply run:
```
fab prod dcbuild
fab prod dcup
```
This will run all docker commands agains the production docker host. After the 
migrations, data-loading, and fixtures loading steps complete (up to 5 mins),
the production server and all data will be available at https://rocdata.global/

Use `fab prod dclogs:'-f'` to see what's going on.

