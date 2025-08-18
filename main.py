
#!/usr/bin/env python

import os
import copy
import json
import time
import logging
from datetime import datetime, timedelta
from io import BytesIO

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, current_app, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Set up logging
logging.basicConfig(level=logging.INFO)

# ============ Flask App Configuration ============
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# ============ Forms ============
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

# ============ Data Manager & User Model ============
# Data file paths
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PRACTICE_TESTS_FILE = os.path.join(DATA_DIR, 'practice_tests.json')
FULL_MOCK_TESTS_FILE = os.path.join(DATA_DIR, 'full_mock_tests.json')
MOCK_TESTS_FILE = os.path.join(DATA_DIR, 'full_mock_tests.json')
TEST_RESULTS_FILE = os.path.join(DATA_DIR, 'test_results.json')
MOCK_TEST_RESULTS_FILE = os.path.join(DATA_DIR, 'mocktests_results.json')
VOCABULARY_FILE = os.path.join(DATA_DIR, 'vocabulary.json')
VOCABULARY_PROGRESS_FILE = os.path.join(DATA_DIR, 'vocabulary_progress.json')
JOBS_FILE = os.path.join(DATA_DIR, 'jobs.json')
CHAT_MESSAGES_FILE = os.path.join(DATA_DIR, 'chat_messages.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, subscription_type=None, subscription_expires=None, is_superuser=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.subscription_type = subscription_type
        self.subscription_expires = subscription_expires
        self.is_superuser = is_superuser

    def has_active_subscription(self):
        if not self.subscription_type or not self.subscription_expires:
            return False
        try:
            return datetime.fromisoformat(self.subscription_expires) > datetime.now()
        except:
            return False

    def is_super_user(self):
        return self.is_superuser

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))

# ============ Data Management Functions ============
def load_json_file(filepath, default=None):
    if default is None:
        default = []
    if not os.path.exists(filepath):
        save_json_file(filepath, default)
        return default
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default

def save_json_file(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_id(data_list):
    if not data_list:
        return 1
    return max(item['id'] for item in data_list) + 1

# User management
def get_users():
    return load_json_file(USERS_FILE, [])

def save_users(users):
    save_json_file(USERS_FILE, users)

def get_user_by_email(email):
    users = get_users()
    for user_data in users:
        if user_data['email'] == email:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                subscription_type=user_data.get('subscription_type'),
                subscription_expires=user_data.get('subscription_expires'),
                is_superuser=user_data.get('is_superuser', False)
            )
    return None

def get_user_by_id(user_id):
    users = get_users()
    for user_data in users:
        if user_data['id'] == user_id:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                subscription_type=user_data.get('subscription_type'),
                subscription_expires=user_data.get('subscription_expires'),
                is_superuser=user_data.get('is_superuser', False)
            )
    return None

def create_user(username, email, password):
    users = get_users()
    user_id = get_next_id(users)
    user_data = {
        'id': user_id,
        'username': username,
        'email': email,
        'password_hash': generate_password_hash(password),
        'subscription_type': None,
        'subscription_expires': None,
        'created_at': datetime.now().isoformat()
    }
    users.append(user_data)
    save_users(users)
    return User(id=user_id, username=username, email=email, password_hash=user_data['password_hash'])

# Test management
def get_practice_tests():
    return load_json_file(PRACTICE_TESTS_FILE, [
        {
            'id': 1,
            'title': 'Listening Practice Test 1',
            'section': 'Listening',
            'duration_minutes': 30,
            'description': 'Basic listening comprehension test',
            'is_premium': False,
            'content': {
                'sections': {
                    'listening': {
                        'duration_minutes': 30,
                        'passages': [],
                        'questions': []
                    }
                }
            }
        },
        {
            'id': 2,
            'title': 'Reading Practice Test 1',
            'section': 'Reading',
            'duration_minutes': 45,
            'description': 'Reading comprehension and analysis',
            'is_premium': False,
            'content': {
                'sections': {
                    'reading': {
                        'duration_minutes': 45,
                        'passages': [],
                        'questions': []
                    }
                }
            }
        }
    ])

