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

```bash
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

```bash
fab dcbuild
fab dcup
```

This will spin up a docker container you can access at http://localhost:8000/

Use `fab dclogs:'-f'` to see what's going on.



## Production setup (docker-compose on remote host)

Check that the `PROUCTION_DOCKER_HOST` variable is set correctly in `fabfile.py`
then simply run:

```bash
fab prod dcbuild
fab prod dcup
```

This will run all docker commands agains the production docker host. After the 
migrations, data-loading, and fixtures loading steps complete (up to 5 mins),
the production server and all data will be available at https://rocdata.global/

Use `fab prod dclogs:'-f'` to see what's going on. The re-deploy takes a few minutes,
during which the website will be unavailable (showing the "Bad Gateway" error message).



## Static webpages
The `rocserver` homepage and other static info pages are maintained as google docs.
Each of the pages corresponds to one google document in the google drive folder
called [Website](https://drive.google.com/drive/u/0/folders/1PrR0zGaYRsXOsXDojjSWVyDosufCY1C-)
(accessible only to the maintainers of the rocdata.global server).

- To modify the text that appears on the website, simply change the corresponding
  google document and the changes will be reflected on the website a few minutes later.
  No technical expertise is required for this most common case—just WYSIWYG-edit the google doc.

Other types of changes to the website require technical expertise, editing HTML,
and re-deploying the server code (`fab prod dcbuild; fab prod dcup`):

- To modify the website footer, change the HTML template in `standards/templates/website/base.html`.
- To change the website header (navigation links), edit the template
  `website/templates/website/fragments/navbar.html`.
- To add a new page to the website, follow the steps:
  1. Create a new google document in the [Website](https://drive.google.com/drive/u/0/folders/1PrR0zGaYRsXOsXDojjSWVyDosufCY1C-) folder
  2. Use the format page option to set the paper size to 11'x17' portrait mode
  3. Set the style of the google document to match the current website styling:
     - Font: Helvetica Neue
     - Normal Text (paragraphs): 13pt, 1.2 line spacing
  4. Use the File > Publish to the web menu, then choose Embed tab, and obtain
     the `embed_url` string for the document (this is URL where the HTML of the
     google document is available on google's servers).
  5. Add a new entry to `WEBSITE_PAGES_GOOGLE_DOCS` dict in the file `standards-server/settings.py`
     using the desired page name as the key. For example to add a new page `/pages/foo`
     the key should be `foo`.
  6. (optional) Add the new page to the nav menu `website/templates/website/fragments/navbar.html`
     or link to the new page from one of the existing website pages.
