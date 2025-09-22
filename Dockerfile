FROM ubuntu:noble

COPY ./scripts/install-dependencies ./install-dependencies

RUN ./install-dependencies

USER 1000

WORKDIR /home/ubuntu

CMD ["bash"]
