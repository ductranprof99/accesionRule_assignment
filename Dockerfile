FROM python
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip uninstall django
RUN pip install django pymongo dnspython djangorestframework-simplejwt django-rest-swagger djangorestframework djongo google-api-python-client drf-yasg bs4 mlxtend pandas numpy matplotlib
RUN pip freeze >> requirements.txt
