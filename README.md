# Mode Python Importers

This is a simple Python client demonstrating how to import CSV files from your
computer or the web into [Mode](https://modeanalytics.com).

## Setup

1. Clone this repository and `cd` into it
2. Copy `config.template.yml` to `config.yml`
3. Add your Mode username and password to `config.yml`
   ([documentation](http://developer.modeanalytics.com/#page:authentication))
4. Run `python setup.py install`

## Usage

Once you've set things up, you can use a single line command to import data
into Mode. All commands should begin with

```
$ python mode-python-importers/import.py --csv=[FILE]
```

In this case, `FILE` is either:

* the path to a local CSV file on your computer, or
* the URL of a CSV file on the web

Optional flags:

- `--name=TABLE_NAME` the name of the table to be imported
- `--desc="DESCRIPTION"` a brief public description of the table
- `--no-prompt` infer table name from the file name or URL instead of
  prompting. (This will be ignored if `--name` is present. If this flag is
  set and you don't provide a description, your table's description will be
  left blank.)
- `--replace` if the table name provided or inferred already exists, the 
  table will be replaced with your chosen CSV. Note that table replacements
  cannot be undone, so this flag is not recommended if the table name is
  inferred.

## Example Usage

```
$ python mode-python-importers/import.py \
  --csv=https://raw.githubusercontent.com/fivethirtyeight/data/master/infrastructure-jobs/payroll-states.csv

>>> Enter table name: python_api_example
>>> Enter table description: This is an example of a table imported using the Python API client.
>>> Retrieving CSV.
>>> CSV successfully retrieved.
>>> Displaying formatted column names and types:

---------------  ----------------  ------------  ------  ----  ------  -------
new_column_name  orig_column_name  guessed_type  string  date  number  boolean

state_code       state_code        number        --      --    100.0%  --
state_name       state_name        string        100.0%  --    --      --
---------------  ----------------  ------------  ------  ----  ------  -------

>>> Creating upload.
>>> Upload created.
>>> Creating table at https://modeanalytics.com/api/benn/tables
>>> Beginning table creation.
>>> Check status at https://modeanalytics.com/api/benn/tables/python_api_example/imports/7ff7a57c9d9b
>>> Current status: enqueued
>>> Current status: enqueued
>>> Current status: succeeded
>>> Import successful
>>> Table location: https://modeanalytics.com/benn/tables/python_api_example
```
