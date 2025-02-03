from setuptools import setup, find_packages

setup(
    name="textarena",
    version="0.3.2",
    url="https://github.com/LeonGuertler/TextArena",
    author="Leon Guertler",
    author_email="Guertlerlo@cfar.a-star.edu.sg",
    description="[WIP] A Collection of Competitive Text-Based Games for Language Model Evaluation and Reinforcement Learning",
    packages=find_packages(include=["textarena", "textarena.*"]),
    include_package_data=True,
    package_data={
        "": ["*.json"],  # Include all JSON files in any package
        "textarena.envs.two_player.TruthAndDeception": ["*.json"],  # Explicitly include JSON files in this directory
        "textarena": ["envs/**/*.json"],  # Recursive include from textarena root
    },
    install_requires=[
        "requests",
        "aiohttp",
        "backoff",
        "rich",
        "networkx",
        "importlib",
        "openai",
        "imageio",
        "imageio[ffmpeg]",
        "e2b_code_interpreter",
        "importlib",
        "transformers",
        "playwright",
        "opencv-python",
        "chess",
        "pyenchant"
    ],
    python_requires='>=3.9',
)
