import os
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
    
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers',
                          'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods',
                          'GET,PUT,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  
  @app.route('/categories', methods=['GET'])
  def getCategories():
    try:
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories.items]
    except:
      print(sys.exc_info())
      abort(422)
    return jsonify({
      'success': True,
      'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def getQuestions():
    try:
      page = request.args.get('page', 1, type=int)
      questions = Question.query.paginate(page, per_page=QUESTIONS_PER_PAGE)
      formatted_questions = [question.format() for question in questions.items]
      categories = Category.query.all()
      
      if len(questions) == 0:
        abort(404)

      return jsonify({
      'success': True,
      'questions': formatted_questions,
      'totalQuestions': len(Question.query.all()),
      'categories': categories,
      'current_category': questions.category
    })
    except:
      print(sys.exc_info())
      abort(422)
    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def deleteQuestion(question_id):
    question = Question.query.get(question_id)
    if question is None:
      abort(404)

    try:
      question.delete()

    except:
      print(sys.exc_info())
      abort(422)

    return jsonify({
      'success': True,
      'deleted': question_id
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/qustions', methods=['POST'])
  def createQuestion():
    data = request.get_json()
    try:
      question = Question(
        question=data['question'],
        answer=data['answer'],
        category=data['category'],
        difficulty=data['difficulty']
      )
      question.insert()
    except:
      print(sys.exc_info())
      abort(405)
    return jsonify({
      'success': True,
      'created': question.id,
      'question': question.format()
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def searchQuestion():
    body = request.get_json()
    search = body.get('search', None)
    page = request.args.get('page', 1, type=int)
    try:
      if search is None:
        questions = Question.query.order_by(Question.id).paginate(page, per_page= QUESTIONS_PER_PAGE)
        
      else:
        questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).paginate(page, per_page= QUESTIONS_PER_PAGE)
      
      formatted_questions = [question.format() for question in questions.items]
      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'totalQuestions': len(questions.all())
      })
    except:
      print(sys.exc_info())
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categoris/<int:category_id>/questions', methods=['GET'])
  def getByCategory(category_id):
    try:
      page = request.args.get('page', 1, type=int)
      questions = Question.query.filter(Question.category == category_id).paginate(page, per_page=QUESTIONS_PER_PAGE)
      formatted_questions = [question.format() for question in questions.items]
    except:
      print(sys.exc_info())
      abort(404)
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'current_category': category_id,
      'totalQuestions': questions.total
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizes', methods=['POST'])
  def getQuiz(quiz_category, previuos_questions):
    questions = Question.query.filter(Question.category == quiz_category)
    try:
      for question in questions:
        if question not in previuos_questions:
          return jsonify({
            'success': True,
            'current_question': question
          }), previuos_questions.insert(question)
        else:
          return jsonify({
            'success': True,
            'previous_question': question
          })
    except:
      print(sys.exc_info())
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(404)
  def notFound(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not Found"
      }), 404

  @app.errorhandler(405)
  def notFound(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "Method Not Allowed"
      }), 405

  @app.errorhandler(500)
  def noResponse(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "No Response"
      }), 500

  return app

    