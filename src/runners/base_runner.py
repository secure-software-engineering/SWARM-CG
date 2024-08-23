import os
import time
import docker
from core import setup_logger, FileHandler

# Create a logger
logger = setup_logger("Base Runner", "base_runner.log")

KEEP_CONTAINERS_RUNNING = False


class BaseRunner:
    def __init__(
        self,
        tool_name,
        dockerfile_path,
        host_results_path,
        dockerfile_name="Dockerfile",
        volumes={},
        nocache=False,
        language=None,
        benchmark_name=None,
        models=None,
    ):
        try:
            self.docker_client = docker.from_env()
            # Test the connection
            self.docker_client.ping()
            logger.info("Docker client connected successfully.")
        except docker.errors.DockerException as e:
            logger.error(f"Error connecting to Docker: {e}")
            raise
        self.tool_name = tool_name
        self.dockerfile_path = dockerfile_path
        self.dockerfile_name = dockerfile_name
        self.test_runner_script_path = "/tmp/src/runner.py"
        self.benchmark_path = "/tmp/benchmarks"
        self.host_results_path = host_results_path
        self.volumes = volumes
        self.nocache = nocache
        self.language = language
        self.benchmark_name = benchmark_name
        self.models = models

        self.file_handler = FileHandler()

        if not os.path.exists(self.host_results_path):
            os.makedirs(self.host_results_path)

    def _build_docker_image(self):
        try:
            logger.info("Building image")
            image, _ = self.docker_client.images.build(
                path=self.dockerfile_path,
                tag=self.tool_name,
                dockerfile=self.dockerfile_name,
                nocache=self.nocache,
            )
            return image
        except docker.errors.BuildError as e:
            logger.error(f"Error building Docker image: {e}")
            raise

    def spawn_docker_instance(self):
        try:
            logger.info("Creating container")
            container = self.docker_client.containers.run(
                self.tool_name,
                detach=True,
                stdin_open=True,
                tty=True,
                volumes=self.volumes,
            )
            return container
        except docker.errors.APIError as e:
            logger.error(f"Error creating Docker container: {e}")
            raise

    # def setup_benchmark_external_library(self):
    #     _, response = self.container.exec_run("pip install typeevalpy-external-module", stream=True)

    def run_test_in_session(self):
        try:
            _, response = self.container.exec_run(
                f"python {self.test_runner_script_path}", stream=True
            )
            for line in response:
                logger.info(line)
        except Exception as e:
            logger.error(f"Error running test in container: {e}")
            raise

    def copy_results_from_container(self):
        try:
            self.file_handler.copy_files_from_container(
                self.container,
                self.benchmark_path,
                f"{self.host_results_path}/{self.tool_name}",
            )
        except Exception as e:
            logger.error(f"Error copying results from container: {e}")
            raise

    def run_tool_test(self):
        logger.info("#####################################################")
        logger.info(f"Running : {self.tool_name}")
        try:
            self._build_docker_image()
            self.container = self.spawn_docker_instance()

            # Construct the language-specific src path
            src = os.path.join("..", "benchmarks", self.language, self.benchmark_name)
            dst = "/tmp"
            self.file_handler.copy_files_to_container(self.container, src, dst)

            # self.setup_benchmark_external_library()
            logger.info("Benchmark files copied to container")
            logger.info("Call Graph Analysis...")
            start_time = time.time()

            try:
                self.run_test_in_session()
            except Exception as e:
                logger.error(f"Error during execution of run_test_in_session(): {e}")
                return  # Exit if this step fails

            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Execution time: {execution_time} seconds")

            try:
                self.copy_results_from_container()
            except Exception as e:
                logger.error(
                    f"Error during execution of copy_results_from_container: {e}"
                )

        except Exception as e:
            logger.error(f"Error during tool test: {e}")

        finally:
            if not KEEP_CONTAINERS_RUNNING:
                self.container.stop()
                time.sleep(5)
                self.container.remove()
