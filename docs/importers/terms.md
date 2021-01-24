Controlled vocabulary terms
===========================

Can be loaded using individual commands like:

    ./manage.py createjurisdiction --name Global --display_name "Global Terms" --language "en"
    ./manage.py loadterms data/terms/ContentRelationKinds.yml

but too numerous...

Instead load using fab command:

    fab load_terms

which will create all relevant jurisdictions and load all controlled vocabularies
from the corresponding GitHub repositories. See `fabfile.py` source code for details.



Examples terms YAML data 
------------------------

 - [Global:ContentStandardRelationKinds.yml](https://github.com/rocdata/rocserver/blob/main/data/terms/ContentStandardRelationKinds.yml)
 - [Ghana:GradeLevels.yml](https://github.com/rocdata/standards-ghana/blob/main/terms/GradeLevels.yml)



Create controlled vocabularies and terms
----------------------------------------

 1. Create GitHub repo where you will store the data.
 2. Add folder called `terms/` in the repo.
 3. Add YAML data file in format similar to the examples shown above.
 
You can now use the command `./manage.py loadterms <URL>` to import the controlled 
vocabulary data into your local `rocserver` instance, where `<URL>` is the full
path of the "raw" file hosted on GitHub.



Uploading controlled vocabularies and terms using a spreadsheet
---------------------------------------------------------------

 1. Prepare data using the spreadsheet template TODOLINK
 2. Upload data using the form at TODOLINK
 3. Verify and review uploaded data was correctly parsed and validated.
    Go back to step 1 if something doesn't look right.
 4. Change status to `publicdraft` so other users will be able to view the data.

