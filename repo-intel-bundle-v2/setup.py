from setuptools import setup, find_packages

setup(
    name="repo-intel-bundle-v2",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp[cli]>=0.5.0",
        "requests",
        "python-dotenv",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "repo-intel=server:main",
        ],
    },
)
