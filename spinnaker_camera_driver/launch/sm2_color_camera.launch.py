from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument as LaunchArg
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration as LaunchConfig
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare


camera_params = {
    'color': {
        'debug': False,
        'compute_brightness': True,
        'dump_node_map': False,
        'adjust_timestamp': False,
        'pixel_format': 'BayerRG8',  # Formato de pixel para câmeras coloridas
        'gain_auto': 'On',                  # Modificado para automático
        'gain': 0,
        'exposure_auto': 'On',              # Modificado para automático
        'exposure_time': 16667,             # Valor padrão quando automático está desligado
        'frame_rate': 59.99,
        'frame_rate_enable': True,
        'auto_exposure_lower_limit': 30,    # Limite mínimo (µs)
        'auto_exposure_upper_limit': 16797.84,  # Ajustado para valor máximo compatível
        'buffer_queue_size': 10,
        'line2_selector': 'Line2',
        'line2_v33enable': False,
        'line3_selector': 'Line3',
        'line3_linemode': 'Input',
        'trigger_selector': 'FrameStart',
        'trigger_mode': 'Off',
        'trigger_source': 'Line3',
        'trigger_delay': 29,                 # Valor original mantido para color
        'trigger_overlap': 'ReadOut',
        'chunk_mode_active': True,
        'chunk_selector_frame_id': 'FrameID',
        'chunk_enable_frame_id': True,
        'chunk_selector_exposure_time': 'ExposureTime',
        'chunk_enable_exposure_time': True,
        'chunk_selector_gain': 'Gain',
        'chunk_enable_gain': True,
        'chunk_selector_timestamp': 'Timestamp',
        'chunk_enable_timestamp': True,
        'binning_x': 1,
        'binning_y': 1,
    },
    'grayscale': {
        'debug': False,
        'compute_brightness': True,
        'dump_node_map': False,
        'adjust_timestamp': False,
        'gain_auto': 'On',                  # Já estava correto
        'gain': 0,
        'exposure_auto': 'On',              # Já estava correto
        'exposure_time': 16667,             # Valor padrão quando automático está desligado
        'frame_rate': 59.99,
        'auto_exposure_lower_limit': 30,     # Limite mínimo (µs)
        'auto_exposure_upper_limit': 16797.84,  # Máximo compatível
        'line2_selector': 'Line2',
        'line2_v33enable': False,
        'line3_selector': 'Line3',
        'line3_linemode': 'Input',
        'trigger_selector': 'FrameStart',
        'trigger_mode': 'Off',
        'trigger_source': 'Line3',
        'trigger_delay': 9,                  # Delay otimizado
        'trigger_overlap': 'ReadOut',
        'chunk_mode_active': True,
        'chunk_selector_frame_id': 'FrameID',
        'chunk_enable_frame_id': True,
        'chunk_selector_exposure_time': 'ExposureTime',
        'chunk_enable_exposure_time': True,
        'chunk_selector_gain': 'Gain',
        'chunk_enable_gain': True,
        'chunk_selector_timestamp': 'Timestamp',
        'chunk_enable_timestamp': True,
    }
}


def make_camera_node(name, cam_type, serial, camera_info_url, frame_id, camera_type):
    parameter_file = PathJoinSubstitution(
        [FindPackageShare('spinnaker_camera_driver'), 'config', cam_type + '.yaml']
    )
    return ComposableNode(
        package='spinnaker_camera_driver',
        plugin='spinnaker_camera_driver::CameraDriver',
        name=name,
        namespace=LaunchConfig('namespace'),
        parameters=[
            camera_params[camera_type],
            {   'parameter_file': parameter_file,
                'serial_number': serial,
                'camerainfo_url': camera_info_url,
                'frame_id': frame_id
            }
        ],
        remappings=[('~/control', '/exposure_control/control')],
        extra_arguments=[{'use_intra_process_comms': True}],
    )


def launch_setup(context, *args, **kwargs):
    camera_type = LaunchConfig('camera_type').perform(context)
    cam_type_0 = LaunchConfig('cam_0_type').perform(context)
    cam_type_1 = LaunchConfig('cam_1_type').perform(context)
    serial_0 = LaunchConfig('cam_0_serial').perform(context)
    name_0 = LaunchConfig('cam_0_name').perform(context)
    frame_0 = LaunchConfig('cam_0_frame_id').perform(context)
    serial_1 = LaunchConfig('cam_1_serial').perform(context)
    frame_1 = LaunchConfig('cam_1_frame_id').perform(context)
    name_1 = LaunchConfig('cam_1_name').perform(context)


    cam_0_camera_info_url = 'file://' + str(PathJoinSubstitution([
        FindPackageShare('spinnaker_camera_driver'), 'config', serial_0 + '.yaml'
    ]).perform(context))
    cam_1_camera_info_url = 'file://' + str(PathJoinSubstitution([
        FindPackageShare('spinnaker_camera_driver'), 'config', serial_1 + '.yaml'
    ]).perform(context))

    container = ComposableNodeContainer(
        name='camera_container',
        namespace=LaunchConfig('namespace'),
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            make_camera_node(name_0, cam_type_0, serial_0, cam_0_camera_info_url, frame_0, camera_type),
            make_camera_node(name_1, cam_type_1, serial_1, cam_1_camera_info_url, frame_1, camera_type),
        ],
        output='screen',
    )
    return [container]


def generate_launch_description():
    return LaunchDescription([
        LaunchArg('cam_0_name', default_value='left', description='Camera 0 name'),
        LaunchArg('cam_1_name', default_value='right', description='Camera 1 name'),
        LaunchArg('cam_0_type', default_value='blackfly_s', description='Camera 0 type'),
        LaunchArg('cam_1_type', default_value='blackfly_s', description='Camera 1 type'),
        LaunchArg('cam_0_serial', default_value='22548025', description='Camera 0 serial number'),
        LaunchArg('cam_1_serial', default_value='22548033', description='Camera 1 serial number'),
        LaunchArg('cam_0_frame_id', default_value='SM2/left_camera_link', description='Frame ID for camera 0'),
        LaunchArg('cam_1_frame_id', default_value='SM2/right_camera_link', description='Frame ID for camera 1'),
        LaunchArg('namespace', default_value='SM2', description='ROS namespace'),
        LaunchArg('camera_type', default_value='color', description='color or grayscale stereo system?'),
        OpaqueFunction(function=launch_setup),
    ])
