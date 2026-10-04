from setuptools import setup, find_packages

setup(
    name="colabcam",
    version="0.1.0",
    description="A lightweight OpenCV camera capture tool tailored for Google Colab and tablets",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python-headless"
    ],
    python_requires=">=3.7",
)