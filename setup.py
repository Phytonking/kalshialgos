from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kalshi-hedge-fund",
    version="0.1.0",
    author="Kalshi AI Hedge Fund Team",
    author_email="team@kalshi-hedge-fund.com",
    description="An open source framework for AI-powered hedge fund operations on Kalshi event contracts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/kalshi-hedge-fund",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kalshi-hedge-fund=kalshi_hedge_fund.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "kalshi_hedge_fund": ["config/*.yaml", "config/*.json"],
    },
)