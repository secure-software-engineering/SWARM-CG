import docker

def test_docker_connection():
    try:
        client = docker.from_env()
        print("Docker client connected successfully.")
        print("Docker version:", client.version())
    except docker.errors.DockerException as e:
        print("Error connecting to Docker:", e)

if __name__ == "__main__":
    test_docker_connection()