def get_full_mock_tests():
    return load_json_file(MOCK_TESTS_FILE, [
        {
            'id': 100,
            'title': 'Complete OET Mock Test 1',
            'section': 'All Sections',
            'duration_minutes': 180,
            'description': 'Full OET practice exam covering all sections',
            'is_mock_test': True,
            'is_premium': False,
            'content': {
                'sections': {
                    'reading': {
                        'duration_minutes': 45,
                        'passages': [
                            {
                                'id': 1,
                                'title': 'Patient Care Guidelines',
                                'content': 'Comprehensive patient care guidelines for healthcare professionals...'
                            }
                        ],
                        'questions': [
                            {
                                'id': 1,
                                'question': 'What is the primary focus of patient care?',
                                'type': 'multiple_choice',
                                'options': ['Safety', 'Efficiency', 'Cost', 'Speed'],
                                'correct_answer': 0
                            }
                        ]
                    }
                }
            }
        }
    ])

def get_test_by_id(test_id):
    practice_tests = get_practice_tests()
    for test in practice_tests:
        if test['id'] == test_id:
            test['test_type'] = 'practice'
            return test
    mock_tests = get_full_mock_tests()
    for test in mock_tests:
        if test['id'] == test_id:
            test['test_type'] = 'mock'
            return test
    return None

# Test results management
def get_test_results():
    return load_json_file(TEST_RESULTS_FILE, [])

def save_test_results(results):
    save_json_file(TEST_RESULTS_FILE, results)

def get_mock_test_results():
    return load_json_file(MOCK_TEST_RESULTS_FILE, [])

def save_mock_test_results(results):
    save_json_file(MOCK_TEST_RESULTS_FILE, results)

def get_user_test_results(user_id):
    results = get_test_results()
    user_results = []
    for result in results:
        if result.get('user_id') == user_id:
            test = get_test_by_id(result.get('test_id'))
            if test:
                r = result.copy()
                r['practice_test'] = {'title': test.get('title'), 'section': {'name': test.get('section')}}
                user_results.append(r)
    return sorted(user_results, key=lambda x: x.get('completed_at', ''), reverse=True)

