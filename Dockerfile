FROM python:3.9
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update -y
RUN apt-get update
RUN yes y | apt-get install cmake
RUN cd pipelines/MyBindings; mkdir build
RUN cd pipelines/MyBindings/build; cmake ..; make; mv denovo_sequencing.cpython-39-x86_64-linux-gnu.so ../../DeNovo/denovo_sequencing.so
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000" ]