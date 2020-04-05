import setuptools
import chatalyzer

setuptools.setup(
    name='chatalyzer',
    version=chatalyzer.__version__,
    author="Haran Rajkumar, Vaibhav Kulshrestha",
    author_email="haranrajkumar97@gmail.com, vaibhav1kulshrestha@gmail.com",
    description="WhatsApp Chat Analyzer",
    url="https://github.com/haranrk/chatalyzer",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'tqdm',
        'Jinja2',
        'pandas'
        ],
    entry_points='''
        [console_scripts]
        chatalyze=chatalyzer.chatalyzer:main
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

