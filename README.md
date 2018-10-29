# TalentLMS API Wrapper

Python client library for [Talent LMS API](https://www.talentlms.com/pages/docs/TalentLMS-API-Documentation.pdf)

### Installation

This module is not submitted to PyPI. You can install direct from github with `pip install git+git://github.com/govex/talentpy` or by cloning the repo and running: `pip install -e .` from within the directory.


### Usage

~~~
from talentpy import Talent

apikey="yourTalentLMSkey"
domain="domain"

t = Talent(apikey=apikey, domain=domain)
~~~

Replace `yourTalentLMSkey` with your api key and `domain` with the part that says "domain" in https://domain.talentlms.com/. Strong suggestion: store your api key as an environmental variable and use `os.environ.get('apikey')` (which is the argument default). Never save an apikey in your code. 

To get all your courses:

`all_courses = t.get_courses()`

See the [talentpy](https://github.com/govex/talentpy/blob/master/talentpy/talentpy.py) module for the rest of the implemented methods. 

If your needed API call does not have a method, please submit a pull request!
