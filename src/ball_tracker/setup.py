from setuptools import setup
import os
from glob import glob

package_name = 'ball_tracker'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],

    data_files=[
        # REQUIRED for ROS2 package recognition
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # package.xml
        ('share/' + package_name, ['package.xml']),

        # launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),

        # world files
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.world')),

        # urdf/xacro files
        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='Ball tracking robot nodes',
    license='Apache-2.0',

    entry_points={
        'console_scripts': [
            'perception_node = ball_tracker.perception_node:main',
            'control_node = ball_tracker.control_node:main',
        ],
    },
)
