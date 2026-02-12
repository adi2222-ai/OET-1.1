# OET Practice Test Simulator

A comprehensive web-based simulator for the **Occupational English Test (OET)** featuring all four essential sections: Reading, Listening, Writing, and Speaking. This platform is designed for healthcare professionals preparing for the OET exam.

## Features

### ✅ Complete OET Test Sections

1. **Reading Comprehension (45 minutes)**
   - 4 medical passages with comprehension questions
   - Multiple choice questions
   - Real-time progress tracking
   - Instant scoring

2. **Listening Comprehension (30 minutes)**
   - Audio-based passages (2 passages)
   - Multiple choice questions
   - Play/pause controls
   - Realistic healthcare scenarios

3. **Professional Writing (45 minutes)**
   - 2 writing tasks (letters and case notes)
   - Word count tracker
   - Sample answers for reference
   - Manual assessment capability

4. **Professional Speaking (20 minutes)**
   - 2 speaking tasks
   - Microphone recording capability
   - Assessment criteria guidance
   - Role-play scenarios

### 📊 User Features

- **User Authentication**: Register and login to track progress
- **Dashboard**: Overview of all test sections and statistics
- **Progress Tracking**: View test history and improvement over time
- **Vocabulary Module**: Learn 20+ medical terms with definitions
- **Mock Tests**: Full OET simulation test (160 minutes, all 4 sections)
- **Performance Analytics**: Detailed scoring and progress reports

## Installation & Setup

### Prerequisites
- Python 3.11+
- Flask and dependencies (see `pyproject.toml`)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OET-1.1
   ```

2. **Create virtual environment** (if not already done)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or if using pyproject.toml
   pip install -e .
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the app**
   - Open browser and navigate to: `http://localhost:5000`

## Usage Guide

### For New Users

1. **Register**: Create an account with email and password
2. **Login**: Access your personal dashboard
3. **Choose a Test**:
   - **Practice Tests**: Test individual sections
   - **Mock Tests**: Full exam simulation

### Taking a Test

#### Reading Test
- Read passages on the left
- Answer multiple choice questions on the right
- Timer counts down (45 minutes)
- Submit when complete

#### Listening Test
- Click play to listen to audio
- Answer questions after listening
- Can replay audio (recommended: once or twice)
- 30 minutes total

#### Writing Test
- Read task instructions
- Write your response in the textarea
- Word count tracker helps monitor limit
- View sample answer for guidance
- 45 minutes total

#### Speaking Test
- Review the task and assessment criteria
- Click record button to start recording
- Speak your response clearly
- Can record multiple times
- 20 minutes total

### Viewing Results

After completing a test:
1. View immediate score and feedback
2. Check correct answers and explanations
3. Save results for future review
4. View progress graph on dashboard

## Project Structure

```
OET-1.1/
├── main.py                 # Flask app (core logic)
├── data/                   # JSON data storage
│   ├── oet_tests.json     # Test content (all 4 sections)
│   ├── users.json          # User accounts
│   ├── test_results.json   # Test scores
│   └── vocabulary.json     # Medical terminology
├── templates/              # HTML templates
│   ├── base.html          # Base layout
│   ├── dashboard.html     # User dashboard
│   ├── reading_test_interface.html
│   ├── listening_test_interface.html
│   ├── writing_test_interface.html
│   ├── speaking_test_interface.html
│   ├── practice_tests.html
│   └── ...                # Other pages
├── static/                # Static files
│   ├── css/style.css
│   ├── js/main.js
│   └── audio/             # Audio files for listening tests
└── pyproject.toml        # Python package configuration

```

## Test Questions & Answers

### Reading Section
- Question 1: Answer 1
- Question 2: Answer 2
- Question 3: Answer 1
- Question 4: Answer 3
- etc.

### Listening Section
- Question 1: Answer 1
- Question 2: Answer 0
- Question 3: Answer 2
- etc.

### Writing & Speaking
- Manual assessment required (human review)
- Completion scores based on submission

## Medical Vocabulary

The app includes 20+ medical terms with:
- Definition
- Specialty (Cardiovascular, Respiratory, etc.)
- Usage examples

Terms covered:
- Hypertension
- Tachycardia
- Dyspnea
- Hypoglycemia
- Arrhythmia
- And more...

## Scoring System

### Reading & Listening
- Automatic scoring (multiple choice)
- Score = (Correct Answers / Total Questions) × 100

### Writing & Speaking
- Completion-based preliminary score
- Requires manual human assessment for final score
- Assessors check for:
  - Clarity and professionalism
  - Appropriate vocabulary
  - Grammar and structure
  - Task completion

## Features & Functionality

### Dashboard Statistics
- Total tests completed
- Medical terms learned
- Average score across all tests
- Day streak counter

### Quick Access
- One-click access to each test section
- Mock test launch
- Vocabulary learning
- Progress view

### Timer System
- Countdown timer for each section
- Auto-submit when time expires
- Progress indication

## Browser Support

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (responsive design)

## Microphone Access (for Speaking Tests)

- Required for recording responses
- Browser will request permission
- Allow microphone access when prompted
- Uses Web Audio API for recording

## Audio Files

Audio files for listening tests are stored in:
- `static/audio/listening.mp3`

Format: MP3, monoaural, 8-16kHz recommended

## Troubleshooting

### "No microphone permissions"
- Allow microphone access in browser settings
- Check if microphone is connected
- Try different browser

### Timer issues
- Ensure JavaScript is enabled
- Check browser clock is correct
- Try refreshing the page

### Audio not playing
- Check if audio file exists in `static/audio/`
- Verify browser audio permissions
- Try different audio format if available

## Future Enhancements

- [ ] AI-powered speaking assessment
- [ ] Adaptive difficulty levels
- [ ] Mobile app version
- [ ] Video explanations for answers
- [ ] Study group features
- [ ] Certificate generation

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Bootstrap, JavaScript
- **Storage**: JSON files (can be upgraded to SQL database)
- **Authentication**: Flask-Login with hashed passwords
- **Forms**: Flask-WTF with validation

## Database Structure

### users.json
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "password_hash": "hashed_password",
  "subscription_type": null,
  "subscription_expires": null,
  "is_superuser": false,
  "created_at": "2024-02-15T10:30:00"
}
```

### oet_tests.json
Contains comprehensive test data with:
- Reading passages and questions
- Listening passages and audio references
- Writing tasks with prompts and word limits
- Speaking tasks with assessment criteria

## Contributing

To contribute improvements:
1. Test new features thoroughly
2. Follow PEP 8 Python style guide
3. Update documentation
4. Create clear commit messages

## License

This project is open source and available for educational purposes.

## Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Contact the development team

---

**Version**: 1.1  
**Last Updated**: February 2026  
**Status**: Fully Functional OET Simulator ✅
