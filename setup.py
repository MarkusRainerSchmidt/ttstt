import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TTsTT-server",
    version="0.0.1",
    author="Markus Schmidt",
    author_email="markus.rainer.schmidt@gmail.com",
    description="Server for the TableTop Simulator TerrainTool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarkusRainerSchmidt/ttstt",
    project_urls={
        "Bug Tracker": "https://github.com/MarkusRainerSchmidt/ttstt/issues",
    },
    include_package_data=True,
    packages=setuptools.find_packages(include=["ttstt"]),
    install_requires=['Flask', 'gunicorn', 'numpy', 'easygui', 'pypng', 'git+https://github.com/pvigier/perlin-numpy'],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
