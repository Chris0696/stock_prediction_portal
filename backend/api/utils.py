import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import matplotlib.pyplot as plt


def save_plot(plot_img_path):
    # Create the file path using FileSystemStorage
    fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
    image_path = fs.path(plot_img_path)  # Create full path to file
    # image_path = os.path.join(settings.MEDIA_ROOT, plot_img_path)
    plt.savefig(image_path)
    plt.close()
    # Generate URL accessible from MEDIA_URL
    image_url = fs.url(plot_img_path)   # Generates a complete URL
    # image_url = settings.MEDIA_URL + plot_img_path

    return image_url