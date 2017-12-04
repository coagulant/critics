FROM python:3.6-slim
MAINTAINER The MyBook Developers <dev@mybook.ru>

RUN groupadd critics && useradd --no-create-home --gid critics critics

COPY . /tmp/critics
WORKDIR /tmp/critics
RUN pip install -e .

EXPOSE 9137
VOLUME [ "/critics" ]
WORKDIR /critics
RUN chown -R critics:critics /critics
USER critics
ENTRYPOINT [ "/usr/local/bin/critics" ]
