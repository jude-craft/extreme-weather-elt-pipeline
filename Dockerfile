# use python light weight base image
FROM python:3.11-slim

# install uv
RUN pip install uv

# set working directory inside the container
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Use uv to install dependencies quickly
RUN uv pip install --system -r  requirements.txt

# Copy the extraction script into the container
COPY extract.py .

# Run the script when the container starts
CMD ["python", "extract.py"]