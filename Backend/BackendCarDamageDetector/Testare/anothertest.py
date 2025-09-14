from inference_sdk import InferenceHTTPClient
from PIL import Image
import matplotlib.pyplot as plt
import cv2

CLIENT = InferenceHTTPClient(
    api_url="https://outline.roboflow.com",
    api_key="VfyCoLpU7mZF8UwK3FWB"
)
image_path = 'E:/Licenta/ExPtDetectareDaunaMasina/images/train/2003-Volkswagen-Passat-WVWPH63B13P205670-2.jpg'

result = CLIENT.infer('E:/Licenta/ExPtDetectareDaunaMasina/images/train/2003-Volkswagen-Passat-WVWPH63B13P205670-2.jpg', model_id="car-parts-segmentation/2")

print(result)  # Afișează rezultatul brut

# Încarcă imaginea originală
image = cv2.imread(image_path)
if image is None:
    raise ValueError("Imaginea nu a fost găsită. Verifică calea fișierului.")

# Convertim imaginea în RGB (OpenCV încarcă în BGR)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Desenează predicțiile pe imagine
for pred in result['predictions']:
    # Coordonatele centrului și dimensiunile obiectului
    x_center, y_center = pred['x'], pred['y']
    width, height = pred['width'], pred['height']
    class_name = pred['class']
    confidence = pred['confidence']

    # Calculează colțurile dreptunghiului
    x1 = int(x_center - width / 2)
    y1 = int(y_center - height / 2)
    x2 = int(x_center + width / 2)
    y2 = int(y_center + height / 2)

    # Desenează un dreptunghi în jurul obiectului
    cv2.rectangle(image, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)

    # Adaugă eticheta cu numele clasei și scorul de încredere
    label = f"{class_name} ({confidence:.2f})"
    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Afișează imaginea procesată folosind Matplotlib
plt.figure(figsize=(10, 7))
plt.imshow(image)
plt.axis('off')  # Ascunde axele
plt.show()

# Salvează imaginea cu predicțiile
output_path = 'output_with_predictions.jpg'
Image.fromarray(image).save(output_path)
print(f"Imaginea cu predicțiile a fost salvată la: {output_path}")