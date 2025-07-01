from setuptools import setup, find_packages, find_namespace_packages

setup(
    name="textarena",
    version="0.6.9",
    url="https://github.com/LeonGuertler/TextArena",
    author="Leon Guertler",
    author_email="Guertlerlo@cfar.a-star.edu.sg",
    description="A Collection of Competitive Text-Based Games for Language Model Evaluation and Reinforcement Learning",
    packages=find_namespace_packages(include=["textarena", "textarena.*"]),
    include_package_data=True,
    package_data={
        "": ["*.json"],  # Include all JSON files in any package
        "": ["*.jsonl"],  # Include all JSON files in any package
        "textarena": ["envs/**/*.json"],  # Recursive include from textarena root
    },
    install_requires=["openai", "rich", "nltk", "chess", "python-dotenv" , "requests", "websockets"],
    python_requires='>=3.10',
)
