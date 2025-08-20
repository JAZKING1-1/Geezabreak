# GeezaBreak Project

A Django-based web application for GeezaBreak, providing services for children and families.

## Features

- Referral system for service requests
- Comment and feedback functionality
- User-friendly interface with responsive design
- Comprehensive admin dashboard

## Setup Instructions

### Prerequisites
- Python 3.x
- Django

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/geezabreak.git
cd geezabreak
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run migrations:
```
python manage.py migrate
```

5. Start the development server:
```
python manage.py runserver
```

## Project Structure

- `geezabreak/`: Main project configuration
- `main/`: Primary application with models, views, and templates
- `static/`: Static files (CSS, JavaScript, images)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
