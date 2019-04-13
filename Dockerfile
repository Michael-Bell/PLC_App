From m8377/plc_app_ufv:latest
Add . /code
WORKDIR /code
RUN apt update
RUN apt install -y usbutils
RUN pip install -r requirements.txt
CMD python app.py