Purpose
-------

Repository contains script to report results from XML file to TestRail. Only tests from XML will be added to run.

Requirements
------------

- python 2.7
- [testrail-python](https://github.com/travispavek/testrail-python)

Settings
--------

**Your XML file structure**

Only test group name and status of test case are significant to reporter for now:
```xml
<xml>
  <testsuite errors='0' failures='0' skip='0' tests='7'>
    <testcase name='your_test_group_is_here'/>
    <testcase name='your_another_test_group_is_here'/>
  </testsuite>
</xml>
```

By default `0` status is mapped to `passed` on TestRail, `1` is mapped to `failed` test.

**Your TestRail settings**

Required environment variables:

```bash
export TESTRAIL_USER_EMAIL=
export TESTRAIL_USER_KEY=
export TESTRAIL_URL=
export TESTRAIL_PROJECT=    # name of the project where to find tests
export TESTRAIL_MILESTONE=  # is used for creating of plans and runs
export TESTRAIL_SUITE=      # name of the suite where to get tests for the run
export TESTRAIL_PLAN=       # name of the plan where to collect the run
```

Optional environment variables:

```bash
export XML_PATH=      # path to your XML file with test results; default is 'nosetests.xml'
export TESTRAIL_RUN=  # name of the run; by default is equal to test suite
```

Start
-----

To run script which will add test results to TestRail, you may use:
```bash
python reporter.py
```

Logic of work
-------------

Script finds the suite in your TestRail project, then gets all cases from this suite and filters them to consider only those tests, which test groups are presented in your XML file. Then it finds test plan (or creates it if test plan whith specified name doesn't exist) and finds or creates test run within the plan. Finally, it adds test results for the run.

