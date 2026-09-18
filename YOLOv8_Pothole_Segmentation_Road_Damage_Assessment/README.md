### 🛣️ Real-Time Pothole Segmentation for Road Damage Assessment with YOLOv8
![Pothole Segmentation](/images/cover_image_raw.png)

## 🔍 Overview
This project leverages YOLOv8-seg's cutting-edge segmentation capabilities for real-time road damage assessment, with a particular emphasis on pothole detection. It aims to bolster road maintenance efforts by providing precise, real-time data on road conditions, thereby enhancing public safety and aiding in urban infrastructure management. Combining computer vision with advanced object segmentation, our solution delineates potholes in detail, offering actionable insights for smart city and autonomous vehicle advancements.


## 🎯 Objectives
Key milestones in this project include:
* **Speed-Oriented YOLOv8n-seg Selection:** Adopting YOLOv8n-seg for its quick processing, balancing speed with accuracy, ideal for real-time pothole analysis.
* **Targeted Dataset Preparation:** Creating a curated dataset of pothole imagery, augmented to train the model effectively for segmentation tasks.
* **YOLOv8-seg Fine-Tuning:** Adapting the pre-trained model via transfer learning to pinpoint and segment potholes with high precision.
* **Comprehensive Model Evaluation:** Utilizing various metrics and analyses to validate the model's performance and ensure its dependability.
* **Model Inference Testing:** Assessing the model on validation images and a novel test video to confirm its real-world applicability.
* **Real-Time Damage Assessment:** Implementing the model on video feeds to continuously monitor and quantify pothole-inflicted road damage.


## 📚 Dataset Description

