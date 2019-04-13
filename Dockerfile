From python:3.6
Add . /code
WORKDIR /code
RUN apt update
RUN apt install -y usbutils
RUN pip install -r requirements.txt
CMD python app.py
