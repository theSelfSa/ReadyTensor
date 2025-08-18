from setuptools import setup, find_packages

setup(
    name="ReadyTensor",
    version="1.0.0", 
    packages=find_packages(),
    package_data={
        "ReadyTensor": ["config/*.json", "config/scoring/*.yaml", "config/*.yaml"]
    },
    include_package_data=True,
)
