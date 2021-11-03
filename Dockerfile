FROM python
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip uninstall django
RUN pip install django pymongo dnspython
RUN pip freeze >> requirements.txt
