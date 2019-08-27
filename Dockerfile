FROM node:8-alpine AS build
WORKDIR /xl_auth
COPY . .
RUN rm -rf *venv/ && rm -f assets/.DS_Store && npm install && npm run build && rm -rf node_modules/

FROM python:3.6-slim
ENV FLASK_DEBUG=1
ENV FLASK_APP=autoapp.py
ENV BABEL_DEFAULT_LOCALE=sv

WORKDIR /xl_auth
COPY --from=build /xl_auth .
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && pip --no-cache-dir --disable-pip-version-check install -r requirements.txt \
    && flask translate --compile-only && rm -f dev.db && flask db upgrade && flask clean \
    && apt-get --purge autoremove -y git && apt-get autoclean && rm -rf /var/lib/apt/lists/*

EXPOSE 5000

CMD ["prod-run"]
ENTRYPOINT ["flask"]
