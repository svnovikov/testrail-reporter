import os
import xml.etree.ElementTree as xml

import requests.packages.urllib3
from testrail import TestRail

requests.packages.urllib3.disable_warnings()

tr_project = os.environ.get('TESTRAIL_PROJECT')
tr_milestone = os.environ.get('TESTRAIL_MILESTONE')

tr_suite = os.environ.get('TESTRAIL_SUITE')
tr_testplan = os.environ.get('TESTRAIL_PLAN')
tr_testrun = os.environ.get('TESTRAIL_RUN', tr_suite)

xml_path = os.environ.get('XML_PATH', 'nosetests.xml')


def parse_xml():
    tree = xml.parse(xml_path)
    root = tree.getroot()

    tcases = {}  # map test group to test result

    for tc in root.iter('testcase'):
        tc_attrs = tc.attrib
        status = tc.getchildren()
        if not status:
            status = {'passed': ''}
        elif 'skipped' in status[0].__str__():
            status = {'skipped': status[0].text}
        else:
            status = {'failed': status[0].text}
        tcases[tc_attrs['name']] = status

    return tcases


def get_test_group(tr_case):
    return tr_case.raw_data().get('custom_test_group', '')


class Reporter:
    def __init__(self, project_name, milestone_name, suite_name, plan_name,
                 run_name, cases_xml):
        self.project = None
        self.tr_project = self.init_project(project_name)
        self.milestone = self.find_milestone(milestone_name)

        self.suite = self.find_suite(suite_name)
        self.cases = self.tr_project.cases(self.suite)

        self.plan = self.find_plan(plan_name)
        self.run = self.find_or_create_test_run(run_name)

	self.tests = list(self.tr_project.tests(self.run))
	self.filter_tests(cases_xml)
        self.add_results(cases_xml)

    def init_project(self, project_name):
        project = TestRail()
        for prj in project.projects():
            if prj.name == project_name:
                project.set_project_id(prj.id)
                self.project = prj
                return project
        raise Exception('Project "{}" is not found.'.format(project_name))

    def find_suite(self, suite_name):
        for suite in self.tr_project.suites():
            if suite.name == suite_name:
                return suite
        raise Exception('The test suite {} is not found'.format(suite_name))

    def find_milestone(self, milestone_name):
        for m in self.tr_project.milestones():
            if m.name == milestone_name:
                return m
        raise Exception('Milestone {} is not found'.format(milestone_name))

    def filter_tests(self, cases_xml):
        """Leave only those tests which are in xml."""
        testrail_tests = [get_test_group(test) for test in self.tests]
        xml_cases = cases_xml.keys()
        tests = filter(lambda x: get_test_group(x) in xml_cases, self.tests)
        cases_gr = filter(lambda x: x in xml_cases, testrail_tests)
        print('NOTE: the following test cases dont have result and will be '
              'marked as "untested":\n{}'
              .format(set(testrail_tests) - set(cases_gr)))
        print('NOTE: the following test cases are new for the test suite {!r}!'
              ' Their results will be ignored:\n{}'
              .format(tr_suite, set(xml_cases) - set(cases_gr)))
        print('NOTE: the following test cases have results: \n{}'
              .format(set(cases_gr)))
        self.tests = tests

    def find_plan(self, plan_name):
        """Find existing TestRail Plan."""
        plans = self.tr_project.plans()
        for plan in plans:
            if plan.name == plan_name:
                print('Plan {} is found'.format(plan_name))
                return plan
        raise Exception('Plan {} is not found'.format(plan_name))

    def find_or_create_test_run(self, run_name):
        """Find existing or create new TestRail Run."""
        runs = []
        for r in self.plan.entries:
            runs += r.runs

        for r in runs:
            if r.name == run_name:
                run = r
                print 'Run {} is found'.format(run_name)
                break
        else:
            entry = {
                'name': run_name,
                'suite_id': self.suite.id,
                'include_all': False,
                'case_ids': [_.id for _ in self.cases],
                'project_id': self.project.id,
                'milestone_id': self.milestone.id,
                'plan_id': self.plan.id
            }
            run = self.plan.api.add_plan_entry(entry)
            run = self.plan.api.get_run(run['id'])
            print 'Run {} is created'.format(run_name)
        return run

    def add_results(self, cases_xml):

        for test in self.tests:
            test_group = get_test_group(test)
            status, comment = cases_xml.get(get_test_group(test)).items()[0]
            if self.tr_project.status(status) is None:
                print('NOTE: Unknown status {!r} for test cases {!r}. Ignoring'
                      .format(status, test_group))
                continue

            result = self.tr_project.result()
            result.test = test
            result.comment = comment
            result.status = self.tr_project.status(status)
            print('Adding result for test case {!r} : {!r}'
                  .format(test_group, status))

            self.tr_project.add(result)


if __name__ == '__main__':
    tc = parse_xml()
    p = Reporter(tr_project, tr_milestone, tr_suite, tr_testplan,
                 tr_testrun, tc)
    print('[TestRun URL] {}'.format(p.run.url))
