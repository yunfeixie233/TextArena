from setuptools import setup, find_packages

setup(
    name="textarena",                        # Package name
    version="0.1.0",                         # Initial release version
    description="A collection of competitive text-based games for language model evaluation and reinforcement learning.",
    author="Leon Guertler",              # Replace with your name
    author_email="guertlerlo@cfar.a-star.edu.sg",   # Replace with your email
    url="https://github.com/yourusername/textarena",  # Replace with your GitHub repo
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "openai",          # Example dependencies
        "tqdm",
        "pytest"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