def save_test_result(user_id, test_id, score_percentage, time_taken_minutes, answers):
    results = get_test_results()
    result_id = get_next_id(results)
    result = {
        'id': result_id,
        'user_id': user_id,
        'test_id': test_id,
        'score_percentage': score_percentage,
        'time_taken_minutes': time_taken_minutes,
        'answers': answers,
        'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    results.append(result)
    save_test_results(results)
    return result_id

def save_mock_test_result(user_id, test_id, score_percentage, time_taken_minutes, answers):
    results = get_mock_test_results()
    result_id = get_next_id(results)
    result = {
        'id': result_id,
        'user_id': user_id,
        'test_id': test_id,
        'score_percentage': score_percentage,
        'time_taken_minutes': time_taken_minutes,
        'answers': answers,
        'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    results.append(result)
    save_mock_test_results(results)
    return result_id

# Vocabulary management
def get_vocabulary_words(specialty=None):
    words = load_json_file(VOCABULARY_FILE, [])
    if specialty:
        return [word for word in words if word.get('specialty', '').lower() == specialty.lower()]
    return words

def get_user_vocabulary_progress(user_id):
    progress_data = load_json_file(VOCABULARY_PROGRESS_FILE, {})
    return progress_data.get(str(user_id), {'learned_words': []})

def mark_word_as_learned(user_id, word_id):
    progress_data = load_json_file(VOCABULARY_PROGRESS_FILE, {})
    user_progress = progress_data.get(str(user_id), {'learned_words': []})
    if word_id not in user_progress['learned_words']:
        user_progress['learned_words'].append(word_id)
        progress_data[str(user_id)] = user_progress
        save_json_file(VOCABULARY_PROGRESS_FILE, progress_data)
        return True
    return False

def test_vocabulary_word(word):
    vocabulary = get_vocabulary_words()
    for vocab_word in vocabulary:
        if vocab_word.get('word', '').lower() == word.lower():
            return {
                'correct': True,
                'word': vocab_word['word'],
                'definition': vocab_word.get('definition', ''),
                'specialty': vocab_word.get('specialty', '')
            }
    return {'correct': False, 'message': f'"{word}" is not found in our medical vocabulary database.'}

# ============ Helper Functions ============
PDF_DIR = os.path.join(app.root_path, 'testspdf')
os.makedirs(PDF_DIR, exist_ok=True)

TEST_ANSWERS = {
    'Reading': {
        'question_1': '2',
        'question_2': '2',
        'question_3': '1',
        'question_4': '1',
        'question_5': '1',
        'question_6': '1',
        'question_7': '3',
        'question_8': '1',
        'question_9': '2',
        'question_10': '1'
    },
    'Listening': {
        'question_1': '1',
        'question_2': '2',
        'question_3': '1',
        'question_4': '1',
        'question_5': '1',
        'question_6': '1',
        'question_7': '2',
        'question_8': '1',
        'question_9': '1',
        'question_10': '1'
    },
    'Writing': {
        'question_writing': 'manual_grading_required'
    },
    'Speaking': {
        'question_speaking': 'manual_grading_required'
    }
}

def calculate_test_score(answers, test_section, test_data=None):
    """Calculate test score based on correct answers"""
    if test_section not in TEST_ANSWERS:
        app.logger.warning(f"Section {test_section} not in test answers")
        return 0.0

    correct_answers = TEST_ANSWERS[test_section]
    total_questions = len(correct_answers)
    correct_count = 0

    for question_key, correct_answer in correct_answers.items():
        if correct_answer == 'manual_grading_required':
            if question_key in answers and answers[question_key].strip():
                correct_count += 0.7
        else:
            if question_key in answers and answers[question_key] == correct_answer:
                correct_count += 1

    score = (correct_count / total_questions) * 100 if total_questions > 0 else 0.0
    return max(0.0, min(100.0, round(score, 1)))

def generate_test_pdf(result, test, user_name, time_taken_minutes):
    """Generate PDF report for test results"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title = Paragraph(f"OET Test Results - {test['title']}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    user_info = Paragraph(f"<b>Student:</b> {user_name}", styles['Normal'])
    story.append(user_info)

    completion_time = Paragraph(f"<b>Completed:</b> {result['completed_at']}", styles['Normal'])
    story.append(completion_time)

    time_taken = Paragraph(f"<b>Time Taken:</b> {time_taken_minutes} minutes", styles['Normal'])
    story.append(time_taken)
    story.append(Spacer(1, 12))

    score = Paragraph(f"<b>Score:</b> {result['score_percentage']:.1f}%", styles['Heading2'])
    story.append(score)

    doc.build(story)
    buffer.seek(0)
    return buffer

# ============ Routes ============
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and user.password_hash and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        if get_user_by_email(form.email.data):
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)

        create_user(form.username.data, form.email.data, form.password.data)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    practice_results = get_user_test_results(current_user.id)
    recent_tests = sorted(practice_results, key=lambda x: x.get('completed_at', ''), reverse=True)[:5]
    vocab_progress = get_user_vocabulary_progress(current_user.id)
    vocab_learned = len(vocab_progress.get('learned_words', [])) if vocab_progress else 0
    
    return render_template('dashboard.html', recent_tests=recent_tests, vocab_learned=vocab_learned, all_test_count=len(practice_results))

@app.route('/practice-tests')
@login_required
def practice_tests():
    tests = get_practice_tests()
    mock_tests = get_full_mock_tests()
    return render_template('practice_tests.html', tests=tests, mock_tests=mock_tests)

@app.route('/mock-tests')
def mock_tests():
    """Public mock tests page - accessible without login"""
    tests = get_full_mock_tests()
    return render_template('mock_tests.html', tests=tests)

@app.route('/test/<int:test_id>')
def take_test(test_id):
    test = get_test_by_id(test_id)
    if not test:
        flash('Test not found', 'danger')
        return redirect(url_for('practice_tests') if current_user.is_authenticated else url_for('mock_tests'))

    session['test_start_time'] = time.time()
    session['current_test_id'] = test_id
    
    is_mock_test = test.get('is_mock_test', False)
    session['mock_test'] = is_mock_test

    if is_mock_test:
        return render_template('mock_test_interface.html', test=test)

    if not current_user.is_authenticated:
        flash('Please log in to take this test', 'warning')
        return redirect(url_for('login'))

    return render_template('practice_test_interface.html', test=test)

@app.route('/submit-test', methods=['POST'])
def submit_test():
    test_id = session.get('current_test_id')
    if not test_id:
        flash('No active test found', 'danger')
        return redirect(url_for('practice_tests') if current_user.is_authenticated else url_for('mock_tests'))

    is_mock = bool(session.get('mock_test', False))

    if not is_mock and not current_user.is_authenticated:
        flash('Please log in to submit this test.', 'warning')
        return redirect(url_for('login'))

    test = get_test_by_id(test_id)
    if not test:
        flash('Test not found', 'danger')
        return redirect(url_for('practice_tests'))

    answers = {}
    for key, value in request.form.items():
        if key.startswith('question_'):
            answers[key] = value

    test_section = test.get('section', 'Reading')
    score_percentage = calculate_test_score(answers, test_section, test)

    start_time = session.get('test_start_time', time.time())
    time_taken_seconds = int(time.time() - start_time)
    time_taken_minutes = max(1, time_taken_seconds // 60)

    user_id = current_user.id if (current_user and current_user.is_authenticated) else None

    score_percentage = float(score_percentage) if score_percentage is not None else 0.0

    if is_mock:
        result_id = save_mock_test_result(user_id, test_id, score_percentage, time_taken_minutes, answers)
    else:
        result_id = save_test_result(user_id, test_id, score_percentage, time_taken_minutes, answers)

    session.pop('test_start_time', None)
    session.pop('current_test_id', None)
    session.pop('mock_test', None)

    if is_mock:
        return redirect(url_for('mock_test_results', result_id=result_id))
    else:
        return redirect(url_for('test_results', result_id=result_id))

@app.route('/results/<int:result_id>')
@login_required
def test_results(result_id):
    all_results = get_test_results()
    result = next((r for r in all_results if r['id'] == result_id and r.get('user_id') == current_user.id), None)

    if not result:
        flash('Test result not found', 'danger')
        return redirect(url_for('dashboard'))

    test = get_test_by_id(result['test_id'])
    if not test:
        test = {
            'id': result['test_id'],
            'title': f'Test {result["test_id"]}',
            'section': 'Unknown',
            'description': 'Test completed'
        }

    return render_template('practice_test_results.html', result=result, test=test)

@app.route('/mock-results/<int:result_id>')
def mock_test_results(result_id):
    all_results = get_mock_test_results()
    result = next((r for r in all_results if r['id'] == result_id), None)
    if not result:
        flash('Mock result not found', 'danger')
        return redirect(url_for('mock_tests'))
    test = get_test_by_id(result['test_id'])
    return render_template('mock_test_results.html', result=result, test=test)

@app.route('/vocabulary')
@login_required
def vocabulary():
    specialty = request.args.get('specialty', 'all')
    words = get_vocabulary_words(specialty if specialty != 'all' else None)
    vocab_progress = get_user_vocabulary_progress(current_user.id)
    learned_word_ids = vocab_progress.get('learned_words', [])
    all_words = get_vocabulary_words()
    specialties = sorted(set(word.get('specialty') for word in all_words if word.get('specialty')))
    return render_template('vocabulary.html', words=words, learned_word_ids=learned_word_ids, specialties=[(s,) for s in specialties], selected_specialty=specialty)

@app.route('/vocabulary-test', methods=['POST'])
@login_required
def vocabulary_test():
    data = request.get_json()
    word = data.get('word', '').strip()
    result = test_vocabulary_word(word)
    return jsonify(result)

@app.route('/mark-word-learned/<int:word_id>', methods=['POST'])
@login_required
def mark_word_learned(word_id):
    success = mark_word_as_learned(current_user.id, word_id)
    return jsonify({'success': success})

@app.route('/subscription')
@login_required
def subscription():
    return render_template('subscription.html')

@app.route('/consultation')
def consultation():
    return render_template('consultation.html')

@app.route('/materials')
def materials():
    return render_template('materials.html')

@app.route('/progress')
@login_required
def progress():
    test_results = get_user_test_results(current_user.id)
    vocab_progress = get_user_vocabulary_progress(current_user.id)
    vocab_count = len(vocab_progress.get('learned_words', [])) if vocab_progress else 0
    total_vocab = len(get_vocabulary_words())
    return render_template('progress.html', test_results=test_results, vocab_count=vocab_count, total_vocab=total_vocab)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
