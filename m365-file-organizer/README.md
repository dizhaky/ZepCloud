# M365 File Organizer

Python application to connect to Microsoft 365, analyze files with Claude, organize/rename intelligently, and store searchable metadata in MongoDB Atlas.

## Quickstart

1. Create and populate `.env` from `.env.example`.
2. Create a virtual environment (Python 3.11+), then install requirements:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

3. Verify settings load and MongoDB connectivity (optional):

```python
from config.settings import settings
from config.mongodb import MongoClientManager

print("DB:", settings.mongodb_database)
# In an async context, you can: await MongoClientManager.ping()
```

## Project Structure

See the implementation spec for full module layout under `src/`.

## Notes

- Use Python 3.11+
- Follow FastAPI/Pydantic/SQLAlchemy async best practices for API components
- Do not commit your `.env`
