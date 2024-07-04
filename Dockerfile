FROM python:3.11

# Container workdir
WORKDIR /

# Copies folders into workdir
COPY data/ data/
COPY endpoints/ endpoints/
COPY model/ model/
COPY routers/ routers/

# Copies files into workdir
COPY .env /
COPY main.py /
COPY settings.py /
COPY requirements.txt /

# Builds python solution
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 4010

CMD [ "--host", "0.0.0.0", "--port", "4010" ]
ENTRYPOINT [ "uvicorn" , "main:app"]