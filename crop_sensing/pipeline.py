# This function is used to test the functionalities of the crop sensing module
from crop_sensing import cobot_manager, create_plc, find_plant, zed_manager


def main():
    linux_ip = "192.168.5.100"  # Replace with the actual IP address
    plants_number = 2  # Number of plants to detect
    # Get the current pose of the cobot
    pose = cobot_manager.get_cobot_pose(linux_ip)

    # Initialize the ZED camera
    zed = zed_manager.zed_init(pose)
    
    # Capture the environment with the ZED camera
    image, depth_map, normal_map, point_cloud = zed_manager.get_zed_image(zed, save=True)

    # Filter the plants from the background
    mask = find_plant.filter_plants(image, save_mask=True)
    
    # Divide the plants into clusters
    masks, bounding_boxes = find_plant.segment_plants(mask, plants_number)
    find_plant.save_clustered_image(image, bounding_boxes)

    # Extract the 3D points from the clusters
    all_bounding_boxes = []
    for i, m in enumerate(masks):
        bbxpts = find_plant.get_3d_bbox(m, point_cloud)
        all_bounding_boxes.append(bbxpts)
        
        # Communicate each bounding box to the cobot (only if the cobot is operated in another machine)
        try:
            cobot_manager.send_cobot_map(linux_ip, bbxpts)
        except Exception as e:
            print(f"Error sending bounding box {i+1}: {e}")
            continue

    # Create point cloud (this will create a .ply file by taking a video of the environment)
    create_plc.record_and_save(plant_name='piantina1', frames=300)

    zed.close()