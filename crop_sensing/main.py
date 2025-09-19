import zed_manager
import find_plant
import cobot_manager
import create_plc
import cv2

# testing parameters
linux_ip = "192.168.5.6"
plants_number = 10

# This function is used to test the functionalities of the crop sensing module
def main():

    # Initialize the ZED camera
    zed = zed_manager.zed_init()
    
    # Start loop
    frame = 1
    for frame in range(100):
        # Capture the environment with the ZED camera
        image, depth_map, normal_map, point_cloud = zed_manager.get_zed_image(zed, save=False)

        # Filter the plants from the background
        mask = find_plant.filter_plants(image, save_mask=False)
        
        # Divide the plants into clusters
        masks, bounding_boxes = find_plant.segment_plants(mask, plants_number)        # Save bounding boxes to a txt file in crop_sensing/data
        find_plant.save_clustered_image(image, bounding_boxes)
        
        # Extract the 3D points from the clusters
        log_file = "crop_sensing/data/log.txt"
        i = 1
        for m, bbx in zip(masks, bounding_boxes):
            bbxpts = find_plant.plot_3d_bbox(m, point_cloud)
            #image = find_plant.draw_3d_bbox(image, bbxpts, K)
            # Logging
            with open(log_file, "a") as f: 
                x0, y0, z0 = map(float, (bbxpts["min"]["x"], bbxpts["min"]["y"], bbxpts["min"]["z"]))
                x1, y1, z1 = map(float, (bbxpts["max"]["x"], bbxpts["max"]["y"], bbxpts["max"]["z"]))
                f.write(
                    f"Frame {frame}, Piantina #{i}: "
                    f"Min(x:{x0}, y:{y0}, z:{z0}), "
                    f"Max(x:{x1}, y:{y1}, z:{z1})\n"
                    )
                i += 1
        frame += 1
        
    # Communicate the bounding boxes to the cobot (only if the cobot is operated in another machine)
    #cobot_manager.send_cobot_map(linux_ip, bbxpts)

    zed.close()
    
    # Create point cloud (this will create a .ply file by taking a video of the environment)
    #create_plc.record_and_save(plant_name='piantina1', frames=300)



if __name__ == "__main__":
    main()
    

