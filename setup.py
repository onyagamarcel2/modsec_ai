from setuptools import setup, find_packages

setup(
    name="modsec_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "httpx>=0.28.0",
        "pytest>=8.0.0",
        "pytest-cov>=6.0.0"
    ],
    python_requires=">=3.8",
) 