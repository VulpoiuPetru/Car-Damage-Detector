from ultralytics import YOLO

# Încarcă greutățile anterioare
model = YOLO("runs/detect/train6322/weights/best.pt")  # Specifică calea către fișierul best.pt

# Continuă antrenamentul pe același model
#results = model.train(data="config.yaml", epochs=10)  # Poți ajusta numărul de epoci


#salvarea modelului pe acelasi project si name,a.i rezultatele sa fie salvate in acelasi loc
#results = model.train(data="config.yaml", epochs=10, project="runs/detect", name="train43")


#evaluarea unei date noi
results = model.predict("runs/testareimagini/img7.jpg")
#results.show()
# Afișarea predicțiilor pentru fiecare imagine din listă
for result in results:
    result.show()