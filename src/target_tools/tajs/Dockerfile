# Use an Ubuntu base image that supports Python 3.10 natively
FROM ubuntu:22.04

# Set working directory
WORKDIR /usr/src/app

# Install necessary packages: Java, Ant, Git, Node.js, Python 3.10, Graphviz
RUN apt-get update && \
    apt-get install -y \
    openjdk-11-jdk \
    ant \
    git \
    curl \
    graphviz \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (version 14.x)
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs

# Clone TAJS repository and submodules
RUN git clone --recursive https://github.com/cs-au-dk/TAJS.git .

# Update submodules just in case
RUN git submodule update --init --recursive

# Build TAJS using Ant
RUN ant

COPY src /tmp/src
# create a system link to python3.10
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Define an entry point to run TAJS analysis. You can modify it as needed.
# ENTRYPOINT ["java", "-jar", "dist/tajs-all.jar"]

# Example default command: Analyze a sample JavaScript file. You can override this during runtime.
CMD ["bash"]
