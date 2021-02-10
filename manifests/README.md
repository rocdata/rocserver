Data manifests
==============
A "data manifest" is a YAML config file that specifies one or more ROC datasets
that are to be loaded into or exported from a ROC server instance.


Example manifests
-----------------
- `roconstants.manifest.yml`: bases ControlledVocabulary and Term data required
  for ROC server operation (Global jurisdiciton)
- `reserverdev.manifest.yml`: small samples of each data type (jurisdictions,
  standards, content, content correlations, standards crosswalks)
- `rocdata.global.manifest.yml`: declarative specification of all data published
  in the ROC data referece implementation server hosted at https://rocdata.global 
- `your-org.manifest.yml`: your organisations' "data presets" in case you want
  to run your own instance of the `rocserver` app


When the primary goal is to export ROC data (use case of `rocserver` as a
static-site generator) you can either export all data in all formats (default)
or use an "exporter manifest" to specify a specific subset of data like this:

- `standards-sample.manifest.yml`: example exporter manifest for the "sample"
  jurisdiction the output of which is saved to the github repor rocdata/standards-sample
  and published at githubpages.io/rocdata/standards-sample 
  (and optionally fronted with w3id "permalink" redirects
  w3id.org/rocdata/sample --> githubpages.io/rocdata/standards-sample/rocdata/sample )



