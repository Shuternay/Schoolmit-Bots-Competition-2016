#!/usr/bin/env python

from PIL import Image, ImageDraw


def main():
  background = (224, 224, 224, 255)
  darkbackground = (176, 176, 192, 255)
  deadbackground = (128, 128, 128, 255)

  img = Image.new("RGBA", (128, 128), background)
  img.save('public/images/0.png', 'PNG')

  img = Image.new("RGBA", (128, 128), background)
  draw = ImageDraw.Draw(img)
  draw.ellipse((16, 16, 112, 112), fill='red', outline='red')
  img.save('public/images/1.png', 'PNG')

  img = Image.new("RGBA", (128, 128), background)
  draw = ImageDraw.Draw(img)
  draw.ellipse((16, 16, 112, 112), fill='blue', outline='blue')
  img.save('public/images/3.png', 'PNG')


  img = Image.new("RGBA", (128, 128), deadbackground)
  img.save('public/images/dark0.png', 'PNG')

  img = Image.new("RGBA", (128, 128), (128, 128, 255, 255))
  draw = ImageDraw.Draw(img)
  draw.ellipse((16, 16, 112, 112), fill='maroon', outline='maroon')
  img.save('public/images/2.png', 'PNG')

  img = Image.new("RGBA", (128, 128), (255, 128, 128, 255))
  draw = ImageDraw.Draw(img)
  draw.ellipse((16, 16, 112, 112), fill='navy', outline='blue')
  img.save('public/images/4.png', 'PNG')

if __name__=='__main__':
  main()
