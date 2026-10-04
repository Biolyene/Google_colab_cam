from setuptools import setup, find_packages

setup(
    name="colabcam",
    version="0.2.0",
    description="Drop-in replacement for cv2 camera and imshow in Google Colab",
    author="Tee Yokky/Biolyene",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python-headless"
    ],
    python_requires=">=3.7",
)