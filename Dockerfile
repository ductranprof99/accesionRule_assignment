FROM python
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip uninstall django
RUN pip install django dnspython djangorestframework-simplejwt django-rest-swagger djangorestframework djongo google-api-python-client drf-yasg bs4 schedule django-cors-headers
RUN pip install mlxtend pandas numpy matplotlib schedule
RUN pip install pymongo==3.12.1
RUN pip freeze >> requirements.txt
