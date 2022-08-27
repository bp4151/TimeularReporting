FROM python:3.11.0rc1-bullseye
WORKDIR /code

ENV API_KEY=${API_KEY}
ENV API_SECRET=${API_SECRET}
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
COPY .env .

RUN python3 -m venv $VIRTUAL_ENV
RUN pip install -r requirements.txt

COPY timeular_reporting.py .
CMD ["python", "timeular_reporting.py"]
