import os
from io import BytesIO
from PIL import Image
from streamlit_cropper import st_cropper
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure database
DATABASE_URL = "sqlite:///images.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Define the database model
class UploadedImage(Base):
    __tablename__ = "uploaded_images"
    id = Column(Integer, primary_key=True)
    order_no = Column(String, nullable=False)  # Store order number
    image_name = Column(String, nullable=False)
    image_path = Column(String, nullable=False)

# Create the database table if it doesn't exist
Base.metadata.create_all(engine)

# Ensure the upload folder exists
UPLOAD_FOLDER = "./uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Streamlit app
st.title("Image Upload, Rotate, and Crop")

# Get `order_no` from URL
query_params = st.experimental_get_query_params()
order_no = query_params.get("order_no", [""])[0]  # Default to an empty string if missing

if not order_no:
    st.error("No order number provided in the URL. Please include `?order_no=12345`.")
else:
    st.write(f"Order Number: {order_no}")

# File upload
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Open the uploaded image
    image = Image.open(uploaded_file)
    st.subheader("Original Image")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Rotation slider
    rotation_angle = st.slider("Rotate Image (in degrees)", min_value=0, max_value=360, step=1, value=0)
    rotated_image = image.rotate(rotation_angle, expand=True)

    st.subheader("Rotated Image")
    st.image(rotated_image, caption="Rotated Image", use_column_width=True)

    # Aspect ratio selector
    aspect_ratio_choice = st.selectbox(
        "Select Aspect Ratio for Cropping",
        options=[(2, 3), (3, 2)],
        format_func=lambda x: f"{x[0]}:{x[1]}"
    )

    # Cropper widget
    st.subheader("Crop Your Image")
    cropped_image = st_cropper(
        rotated_image,
        realtime_update=True,
        box_color="blue",
        aspect_ratio=aspect_ratio_choice,
        return_type="image",  # Ensure we get a PIL image directly
    )

    # Display cropped image
    st.subheader("Cropped Image Preview")
    st.image(cropped_image, caption="Cropped Image", use_column_width=True)

    # Save cropped image
    if st.button("Save Image"):
        # Save cropped image to a file
        image_name = f"cropped_{uploaded_file.name}"
        image_path = os.path.join(UPLOAD_FOLDER, image_name)
        cropped_image.save(image_path)

        # Save metadata to the database
        new_image = UploadedImage(image_name=image_name, image_path=image_path)
        session.add(new_image)
        session.commit()

        st.success(f"Image saved successfully! File: {image_name}")

# Display saved images
st.subheader("Saved Images")
saved_images = session.query(UploadedImage).all()
if saved_images:
    for img in saved_images:
        st.write(f"ID: {img.id}, Name: {img.image_name}")
        st.image(img.image_path, caption=f"ID: {img.id}, Name: {img.image_name}")
else:
    st.write("No images saved yet.")
