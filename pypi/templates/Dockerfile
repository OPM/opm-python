FROM quay.io/pypa/%%DOCKER_IMAGE_NAME%% AS stage1
RUN yum -y update && yum -y install sudo
# We will map the host directory to /tmp/opm/opm-python in "docker run" command

# Create a new user with the same UID and GID as the host user
ARG HOST_UID    # Supplied by the build script as --build-arg
ARG HOST_GID    # Supplied by the build script as --build-arg
ARG username=dockeruser
RUN groupadd -g ${HOST_GID} ${username} && \
    useradd -u ${HOST_UID} -g ${HOST_GID} -m ${username}

# Allow the new user to use sudo without a password
RUN echo "${username} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create and set the correct ownership of the work directory
RUN mkdir -p /tmp/opm && \
    chown ${HOST_UID}:${HOST_GID} /tmp/opm
WORKDIR /tmp/opm
# Switch to the new user
USER ${username}

COPY --chown=${username}:${username} ./manylinux-build.sh .
RUN chmod +x manylinux-build.sh

ENTRYPOINT ["./manylinux-build.sh"]
