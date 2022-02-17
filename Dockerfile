FROM python:3.9-slim-bullseye

# pm2 needed for running Celery workers.
\ 
RUN apt-get -y update && apt-get install -y --no-install-recommends build-essential  \
    curl wget nginx ca-certificates npm \
    && npm install pm2 -g \
    && pip install --upgrade pip setuptools \ 
    && rm -rf /var/lib/apt/lists/*

# Set some environment variables. 
# PYTHONUNBUFFERED - keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. 
# PYTHONDONTWRITEBYTECODE - keeps Python from writing the .pyc files which are unnecessary in this case. 
# PATH & PYTHONPATH - We also update PATH &NPYTHONPATH so that the train and serve programs are found when the container is invoked.
ENV PYTHONUNBUFFERED=TRUE PYTHONDONTWRITEBYTECODE=TRUE PATH="/home/user/app:${PATH}" PYTHONPATH="/home/user/app:${PYTHONPATH}"

# Install python libraries
COPY app/requirements.txt .
RUN pip install -r requirements.txt

# Add non-root user
RUN groupadd -r user && useradd -r -g user user
RUN chown -R user /var/log/nginx /var/lib/nginx /tmp

# Download the model into user home directory, using the user
WORKDIR /home/user
RUN chown -R user /home/user/
USER user
RUN python -c "from transformers import pipeline; classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')"
USER root 

# Set up the program in the image
COPY app /home/user/app
WORKDIR /home/user/app

# Pylint to make sure our code is not too bad.
RUN pylint --disable=R,C ./**/*.py

# Chown app folder
RUN chown -R user /home/user/app 

# Expose port
EXPOSE 8080

# Entrypoint
ENTRYPOINT [ "sh", "./entrypoint" ]

# Switch to the user
USER user