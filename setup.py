from setuptools import setup, find_packages

setup(
    name="schedplus",
    version="0.7.3",
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    install_requires=[
        "PyQt6>=6.11.0",
        "babel>=2.18.0",
        "PyQt6-Qt6>=6.11.1",
        "PyQt6_sip>=13.11.1",
        "tkcalendar>=1.6.1"
    ],

    entry_points={
        "console_scripts": [
            "schedplus = schedplus.__main__:boot"
        ]
    },

    include_package_data=True,
    python_requires=">=3.10",
)
