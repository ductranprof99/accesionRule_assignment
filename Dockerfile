FROM python
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip uninstall django
RUN pip install django pymongo dnspython djangorestframework-simplejwt django-rest-swagger djangorestframework djongo google-api-python-client drf-yasg bs4 schedule
RUN pip install mlxtend pandas numpy matplotlib schedule
RUN pip freeze >> requirements.txt
