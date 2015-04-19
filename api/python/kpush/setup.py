from setuptools import setup, find_packages
setup(
    name="kpush",
    version="0.1.0",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=["requests"],
    scripts=[],
    url="https://github.com/dantezhu/kpush",
    license="MIT",
    author="dantezhu",
    author_email="dantezhu@qq.com",
    description="kpush client api",
)
