# Triton control panel
Web interface for managing the processes of working with neural network models uploaded to the Triton inference server

Triton inference server is an open source tool for deploying deep learning models in a production environment. Triton Inference Server allows you to deploy prepared AI models from frameworks (TensorFlow, PyTorch, TensorRT Plan, Caffe, MXNet or Custom) on local storage, Google Cloud platform or AWS S3 on any GPU or CPU based infrastructure.


## Technology stack
The technology stack used includes:
- [`Python`](https://www.python.org) ver. 3.11
- [`Flask`](https://flask.palletsprojects.com) ver. 2.2.3
- [`PostgreSQL`](https://www.postgresql.org) ver. 15.2
- [`Gunicorn`](https://gunicorn.org) ver. 20.1
- [`Nginx`](https://nginx.org) ver. 1.20
- [`Docker`](https://docs.docker.com/get-docker/) and [`Docker Compose`](https://docs.docker.com/compose/)

Nothing extra, only the essentials! You can easily add everything else yourself by expanding the existing configuration files:
- [requirements.txt](https://github.com/f1rezy/triton-panel/blob/master/app/requirements.txt)
- [docker-compose.yml](https://github.com/f1rezy/triton-panel/blob/master/docker-compose.yml)
- and others...

## Deploy
Build the images and spin up the containers:

```sh
$ docker-compose up --build
```
