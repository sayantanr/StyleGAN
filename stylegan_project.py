# -*- coding: utf-8 -*-
"""stylegan project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14N9yCg31Jhtu5AV4ZQNSAjhex9W3DV9N
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow
print(tensorflow.__version__)

!git clone https://github.com/NVlabs/stylegan2.git

!python /content/stylegan2/run_generator.py generate-images \
--network=gdrive:networks/stylegan2-ffhq-config-f.pkl \
 --seeds=4-6 --truncation-psi=0.4

!ffmpeg -r 1 -i /content/results/00000-generate-images/seed%04d.png -vcodec mpeg4 -y people.mp4

!cp people.mp4 /content

import sys
sys.path.insert(0, "/content/stylegan2")

import argparse
import numpy as np
import PIL.Image
import dnnlib
import dnnlib.tflib as tflib
import re
import sys
import pretrained_networks

def seeder(seeds, vector_size):
 result = []
 for seed in seeds:
   rnd = np.random.RandomState(seed)
   result.append( rnd.randn(1, vector_size))
 return result

def generate_images(gs, seeds, truncation_psi):
   noise_vars = [var for name, var in Gs.components.synthesis.vars.items() if name.startswith('noise')]
 
   Gs_kwargs = dnnlib.EasyDict()
   Gs_kwargs.output_transform = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)
   Gs_kwargs.randomize_noise = False
   if truncation_psi is not None:
       Gs_kwargs.truncation_psi = truncation_psi
 
   for seed_idx, seed in enumerate(seeds):
       print('Generating image for seed %d/%d ...' % (seed_idx, len(seeds)))
       rnd = np.random.RandomState()
       tflib.set_vars({var: rnd.randn(*var.shape.as_list()) for var in noise_vars}) # [height, width]
       images = Gs.run(seed, None, **Gs_kwargs) # [minibatch, height, width, channel]
       path = f"/content/out/image{seed_idx}.png"
       PIL.Image.fromarray(images[0], 'RGB').save(path)

network_pkl = "gdrive:networks/stylegan2-ffhq-config-f.pkl"
print('Loading networks from "%s"...' % network_pkl)
_G, _D, Gs = pretrained_networks.load_networks(network_pkl)

vector_size = Gs.input_shape[1:][0]
seeds = seeder(range(6, 5), vector_size)

!mkdir /content/out

seeds = seeder([6, 5], vector_size)

STEPS = 300
diff = seeds[1] - seeds[0]
step = diff / STEPS
current = seeds[0].copy()
 
seeds2 = []
for i in range(STEPS):
 seeds2.append(current)
 current = current + step

generate_images(Gs, seeds2, truncation_psi=0.4)

!ffmpeg -r 50 -i /content/out/image%d.png -vcodec mpeg4 -y faces.mp4

!cp faces.mp4 /content