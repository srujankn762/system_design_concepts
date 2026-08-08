# Docker + Django Learning Notes (README)

> **Project:** Hello World Django API using Docker\
> **Purpose:** Future reference (50 days later ಕೂಡ ನೋಡಿದರೆ ಅರ್ಥ ಆಗಬೇಕು 😄)

## What I Learned

-   Python Interpreter
-   Virtual Environment (venv)
-   requirements.txt
-   Docker
-   Dockerfile
-   Docker Image
-   Docker Container
-   Gunicorn
-   Port Mapping
-   Docker Build
-   Docker Run

------------------------------------------------------------------------

# Python Interpreter

Python Interpreter ಅಂದ್ರೆ **Python Engine**.

ನಾನು ಬರೆದ Python code ಅನ್ನು ಓದಿ execute ಮಾಡುತ್ತದೆ.

**Bike Example**

-   Bike = Project
-   Engine = Python Interpreter

Engine ಇಲ್ಲದ Bike ಓಡುವುದಿಲ್ಲ. Interpreter ಇಲ್ಲದ Project Run ಆಗುವುದಿಲ್ಲ.

------------------------------------------------------------------------

# Virtual Environment (venv)

ಒಂದು Projectಗೆ ಬೇಕಾದ Packages ಅನ್ನು ಬೇರೆ Projectsಗೆ interfere ಆಗದಂತೆ
ಪ್ರತ್ಯೇಕವಾಗಿ ಇಡುವ Folder.

Packages install ಆಗುವ ಜಾಗ:

``` text
venv/lib/python3.x/site-packages/
```

------------------------------------------------------------------------

# requirements.txt

Projectಗೆ ಬೇಕಾದ Python packages list.

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# Docker

Docker ಅಂದ್ರೆ Application ಅನ್ನು ಒಂದು Portable Box (Container) ಒಳಗೆ Pack ಮಾಡಿ
ಎಲ್ಲೆಡೆ ಒಂದೇ ರೀತಿಯಲ್ಲಿ Run ಮಾಡಿಸುವ Technology.

------------------------------------------------------------------------

# Dockerfile

Dockerಗೆ Instructions ಕೊಡುವ File.

## Example

``` dockerfile
FROM python:3.12-slim

WORKDIR /srujan

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /srujan
RUN pip install -r requirements.txt

COPY . /srujan

EXPOSE 8055

CMD [
"gunicorn",
"helloworld.wsgi:application",
"--bind",
"0.0.0.0:8055",
"--workers",
"3"
]
```

## Explanation

### FROM

Base Python Image.

### WORKDIR

Container ಒಳಗೆ Working Folder.

### RUN

Linux packages install ಮಾಡುತ್ತದೆ.

-   `apt-get update` → package list update
-   `build-essential` → compiler tools
-   `libpq-dev` → PostgreSQL support
-   `rm -rf` → temporary files delete

### COPY

Syntax:

``` text
COPY source destination
```

Examples:

``` dockerfile
COPY requirements.txt /srujan
COPY . /srujan
```

`.` = current project folder.

### EXPOSE

``` dockerfile
EXPOSE 8055
```

Container listens on port 8055.

### CMD

Gunicorn ಮೂಲಕ Django start ಮಾಡುತ್ತದೆ.

------------------------------------------------------------------------

# Build Image

``` bash
docker build -t hello-world-image .
```

`.` = current folder.

------------------------------------------------------------------------

# Run Container

``` bash
docker run -p 8008:8055 hello-world-image
```

### IMPORTANT:

```text
8008 : Is Your local machine port
8055 : Is the port exposed by docker container
```
Browser:

``` text
http://localhost:8008
```

------------------------------------------------------------------------

# Image vs Container

-   Image = Blueprint
-   Container = Running Application

------------------------------------------------------------------------

# Useful Commands

``` bash
docker images
docker ps
docker ps -a
docker rm <container_id>
docker rmi <image_name>
```

------------------------------------------------------------------------

# Errors I Faced

### No module named helloworld.wsgi

Wrong:

``` dockerfile
COPY .. /srujan
```

Correct:

``` dockerfile
COPY . /srujan
```

### This site can't be reached

Wrong:

``` bash
docker run hello-world-image
```

Correct:

``` bash
docker run -p 8000:8000 hello-world-image
```

### DisallowedHost

Open:

``` text
http://localhost:8000
```

(Not `0.0.0.0:8000`)

------------------------------------------------------------------------

# Final Flow

``` text
Create Django Project
↓
Create requirements.txt
↓
Write Dockerfile
↓
docker build -t hello-world-image .
↓
docker run -p 8000:8000 hello-world-image
↓
http://localhost:8000
↓
Application Running 🚀
```
