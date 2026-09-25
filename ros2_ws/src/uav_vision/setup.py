import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'uav_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[

        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'),
        glob('launch/*.launch.py')),


        (os.path.join('share', package_name, 'config'),
        glob('config/*.yaml')),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cole',
    maintainer_email='coltoncoey13@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'nav2_px4_adapter = uav_vision.nav2_px4_adapter:main',
            'object_detector = uav_vision.object_detector:main',
            'obstacle_sensor = uav_vision.obstacle_sensor:main',
        ],
    },
)
