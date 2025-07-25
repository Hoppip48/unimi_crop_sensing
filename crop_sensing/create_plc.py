import pyzed.sl as sl
import time
import sys

import pyzed.sl as sl

def initialize_zed(zed, mesh=True):
    # Set configuration parameters
    init_params = sl.InitParameters()
    
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS  # Use Neural Plus depth sensing mode
    init_params.camera_resolution = sl.RESOLUTION.HD2K  # Set the camera resolution 
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP # Use a right-handed Y-up coordinate system
    init_params.coordinate_units = sl.UNIT.METER  # Set units in meters
    init_params.depth_maximum_distance = 5  # Set the maximum depth sensing distance to 1m
    init_params.depth_minimum_distance = 0.2  # Set the minimum depth sensing distance to 0.2m

    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Failed to open ZED camera: {err}")
        exit(1)

    # Set positional tracking parameters
    tracking_parameters = sl.PositionalTrackingParameters()
    
    # Set spatial mapping parameters
    mapping_parameters = sl.SpatialMappingParameters()
    
    mapping_parameters.resolution_meter = 0.01 # Set the map resolution to 1 cm
    mapping_parameters.range_meter = 2 # Set the mapping range to 2 meter
    
    if mesh:
        mapping_parameters.map_type = sl.SPATIAL_MAP_TYPE.MESH # Use mesh mapping
    else:
        mapping_parameters.map_type = sl.SPATIAL_MAP_TYPE.FUSED_POINT_CLOUD # Use point cloud mapping
    
    # Set mesh filter parameters
    filter_params = sl.MeshFilterParameters()
    filter_params.set(sl.MESH_FILTER.LOW)
      
    # Set runtime parameters
    runtime_parameters = sl.RuntimeParameters()
    runtime_parameters.confidence_threshold = 1  # Set confidence threshold to 0

    # Enable positional tracking
    zed.enable_positional_tracking(tracking_parameters)
    zed.enable_spatial_mapping(mapping_parameters) 
    
    return runtime_parameters, filter_params

def record_and_save(plant_name='plant',frames=300):
    """
    Captures spatial mapping data from a ZED camera over a specified number of frames,
    extracts the spatial mesh, and saves it as a PLY file

    Args:
        plant_name (str): Name used for saving the output PLY file (e.g., "plant1")
        frames (int): Number of frames to capture during spatial mapping

    Raises:
        RuntimeError: If the camera fails to initialize or grab frames
    """
    # Create a ZED camera object
    zed = sl.Camera()
    
    # Initialize the ZED camera with the configuration parameters
    runtime_parameters, filter_params = initialize_zed(zed, False)  
    
    # Create a PLY object
    py_point_cloud = sl.FusedPointCloud() 

    # Grab data 
    timer = 0
    while timer <= frames:
        # Grab a new image and depth map
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            mapping_state = zed.get_spatial_mapping_state()

        # DEBUG: Print spatial mapping state
        print("\rImages captured: {0} / {2} || {1}".format(timer, mapping_state, frames))
        
        timer = timer + 1
                        

    # Extract the mesh
    zed.extract_whole_spatial_map(py_point_cloud) 
         
    # Save the mesh
    py_point_cloud.save(f"data\{plant_name}.ply") 
    
    # Disable configurations and close the camera
    zed.disable_spatial_mapping()
    zed.disable_positional_tracking()
    zed.close()
    
        
if __name__ == "__main__":
    record_and_save()