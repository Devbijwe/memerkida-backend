from main import app,db
from models import Files
import os
import time
import random
import uuid
from flask import request, jsonify
from werkzeug.utils import secure_filename

from PIL import Image
import tempfile
import os
import io
from PIL import Image
from PIL import UnidentifiedImageError

# def resize_images(path):
#     for item in os.listdir(path):
#         if os.path.isfile(os.path.join(path, item)):
#             try:
#                 im = Image.open(os.path.join(path, item))
#                 resized_image = im.resize((200, 200), Image.ANTIALIAS)
#                 resized_image.save(os.path.join(path, item))
#             except UnidentifiedImageError:
#                 print(f"Skipping file {item} as it is not a valid image.")

# resize_images("data/images/tshirts")

# def reduce_image_size(image_path, max_file_size=256 * 1024):
#     # Open the image using PIL
#     image = Image.open(image_path)
#     # Get the current file size of the image
#     current_file_size = os.path.getsize(image_path)
    
#     # Calculate the scaling factor based on the desired file size
#     scale_factor = (max_file_size / float(current_file_size)) ** 0.5


#     # Calculate the new size based on the scaling factor
#     new_size = (int(image.size[0] * scale_factor), int(image.size[1] * scale_factor))

#     # Resize the image
#     resized_image = image.resize(new_size, Image.ANTIALIAS)

#     # Create an in-memory stream to store the resized image data
#     output_stream = io.BytesIO()

#     # Save the resized image to the in-memory stream with the original format
#     resized_image.save(output_stream, format=image.format)

#     # Get the resized image data from the stream
#     resized_image_data = output_stream.getvalue()

#     # Check the size of the resized image
#     resized_file_size = len(resized_image_data)

#     # Check if the resized image is still within the limit
#     if resized_file_size <= max_file_size:
#         print("Image successfully resized to within the size limit.")
#         return resized_image_data
#     else:
#         print("Image could not be resized within the size limit. Returning the original image.")
#         return image.tobytes()

from PIL import Image
import io

def compress_image(image_file, max_size=(None,None), quality=50, target_size_kb=256):
    """
    Compresses an image file by resizing and reducing quality.

    Args:
        image_file (str): The path to the image file.
        max_size (tuple, optional): The maximum size (width, height) allowed for the image. Default is (256, 256).
        quality (int, optional): The image quality to use for compression (0-100). Default is 80.
        target_size_kb (int, optional): The target file size in kilobytes. Default is 256.

    Returns:
        bytes: The compressed image data as a byte array.
    """
    # Open the image file
    image = Image.open(image_file)

    # Resize the image if necessary
    # Resize the image if necessary
    if max_size[0] is not None and max_size[1] is not None:
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size)



    # Set the initial quality range
    quality_lower = 0
    quality_upper = 100

    # Perform binary search to find the optimal quality level
    while quality_lower < quality_upper:
        quality = (quality_lower + quality_upper) // 2
        print(quality)
        # Create a byte array to store the compressed image
        output_buffer = io.BytesIO()

        # Save the image with the current quality level to the byte array
        image.save(output_buffer, format=image.format, optimize=True, quality=quality)

        # Get the byte array data and check the file size
        compressed_data = output_buffer.getvalue()
        file_size_kb = len(compressed_data) / 1024

        if file_size_kb <= target_size_kb:
            # Decrease the upper bound for quality range
            quality_upper = quality
        else:
            # Increase the lower bound for quality range
            quality_lower = quality + 1

        # Reset the byte array for the next compression iteration
        output_buffer.seek(0)
        output_buffer.truncate()

    # Perform one more compression iteration with the final quality level
    image.save(output_buffer, format=image.format, optimize=True, quality=quality_lower)
    compressed_data = output_buffer.getvalue()

    return compressed_data




def save_file(file, upload_path, file_type,compress=True):
    allowed_extensions = get_allowed_extensions(file_type)

    if file and file.filename != '':
        # Validate file extension
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return None, allowed_extensions, None

        # Generate a secure filename
        original_filename = secure_filename(file.filename)
        base_filename, file_extension = os.path.splitext(original_filename)
        timestamp = str(int(time.time()))  # Append timestamp
        random_string = str(random.randint(1, 999999))  # Append random string
        unique_filename = f"Image_{str(uuid.uuid4())}_{timestamp}_{random_string}{file_extension}"

        # Generate the file path
        file_path = os.path.join(upload_path, unique_filename)

        # Check if a file with the same filename already exists
        while os.path.exists(file_path):
            random_string = str(random.randint(1, 999999))  # Generate a new random string
            unique_filename = f"Image_{str(uuid.uuid4())}_{timestamp}_{random_string}{file_extension}"
            file_path = os.path.join(upload_path, unique_filename)
        if compress:
            # Compress the image
            compressed_data = compress_image(file, max_size=(1024, 1024), quality=80)

            if compressed_data is None:
                return None, allowed_extensions, None

            # Save the compressed image data to the file path
            with open(file_path, 'wb') as output_file:
                output_file.write(compressed_data)

            # Return the saved file path, allowed extensions, and the file
            return file_path, allowed_extensions, file
        # Save the file
        file.save(file_path)
        

        

        # Return the saved file path, allowed extensions, and the file
        return file_path, allowed_extensions, file

    return None, allowed_extensions, None


def save_file_path_to_db(file_path, file_type):
    # Save the file path and file type to the database
    fileId = str(uuid.uuid4())
    
    # Generate the file URL based on the fileId
    file_url = f"http://127.0.0.1:5000/api/files/{fileId}"

    # Create a new instance of the Files model
    new_file = Files(fileId=fileId,fileType=file_type, filepath=file_path, fileUrl=file_url)

    # Add the new file to the database
    db.session.add(new_file)
    db.session.commit()

    # Return the file URL
    return file_url

def get_allowed_extensions(file_type):
    allowed_extensions = set()

    if file_type == 'image':
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    elif file_type == 'document':
        allowed_extensions = {'doc', 'docx', 'pdf', 'txt'}
    elif file_type == 'video':
        allowed_extensions = {'mp4', 'mov', 'avi', 'mkv'}
    # Add more file types and their corresponding allowed extensions as needed
    elif file_type == 'audio':
        allowed_extensions = {'mp3', 'wav', 'ogg'}

    return allowed_extensions