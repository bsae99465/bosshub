from setuptools import setup, find_packages

setup(
    name="bosshub",
    version="0.1.0",
    author="BossHub Team",
    author_email="dev@bosshub.io",
    description="Official Python Client for BossHub Cloud (IoT & Enterprise)",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md").exists() else "",
    long_description_content_type="text/markdown",
    url="https://github.com/bsae99465/bosshub",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        # (Optional) ถ้าอยากให้รันคำสั่ง 'bosshub' ใน terminal ได้เลย
        # 'console_scripts': [
        #     'bosshub=bosshub.cli:main',
        # ],
    },
)
