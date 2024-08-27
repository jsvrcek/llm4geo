from setuptools import setup, find_packages

setup(
    name="llm4geo",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["django", "langchain", "langchain-openai"],
)
