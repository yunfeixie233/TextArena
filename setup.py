from setuptools import setup, find_packages

setup(
    name="textarena",
    version="0.1.2",
    url="https://github.com/LeonGuertler/TextArena",
    author="Leon Guertler",
    author_email="Guertlerlo@cfar.a-star.edu.sg",
    description="[WIP] A Collection of Competitive Text-Based Games for Language Model Evaluation and Reinforcement Learning",
    # packages=find_packages(),
    packages=find_packages(include=["textarena", "textarena.*"]),
    include_package_data=True,
    package_data={
        "textarena": ["textarena/envs/two_player/TruthAndDeception/facts.json"],
    },
    install_requires=[],  # fill in later
)