### 🌐 Overview
The [**Pothole Detection for Road Safety Dataset**](https://www.kaggle.com/datasets/farzadnekouei/pothole-image-segmentation-dataset) is purpose-built for training YOLOv8-seg models to identify and segment potholes.

### 🔍 Specifications 
- 🕳️ **Class**: 'Pothole' 
- 🖼️ **Total Images**: 780
- 📏 **Image Dimensions**: 640x640 pixels
- 📂 **Format**: YOLOv8 annotation format

### 🔄 Pre-processing
Includes auto-orientation and resizing to 640x640 for consistency.

### 🔢 Dataset Split
- **Training Set**: 720 images with augmentations.
- **Validation Set**: 60 images.

### 🎭 Augmentation on Training Set
Comprising flips, cropping, rotation, shearing, brightness, and exposure adjustments.

### 📌 Access
Publicly accessible on Kaggle and Roboflow:
- [Kaggle Dataset](https://www.kaggle.com/datasets/farzadnekouei/pothole-image-segmentation-dataset)
- [Roboflow Project](https://universe.roboflow.com/farzad/pothole_segmentation_yolov8/dataset/1)


## 🎥 YouTube Demo
Real-Time Pothole Segmentation for Road Damage Assessment with YOLOv8 in Action:

[![Pothole Segmentation Demo](https://img.youtube.com/vi/1YkmlMbjwxY/0.jpg)](https://youtu.be/1YkmlMbjwxY)  


## 📁 File Descriptions

- **`images/`**: Contains the cover images for the project and the sample image utilized within the notebook.
- **`model/`**: Includes the best-performing fine-tuned YOLOv8 model in `.pt` (PyTorch format) used for pothole segmentation.
- **`pothole_segmentation_YOLOv8.ipynb`**: The Jupyter notebook that documents the model development pipeline, from data preparation to model evaluation and inference.
- **`road_damage_assessment_app.py`**: The Python script for deploying the YOLOv8 segmentation model to estimate road damage in real-time.
- **`road_survey.py`**: Live webcam + ESP32 GPS survey tool. Detects potholes in real time and geotags each detection with a saved image and a CSV log entry.
- **`sample_video.mp4`**: A sample video file used to demonstrate the application's capabilities.
- **`real_time_road_damage_assessment_demo.gif`**: A GIF showcasing the application's real-time road damage assessment.
- **`LICENSE`**: Outlines the terms of use for this project's resources.
- **`README.md`**: The document you are reading that provides an overview and essential details of the project.


## 🚀 Instructions for Local Execution

To experience the full capabilities of the YOLOv8 Traffic Density Estimation project on your local machine, follow these steps:

### 1️⃣. Initial Setup
1. **Clone the Repository**: Start by cloning the project repository to your local system using the command below:
    ```bash
    git clone https://github.com/FarzadNekouee/YOLOv8_Pothole_Segmentation_Road_Damage_Assessment.git
    ```
2. **Navigate to the Project Directory**: After cloning, change into the project directory with:
    ```bash
    cd YOLOv8_Pothole_Segmentation_Road_Damage_Assessment
    ```

### 2️⃣. Exploring the Model Development Pipeline
Get hands-on with the model development process and see the results of traffic density estimation:
1. **Download the Dataset**: Access the dataset from [Kaggle](https://www.kaggle.com/datasets/farzadnekouei/pothole-image-segmentation-dataset). Download and extract it to a known directory on your machine.
2. **Open the Notebook**: Launch Jupyter Notebook or JupyterLab and open `real-pothole_segmentation_YOLOv8.ipynb` to explore the model development pipeline.
3. **Install Dependencies**: Ensure all necessary Python libraries are installed for flawless execution.
4. **Update Paths**: Update the paths in the notebook for the dataset, sample image, and sample video to their respective locations on your local system.
5. **Run the Notebook**: Execute all cells in the notebook to step through the data preprocessing, model training, and evaluation phases.

### 3️⃣. Watching the Real-Time Performance
Witness the real-time road damage assessment capability of our application:
1. **Install Ultralytics YOLO**: Ensure you have the `ultralytics` package installed by running:
    ```bash
    pip install ultralytics
    ```
2. **Run the Analysis Script**: Execute the script to start the real-time traffic density estimation:
    ```bash
    python road_damage_assessment_app.py
    ```
3. **Real-Time Analysis**: The video window will display the live road damage assessment. To exit, simply press 'q' while the video window is active.

This GIF showcases our application running in real-time:

![Real-Time Road Damage Assessment GIF](real_time_road_damage_assessment_demo.gif) 


## 🛰️ Live Road Survey Mode (ESP32 GPS)

`road_survey.py` turns the model into a geotagged pothole survey tool: live webcam feed, on-device detection, and GPS coordinates pulled from an ESP32 over USB serial.

### Hardware / Protocol
- ESP32 connected via USB serial, sending one JSON line per GPS fix:
    ```json
    {"lat": 12.345678, "lon": 77.123456}
    ```
- Configure `SERIAL_PORT` and `SERIAL_BAUD` at the top of `road_survey.py` to match your device (default `COM3` / `115200`).

### Behavior
- On each pothole detection, saves the frame to `survey_output/images/` and appends a row (`timestamp`, `latitude`, `longitude`, `image_path`, `damage_percent`) to `survey_output/survey_log.csv`.
- A 2-second cooldown between saves avoids flooding the disk while a pothole stays in frame.
- If no GPS fix is available yet, the entry is still saved and tagged `NOFIX`.

### Run
```bash
pip install pyserial
python road_survey.py
```
Press `q` to stop. To verify the GPS line parser without hardware attached:
```bash
python road_survey.py --selftest
```


## 🔗 Additional Resources

- 🎥 **Project Demo**: Watch the live demonstration of this project on [YouTube](https://www.youtube.com/watch?v=1YkmlMbjwxY).
- 🌐 **Kaggle Notebook**: Interested in a Kaggle environment? Explore the notebook [here](https://www.kaggle.com/code/farzadnekouei/pothole-segmentation-for-road-damage-assessment).
- 🌐 **Dataset Source**: Available on both [Roboflow](https://universe.roboflow.com/farzad/pothole_segmentation_yolov8/dataset/1) and [Kaggle](https://www.kaggle.com/datasets/farzadnekouei/pothole-image-segmentation-dataset).
- 🤝 **Connect on LinkedIn**: Have questions or looking for collaboration? Let's connect on [LinkedIn](https://linkedin.com/in/farzad-nekouei-7535aa53/).