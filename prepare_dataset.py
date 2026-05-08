import os
import shutil

SOURCE_DIR = r"C:\Users\Ritesh\Downloads\archive (5)\PlantVillage"

POTATO_DEST = "dataset/potato"
TOMATO_DEST = "dataset/tomato"

POTATO_CLASSES = {
    "Potato___Early_blight": "Early_Blight",
    "Potato___Late_blight":  "Late_Blight",
    "Potato___healthy":      "Healthy",
}

TOMATO_CLASSES = {
    "Tomato_Bacterial_spot":                       "Bacterial_Spot",
    "Tomato_Early_blight":                         "Early_Blight",
    "Tomato_Late_blight":                          "Late_Blight",
    "Tomato_Leaf_Mold":                            "Leaf_Mold",
    "Tomato_Septoria_leaf_spot":                   "Septoria_Leaf_Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Spider_Mites",
    "Tomato__Target_Spot":                         "Target_Spot",
    "Tomato__Tomato_mosaic_virus":                 "Mosaic_Virus",
    "Tomato__Tomato_YellowLeaf__Curl_Virus":       "Yellow_Leaf_Curl_Virus",
    "Tomato_healthy":                              "Healthy",
}

def copy_classes(source_dir, class_map, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for original_name, clean_name in class_map.items():
        src = os.path.join(source_dir, original_name)
        dst = os.path.join(dest_dir, clean_name)
        if not os.path.exists(src):
            print(f"Skipping (not found): {original_name}")
            continue
        if os.path.exists(dst):
            print(f"Already exists: {clean_name}")
            continue
        print(f"Copying {original_name} → {clean_name}")
        shutil.copytree(src, dst)

def count_images(base_dir):
    total = 0
    for class_name in sorted(os.listdir(base_dir)):
        class_path = os.path.join(base_dir, class_name)
        if os.path.isdir(class_path):
            count = len([
                f for f in os.listdir(class_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])
            print(f"  {class_name:<40} {count:>5} images")
            total += count
    print(f"  {'TOTAL':<40} {total:>5} images")

if not os.path.exists(SOURCE_DIR):
    print(f"ERROR: Source folder not found: {SOURCE_DIR}")
else:
    print("Setting up Potato dataset...")
    copy_classes(SOURCE_DIR, POTATO_CLASSES, POTATO_DEST)
    count_images(POTATO_DEST)

    print("\nSetting up Tomato dataset...")
    copy_classes(SOURCE_DIR, TOMATO_CLASSES, TOMATO_DEST)
    count_images(TOMATO_DEST)

    print("\nDataset preparation complete!")