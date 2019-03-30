From python:3.6
Add . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python app.py