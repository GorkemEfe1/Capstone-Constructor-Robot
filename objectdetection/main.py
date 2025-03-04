import ImageProcessor as ip

processor = ip.ImageProcessor("./image.jpg")
processor.extract_building_details()
processor.show_final()
processor.export_json()