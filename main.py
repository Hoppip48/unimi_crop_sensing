import cv2
import zed_manager
import find_plant
import cobot_manager



def main():
    # init magic numbers
    linux_ip = "192.168.5.6"
    plants_number = 2
    
    # Ottieni translazione e orientamento del cobot
    pose = cobot_manager.get_cobot_pose(linux_ip)
    # Inizializza la ZED
    zed = zed_manager.zed_init(pose)
    
    # Acquisisci l'immagine e la mappa di profondità
    image, depth_map, normal_map, point_cloud = zed_manager.get_zed_image(zed)
    
    # Trova il più grande cluster di verde
    mask = find_plant.find_excess_green(image, kernel_dimension=0, cut_iterations=2)
    
    # Dividi la maschera di ogni piantina
    masks, bounding_boxes = find_plant.segment_plants(mask, plants_number)
    
    # Draw bounding boxes on the original mask for visualization
    for (x_min, y_min, x_max, y_max) in bounding_boxes:
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.imwrite("data/clusters.png", image)
    
    for m in masks:
        # Localizza l'area 3D che contiene il cluster 
        bbxpts = find_plant.plot_3d_bbox(m, point_cloud)
        
    # Comunicala al Cobot e acquisci ply
    #cobot_manager.send_cobot_map(linux_ip, bbxpts)
    
    # Analizza ply
    


if __name__ == "__main__":
    main()
    

