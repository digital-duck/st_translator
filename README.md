
# st_translator - Streamlit Translation Management System

A comprehensive translation management system built with Streamlit, supporting multiple translation providers and team collaboration.

## Features

### Current Features
- **Multiple Translation Providers**
  - DeepL integration with auto language detection
  - Source language override capability
  - Alternative translations tracking

- **Smart Translation Interface**
  - Clean three-column layout for language selection
  - Real-time language detection
  - Editable translation results
  - Notes/comments support
  - Project-based organization

- **Data Persistence**
  - SQLite database backend
  - Translation history tracking
  - Full audit trail (creation/update timestamps)

### Technical Stack
- Streamlit for UI
- DeepL API for translation
- SQLite for data storage
- Python dotenv for configuration

## Installation

1. Clone the repository
```bash
git clone git@github.com:digital-duck/st_translator.git
cd st_translator
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
Create a `.env` file with your API keys:
```
DEEPL_AUTH_KEY=your-deepl-api-key
```

4. Initialize the database
```bash
python init_db.py
```

5. Run the application
```bash
streamlit run app.py
```

## Usage

### Translation Page
1. Select translation service provider (currently DeepL)
2. Choose target language
3. Optionally override source language
4. Enter text to translate
5. Review and edit translation
6. Add notes if needed
7. Save translation to project

### Project Management
- Organize translations by project
- Track creation and updates
- Support team collaboration

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS t_translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project text NOT NULL,
    service_provider TEXT NOT NULL,
    source_text TEXT NOT NULL,
    target_text TEXT, 
    source_lang TEXT,
    target_lang TEXT,
    note TEXT,
    created_by TEXT,
    updated_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Contributing
Contributions are welcome! Please see our [ROADMAP.md](ROADMAP.md) for planned features and areas where help is needed.

## License
[Apache License](LICENSE)