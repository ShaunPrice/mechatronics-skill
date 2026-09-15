# Official ROS 2 Jazzy image, verified Linux arm64 installation on 2026-09-15.
ARG ROS_IMAGE=ros:jazzy-ros-base@sha256:386d06ec6d4188f731bae5678e07b4cb64a4e4d4152090c0bd1f881dcf7706f5
FROM ${ROS_IMAGE}

# Build dependencies are installed only in this image. No host packages change.
RUN apt-get update \
    && apt-get install --no-install-recommends -y python3-colcon-common-extensions python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_LOCALHOST_ONLY=1 \
    ROS_DOMAIN_ID=73 \
    RMW_IMPLEMENTATION=rmw_fastrtps_cpp
WORKDIR /workspace
CMD ["sleep", "infinity"]
