ARG DBMS="mariadb"

FROM python:3.9-alpine as builder
ARG DBMS

# set work directory
WORKDIR /build

RUN apk update \
 && apk add gcc make python3-dev musl-dev jpeg-dev zlib-dev

# install database dependencies
RUN if [[ "${DBMS}" == "postgres" ]]; then apk add postgresql-dev; fi

# install dependencies
COPY rqmts/ rqmts

RUN cp rqmts/requirements.txt requirements.txt; \
    if [[ "${DBMS}" == "postgres" ]]; then cat rqmts/requirements.postgres.txt >> requirements.txt; fi; \
    if [[ "${DBMS}" == "mariadb" ]]; then cat rqmts/requirements.mariadb.txt >> requirements.txt; fi;

RUN pip install --prefix=/build/venv -r requirements.txt

FROM python:3.9-alpine
ARG DBMS
ENV DBMS=${DBMS} PROJECT_NAME="app"

# app config
ENV SQL_USER=${PROJECT_NAME} ALLOWED_HOSTS='0.0.0.0' DEBUG=0 SCHEMA="https"

# create the app user and directories
ENV HOME=/home/app APP_HOME=/home/app/web
RUN mkdir -p ${HOME} \
 && mkdir -p ${APP_HOME} \
 && addgroup -S app \
 && adduser -S app -G app \
 && mkdir -p "${APP_HOME}/app/media"
WORKDIR ${APP_HOME}

# install database dependencies
RUN if [[ "${DBMS}" == "postgres" ]]; then apk add --no-cache libpq; fi

COPY --from=builder /build/venv/ /usr/local/

# copy project
COPY . ${APP_HOME}

# chown all the files to the app user
RUN chown -R app:app ${APP_HOME} \
 && chmod +x ${APP_HOME}/entrypoint.sh

ENTRYPOINT "${APP_HOME}/entrypoint.sh"
EXPOSE 8000
USER app
