FROM usgsastro/miniflask
RUN conda install -c conda-forge flask psycopg2
RUN pip install flask-cas-ng
ADD . /
WORKDIR /app

CMD ["python", "budgeting.py"]
