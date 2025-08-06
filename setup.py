"""Setup configuration for bystronic-opc package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bystronic-opc",
    version="0.1.0",
    author="Daniel Risto",
    author_email="daniel@risto.de",
    description="Python library for connecting to Bystronic laser cutting machines via OPC UA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danielristo/bystronic-opc",
    project_urls={
        "Bug Tracker": "https://github.com/danielristo/bystronic-opc/issues",
        "Documentation": "https://bystronic-opc.readthedocs.io/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
        ],
        "web": [
            "flask>=2.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bystronic-monitor=bystronic_opc.cli:main",
            "bystronic-web=bystronic_opc.web:main",
        ],
    },
    keywords="opc-ua, bystronic, laser-cutting, manufacturing, industry-4.0",
    include_package_data=True,
    zip_safe=False,
)