from setuptools import setup, find_packages

setup(
    name="kitchnspy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "fastapi",
        "uvicorn",
        "matplotlib",
        "schedule"
    ],
    entry_points={
        "console_scripts": [
            "kitchinspy=kitchinspy.__main__:main"
        ]
    },
    author="DesayoEm",
    description="A KitchenAid price tracker with email alerts and visualizations.",
    include_package_data=True,
    zip_safe=False,
)
