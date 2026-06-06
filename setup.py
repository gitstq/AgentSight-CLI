"""Setup configuration for AgentSight-CLI."""

from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().strip().split("\n")

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentsight-cli",
    version="1.0.0",
    description="Lightweight terminal AI Agent multi-source web data collection and structured extraction engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AgentSight Team",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "agentsight=agentsight.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
