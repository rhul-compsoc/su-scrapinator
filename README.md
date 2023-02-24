# su-scrapinator
The SU Scrapinator automates membership by scraping the SU.

## Setup
Install Xvfb (X virtual frame buffer) if you want to run in
a GUI-less environment.
```json
pip3 install -r requirements.txt
```

## Usage
Run the following to create members.json
```bash
python3 -u xxxxx@live.rhul.ac.uk -p password -l <url to push data to> -a <auth token for url> -h [status webhook url] -hn [status webhook name]
```

### Output
Output is saved in `members.json`

if SAVE\_FULL\_DATA is False

```json
[
  "21234",
  "3127318", ...
]
```

otherwise it will be in this form

```json
[
  {
    "name": "SMITH, John",
    "student-id": "123131231"
  }, ...
]
```
