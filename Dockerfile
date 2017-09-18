FROM node:8-alpine AS build
WORKDIR /xl_auth
COPY . .
RUN rm -rf *venv/ && rm -f assets/.DS_Store && npm install && npm run build && rm -rf node_modules/

FROM python:3.6-slim
WORKDIR /xl_auth
COPY --from=build /xl_auth .
ENV FLASK_DEBUG=1
ENV FLASK_APP=autoapp.py
RUN pip --no-cache-dir install -r requirements.txt && rm -f dev.db && flask db upgrade

EXPOSE 5000

CMD ["run", "-h", "0.0.0.0"]
ENTRYPOINT ["flask"]
