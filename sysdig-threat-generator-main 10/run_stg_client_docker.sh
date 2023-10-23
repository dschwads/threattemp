#!/bin/bash
docker run -it --rm -v $HOME/.aws:/root/.aws -v $HOME/.config/gcloud:/root/.config/gcloud -v $HOME/.azure:/root/.azure sysdig-threat-generator:latest /bin/bash
