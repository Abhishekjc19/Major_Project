FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir scikit-learn xgboost

# Copy application code and assets
COPY backend/ ./backend/
COPY models/xgb_clf.pkl ./models/xgb_clf.pkl
COPY models/xgb_reg.pkl ./models/xgb_reg.pkl
COPY datasets/ ./datasets/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
