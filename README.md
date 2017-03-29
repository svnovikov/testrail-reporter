Purpose
-------

Repository contains scripts to report results in XML format to TestRail. Reporter gets info about tests from XML file and adds to TestRail run only these tests.

Requirements
------------

- python 2.7
- [testrail library for python](https://github.com/travispavek/testrail-python)

Settings
--------

**Your XML file structure**

Only test group (name) and status of test case is relevant for now. So here is an example:
```xml
<xml>
  <testsuite errors='0' failures='0' skip='0' tests='7'>
    <testcase name='your_test_group_is_here' status='0' />
    <testcase name='your_another_test_group_is_here' status='0' />
  </testsuite>
</xml>
```

If status is '0', then the test will be marked as passed, if status is '1', then test will be marked as failed.

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
export XML_PATH=      # path to your XML file with test results
export TESTRAIL_RUN=  # name of the run; by default is equal to test suite
```

Start
-----

Use `python reporter.py` to add test results to TestRail.
