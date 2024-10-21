from django.db import models
from PIL import Image, ImageOps

class ResizableImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        self.background_color = kwargs.pop('background_color', (255, 255, 255, 255))  # Default white background
        super().__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        super().save_form_data(instance, data)
        if data and hasattr(data, 'file'):
            self.resize_image(instance)

    def resize_image(self, instance):
        image_field = getattr(instance, self.name)
        img = Image.open(image_field.path)

        # Resize image
        if self.width and self.height:
            img = img.resize((self.width, self.height), Image.ANTIALIAS)

        # Create a new image with background color
        background = Image.new('RGBA', (self.width, self.height), self.background_color)
        img = Image.alpha_composite(background, img.convert('RGBA'))

        img.save(image_field.path)
