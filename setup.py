from pathlib import Path

from setuptools import find_packages, setup # type: ignore

BASE_DIR = Path(__file__).resolve().parent
REQUIREMENTS = [
    line.strip()
    for line in (BASE_DIR / 'requirements.txt').read_text(encoding='utf-8').splitlines()
    if line.strip() and not line.startswith('#')
]

setup(
    name='ai-systems-project',
    version='0.1.0',
    author='Md. Ragib Ashhab',
    author_email='ragibashhab2733@gmail.com',
    description='A project implementing fuzzy logic, reinforcement learning, and data-driven AI systems.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=REQUIREMENTS,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)