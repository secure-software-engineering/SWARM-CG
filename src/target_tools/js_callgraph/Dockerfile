# Use the official Node.js image as the base image
FROM node:20

# Set the working directory in the container
WORKDIR /app

# Clone the GitHub repository into the container
RUN npm install -g @persper/js-callgraph

RUN ln -s /usr/bin/python3 /usr/bin/python

# Example default command: Analyze a sample JavaScript file. You can override this during runtime.
CMD ["bash"]
