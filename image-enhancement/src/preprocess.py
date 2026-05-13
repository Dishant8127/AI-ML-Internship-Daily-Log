import cv2
import numpy as np

from rembg import remove
from PIL import Image
from io import BytesIO


def remove_background(image_path):

    with open(image_path, "rb") as f:
        input_data = f.read()

    output_data = remove(input_data)

    image = Image.open(BytesIO(output_data)).convert("RGB")

    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def enhance_contrast(image):

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0,tileGridSize=(8, 8))

    cl = clahe.apply(l)

    enhanced_lab = cv2.merge((cl, a, b))

    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def resize_image(image, size=(224, 224)):

    return cv2.resize(image, size)


def normalize_image(image):

    image = image.astype("float32") / 255.0

    return image


def enhance_image(image_path):

    image = remove_background(image_path)

    image = enhance_contrast(image)

    image = resize_image(image)

    image = normalize_image(image)

    image = (image * 255).astype("uint8")

    return image
