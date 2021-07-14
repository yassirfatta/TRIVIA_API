import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format('postgres','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who invented the phonograph?',
            'answer': 'Thomas Edison',
            'category': 'History',
            'difficaulty': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test getting all categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    # Test getting 10 questions per page
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['cuerrnt_category'])
    
    #Test of NOT FOUND questions request   
    def test_404_not_found_questions(self):
        res = self.client().get('/question?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')
    
    # Test creating new question
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    # Test if creating question is not allowed
    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/50', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')

    # Test question deletion
    def test_delete_question(self):
        res = self.client().delete('/questions/10')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 10).one_or_none

        self.assertEqual(self.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 10)
        self.assertEqual(question, None)

    # Test if delete a question does not exist
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('questions/100')
        data = json.loads(res.data)

        self.assertEqual(self.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # Test Searching for questions that include 'title'
    def test_get_questions_search_with_results(self):
        res = self.client().post('/questions', json={'search': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(len(data['questions']), 1)
    
    # Test Searching for questions without results
    def test_get_questions_search_without_results(self):
        res = self.client().post('/questions', json={'search': 'udacity'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQuestions'], 0)
        self.assertEqual(len(data['questions']), 0)

    # Test getting question by category
    def test_get_question_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestion'])
        self.assertEqual(data['current_category'], 4)

    # Test 404 if category not found
    def test_404_if_category_not_found(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    # Test Post a question in quiz
    def test_post_quiz_question(self):
        res = self.client().post('/quizes', json={'quiz_category':4})
        data = json.loads(res.data)
        questions = Question.query.filter(Question.category == 4)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(questions.category, 4)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()