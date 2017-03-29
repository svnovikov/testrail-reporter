import os

import requests.packages.urllib3
from testrail import *

from parsexml import parse_xml

requests.packages.urllib3.disable_warnings()

tr_project = os.environ.get('TESTRAIL_PROJECT')
tr_milestone = os.environ.get('TESTRAIL_MILESTONE')

tr_suite = os.environ.get('TESTRAIL_SUITE')
tr_testplan = os.environ.get('TESTRAIL_PLAN')
tr_testrun = os.environ.get('TESTRAIL_RUN', tr_suite)


def get_test_group(case):
    return case.raw_data().get('custom_test_group', '')


class Reporter:
    def __init__(self, project_name, milestone_name, suite_name, plan_name,
                 run_name, cases_xml):
        self.project_id = None
        self.tr_project = None
        self.project = self.init_project(project_name)
        self.milestone = self.find_milestone(milestone_name)

        self.suite = self.find_suite(suite_name)
        self.cases = self.tr_project.cases(self.suite)
        self.filter_cases(cases_xml)

        self.plan = self.get_or_create_plan(plan_name)
        self.run = self.get_or_create_test_run(run_name)

        self.statuses = {
            '0': self.tr_project.status('passed'),
            '1': self.tr_project.status('failed')
        }

        self.add_results(cases_xml)

    def init_project(self, project_name):
        self.tr_project = TestRail()

        for p in self.tr_project.projects():
            if p.name == project_name:
                self.tr_project.set_project_id(p.id)
                self.project_id = p.id
                return p

        raise Exception('Project "{}" not found.'.format(project_name))

    def find_suite(self, suite_name):
        for s in self.tr_project.suites():
            if s.name == suite_name:
                return s

    def find_milestone(self, milestone_name):
        for m in self.tr_project.milestones():
            if m.name == milestone_name:
                return m
        raise Exception('Milestone {} not found'.format(milestone_name))

    def filter_cases(self, cases_xml):
        """Leave only those tests which are in xml."""
        self.cases = [case for case in self.cases
                      if get_test_group(case) in cases_xml.keys()]
        return self

    def get_or_create_plan(self, plan_name):
        """Get existing or create new TestRail Plan."""
        plans = self.tr_project.plans()
        for p in plans:
            if p.name == plan_name:
                plan = p
                print 'Plan {} is found'.format(plan_name)
                break
        else:
            plan = self.tr_project.plan()
            plan.name = plan_name
            plan.milestone = self.milestone
            plan.project = self.project
            plan = self.tr_project.add(plan)
            print 'Plan {} is created'.format(plan_name)
        return plan

    def get_or_create_test_run(self, run_name):
        """Get existing or create new TestRail Run."""
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
                'project_id': self.project_id,
                'milestone_id': self.milestone.id,
                'plan_id': self.plan.id
            }
            run = self.plan.api.add_plan_entry(entry)
            run = self.tr_project.api.get_run(run['id'])
            print 'Run {} is created'.format(run_name)
        return run

    def add_results(self, cases_xml):
        tests = list(self.tr_project.tests(self.run))

        for test in tests:
            status = cases_xml.get(get_test_group(test))
            if status is None:
                continue
            if status not in self.statuses:
                print('Unknown status {}. Ignoring'.format(status))
                continue

            result = self.tr_project.result()
            result.test = test
            result.status = self.statuses[status]

            self.tr_project.add(result)


tc = parse_xml()
p = Reporter(tr_project, tr_milestone, tr_suite, tr_testplan, tr_testrun, tc)
