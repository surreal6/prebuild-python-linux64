import docker
import os
import shutil
import tarfile

# Initialize the Docker client
client = docker.from_env()

# Define the image and container names
image_name = "python-64bit"
container_name = "python64"

# Step 1: Remove the image if it already exists
try:
    print(f"Checking if the image {image_name} exists...")
    image = client.images.get(image_name)
    print(f"Image {image_name} exists, removing it...")
    client.images.remove(image=image_name, force=True)
except docker.errors.ImageNotFound:
    print(f"Image {image_name} does not exist, proceeding...")

# Step 2: Build the Docker image
dockerfile_path = "python-64bit"  # Path to the Dockerfile
print(f"Building Docker image {image_name}...")

client.images.build(path=".", dockerfile=dockerfile_path, tag=image_name)

# Step 3: Remove the container if it already exists
try:
    print(f"Checking if the container {container_name} exists...")
    container = client.containers.get(container_name)
    print(f"Container {container_name} exists, removing it...")
    container.stop()
    container.remove()
except docker.errors.NotFound:
    print(f"Container {container_name} does not exist, proceeding...")

# Step 4: Run the Docker container with the specific name
print(f"Running Docker container {container_name}...")

container = client.containers.run(image_name, name=container_name, detach=False)

# Step 5: Copy files from the Docker container to the host
src_path = "/python-build"  # Path in the container
dest_path = "output"        # Destination path on the host

print(f"Copying files from {container_name}:{src_path} to {dest_path}...")

# Ensure the destination directory exists
os.makedirs(dest_path, exist_ok=True)

# Use the low-level API to copy files
archive_stream, _ = client.api.get_archive(container_name, src_path)

with open(os.path.join(dest_path, "output.tar"), "wb") as f:
    for chunk in archive_stream:
        f.write(chunk)

print(f"Files copied to {dest_path}")
# Cleanup: Stop and remove the container after use
container = client.containers.get(container_name)
container.stop()
container.remove()

print(f"Container {container_name} stopped and removed.")


print("Extracting python...")
# Ensure the extraction directory exists
os.makedirs("output/output", exist_ok=True)
with tarfile.open("output/output.tar", 'r') as tar:
    # Extract all the contents to the specified directory
    tar.extractall(path="output/output")

shutil.copytree("output/output/python-build/usr/local", "output/cpython-3.13.3-linux64")
