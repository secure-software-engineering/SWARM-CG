# Use the official Node.js image as the base image
FROM node:20

# Set the working directory in the container
WORKDIR /app

# Install Python, pip, and build tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /venv

# Upgrade pip within the virtual environment
RUN /venv/bin/pip install --upgrade pip

# Install Esprima in the virtual environment
RUN /venv/bin/pip install esprima

# Install the required Node.js packages globally
RUN npm install -g @persper/js-callgraph

# Create a symbolic link for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set environment variables to use the virtual environment
ENV PATH="/venv/bin:$PATH"

# Example default command: Start a bash shell. You can override this during runtime.
CMD ["bash"]
