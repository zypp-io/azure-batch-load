from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fp:
    install_requires = fp.read()

setup(
    name="azurebatchload",
    version="0.0.1",
    author="Erfan Nariman",
    author_email="erfannariman@gmail.com",
    description="Download files in batches from Azure Blob Storage Containers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="python, azure, blob, download, batch",
    url="https://github.com/erfannariman/azure-batch",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={"console_scripts": ["run=df_to_azure.export:run"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    project_urls={
        "Bug Reports": "https://github.com/erfannariman/azure-batch/issues",
        "Source": "https://github.com/erfannariman/azure-batch",
    },
)
