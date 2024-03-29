FROM python:3.12-rc-slim
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
