FROM python:3.10

# Set the time zone
ARG TZ Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the application's root path
ENV APPLICATION_ROOT /

# Set the database port
ENV DB_PORT 5432

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install finance module
COPY . .
RUN pip install --no-cache-dir .

ENTRYPOINT ["gunicorn", "finance:app", "--bind=0.0.0.0:5000"]
CMD [ \
    "--log-level=info", \
    "--access-logformat=%(t)s %(h)s %(a)s %(r)s %(s)s %(b)s", \
    "--access-logfile=-", \
    "--logfile=-" \
]

EXPOSE 5000