import os
import requests
import pandas as pd
import pdb


class Talent:
    """TalentLMS client class
    """

    def __init__(self,
                 apikey=os.environ.get('apikey'),
                 domain=os.environ.get('domain')):
        """initialize by getting the apikey and domain of TalentLMS account"""
        self.apikey = apikey
        self.domain = domain

    def get_users(self):
        """get all users"""
        url = 'https://{}:@{}.talentlms.com/api/v1/users'.format(
            self.apikey, self.domain)

        response = requests.request('GET', url)
        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        users = response.json()
        return(users)

    def get_user(self, user_id):
        """get a specific user"""
        url = 'https://{}:@{}.talentlms.com/api/v1/users/id:{}'\
              .format(self.apikey, self.domain, user_id)

        response = requests.request('GET', url)
        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        user = response.json()
        return(user)

    def get_courses(self):
        """get all courses"""
        url = 'https://{}:@{}.talentlms.com/api/v1/courses'.format(
            self.apikey, self.domain)

        response = requests.request('GET', url)

        courses = response.json()
        return(courses)

    def get_course(self, course_id):
        """get a specific course"""
        url = 'https://{}:@{}.talentlms.com/api/v1/courses/id:{}'\
              .format(self.apikey, self.domain, course_id)

        response = requests.request('GET', url)
        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        course = response.json()
        return(course)

    def get_user_status_in_course(self, course_id, user_id):
        """find a users progress in a given course"""
        url = 'https://{}:@{}.talentlms.com/api/v1/getuserstatusincourse/course_id:{},user_id:{}'\
              .format(self.apikey, self.domain, course_id, user_id)

        response = requests.request('GET', url)
        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        progress = response.json()
        return(progress)

    def get_timeline(self, event_type, course_id=None, user_id=None):
        """get timeline for given event type
        
        event_type: required (see timeline event mappings for options https://www.talentlms.com/pages/docs/TalentLMS-API-Documentation.pdf)
        course_id: optional
        user_id: optional
        """
        
        url = ('https://{}:@{}.talentlms.com/api/v1/gettimeline/event_type:{}'\
               .format(self.apikey, self.domain, event_type))
        if course_id:
            url += ',course_id:{}'.format(course_id)
        if user_id:
            url += ',user_id:{}'.format(user_id)
              
        response = requests.request('GET', url)
        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        timeline = response.json()
        return(timeline)


    
    def get_survey_response(self, survey_id, user_id):
        """get survey answers for a given survey and user"""
        url = 'https://{}:@{}.talentlms.com/api/v1/getsurveyanswers/survey_id:{},user_id:{}'\
              .format(self.apikey, self.domain, survey_id, user_id)

        response = requests.request("GET", url)

        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        answers = response.json()

        return(answers)

    def get_survey_responses(self, survey_id, user_ids=[], verbose=False):
        """get responses to a survey from a list of user ids (default is all registered users)"""

        if not user_ids:
            user_ids = [i['id'] for i in self.get_users()]

        answers = []
        for user_id in user_ids:
            if verbose:
                print('Getting answers from user: {}'.format(user_id))

            try:
                answer = self.get_survey_response(survey_id, user_id)
            except TalentLMSError:
                continue

            answers.append(answer)

        return(answers)

    def get_many_survey_responses(self, course_ids=[], verbose=False):
        """get responses to surveys from multiple courses"""

        if not course_ids:
            course_ids = [i['id'] for i in self.get_courses()]

        answers_all = {}
        for course_id in course_ids:
            try:
                course = self.get_course(course_id)
            except TalentLMSError:
                continue

            # get course roster
            users = [i['id']
                     for i in course['users'] if i['role'] == 'learner']

            # get course surveys
            surveys = [i['id']
                       for i in course['units'] if i['type'] == 'Survey']

            # if there are no surveys, skip this course
            if not surveys:
                continue

            answers = {}
            for survey in surveys:
                if verbose:
                    print('Getting results for survey: {}'.format(survey))
                answers[survey] = self.get_survey_responses(
                    survey, users, verbose)
            answers_all[course_id] = answers

        return(answers_all)

    def get_branches(self):
        """get all branches available"""
        url = 'https://{}:@{}.talentlms.com/api/v1/branches'.format(
            self.apikey, self.domain)

        response = requests.request('GET', url)

        branches = response.json()
        return(branches)

    def get_branch(self, branch_id):
        """get a specific branch"""
        url = 'https://{}:@{}.talentlms.com/api/v1/branches/id:{}'\
              .format(self.apikey, self.domain, branch_id)

        response = requests.request('GET', url)
        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        branch = response.json()
        return(branch)

    def get_statuses_df(self, course_ids):
        """get user statuses for each course"""
        statuses = pd.DataFrame(
            columns=['course_id', 'course_name', 'user_id', 'perc_comp'])
        for cid in course_ids:
            course = self.get_course(cid)
            for user in course['users']:
                if user['role'] == 'learner':
                    row = {'course_id': course['id'],
                           'course_name': course['name'],
                           'user_id': user['id'],
                           'perc_comp': user['completion_percentage'],
                           }
                    statuses = statuses.append(row, ignore_index=True)
        return(statuses)

    def gotocourse(self, user_id, course_id, export=None):
        url = 'https://{}:@{}.talentlms.com/api/v1/gotocourse/user_id:{},course_id:{}'.format(
            self.apikey, self.domain, user_id, course_id)

        response = requests.request('GET', url)
        if response.status_code != 200:
            raise TalentLMSError(response.json()['error']['message'])

        goto = response.json()['goto_url']

        course_page = requests.request('GET', goto)

        if not export:
            return(course_page.text)
        else:
            html = open(export, 'w')
            html.write(course_page.text)
            html.close()
            return(True)


class TalentLMSError(Exception):
    def __init__(self, error):
        Exception.__init__(self, error)
