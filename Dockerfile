FROM python:3.6
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

#Additional installation for HealthPlanner API
RUN pip install -r requirements.txt

EXPOSE 5000
LABEL io.openshift.expose-services 5000:http

CMD [ "python", "app.py" ]