import cv2
import numpy as np

class YOLOSegmenter:
    def __init__(self, config_path: str = "yolov3.cfg", weights_path: str = "yolov3.weights", classes_path: str = "coco.names"):
        self.net = None
        self.classes = []
        self.person_class_id = 0

        try:
            self.net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
            with open(classes_path, "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
            self.person_class_id = self.classes.index("person")
        except Exception as e:
            print(f"[RADCAM] Aviso: Arquivos YOLO não carregados ({e}). FX desativado.")

    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        return [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

    def detect_persons(self, frame: np.ndarray, conf_threshold: float = 0.5) -> list[tuple[int, int, int, int]]:
        if self.net is None:
            return []

        (H, W) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers())

        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > conf_threshold and class_id == self.person_class_id:
                    center_x, center_y = int(detection[0] * W), int(detection[1] * H)
                    w, h = int(detection[2] * W), int(detection[3] * H)
                    x, y = int(center_x - w / 2), int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))

        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, 0.4)
        return [boxes[i[0] if isinstance(i, (list, tuple, np.ndarray)) else i] for i in indices]