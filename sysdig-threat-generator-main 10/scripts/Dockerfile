FROM python:3.9-slim as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

from base AS python-deps

RUN pip install pipenv
run apt-get update && apt-get install -y gcc curl
COPY ./scripts/Pipfile .
COPY ./scripts/Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime
COPY --from=python-deps /.venv /.venv
# copy in pipenv
ENV PATH="/.venv/bin:$PATH"
RUN apt-get update && apt-get install -y wget unzip

WORKDIR /home
# get tf
RUN wget https://releases.hashicorp.com/terraform/1.2.4/terraform_1.2.4_linux_amd64.zip
RUN unzip terraform_1.2.4_linux_amd64.zip
RUN mv ./terraform /usr/bin/
RUN terraform -help

COPY ./scripts/* .
COPY ./tf_fargate/*.tf .
ENTRYPOINT ["/bin/bash"]
#CMD ["--help"]
