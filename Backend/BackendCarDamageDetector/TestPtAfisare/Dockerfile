FROM python:3.11-slim

# We set the working directory
WORKDIR /app

# nstall the required system dependencies, including msodbcsql17 for pyodbc
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql17 \
    unixodbc \
    unixodbc-dev \
    build-essential \
    gcc \
    libgl1 \
    libglib2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the application files into the container
COPY . .

# install the necessary Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# expose the port used by the application
EXPOSE 8080

# start the FastAPI server with uvicorn
CMD ["uvicorn", "ElementDetector:app", "--host", "0.0.0.0", "--port", "8080"]



