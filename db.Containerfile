# Pull base image from docker.io.
# Specify platform for those on, for example, Apple M1 machines.
FROM --platform=linux/amd64 docker.io/library/postgres:14

ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=tams

EXPOSE 5432