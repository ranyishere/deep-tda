import imageio
from math import inf
import numpy as np
import matplotlib.pyplot as plt
import os
from ripser import ripser, Rips


def generate(i, all_block_list, names=[]):
    bs = (0, 0)
    block_lists = []
    all_images = []
    directory = "images/batches/{0}".format(i)
    for j, block in enumerate(all_block_list):
        if block.shape != bs:
            block_lists.append([])
            bs = block.shape
        block_lists[-1].append(({"block": block, "name": names[j]}))
    for j, block_list in enumerate(block_lists):
        all_images += visualize('{0}/{1}'.format(directory,
                                                 j),
                                [block["block"] for block in block_list],
                                names=[block["name"] for block in block_list],
                                c=len(all_images))
    imageio.mimsave('{0}/all.gif'.format(directory), all_images, fps=3)
    return all_images


def visualize(dn, block_list, names=[], c=0):
    """
    Given layers of batch data, generate their Vietoris-Rips Complexes, persistence diagrams, and plot as gif.
    :params i:
    :params block: list of second-order numpy array
    """
    directory = dn
    os.makedirs(directory, exist_ok=True)  # succeeds even if directory exists.
    images = []
    diagrams_list = []

    birth = 0
    death = 0

    bs = (0, 0)

    for j, block in enumerate(block_list):
        rips = Rips(verbose=False)
        diagrams = rips.fit_transform(block)
        for k, diagram in enumerate(diagrams):
            if len(diagram) != 0:
                birth = max(birth, max(diagram[:, 0]))
                death = max(death, max([v for v in diagram[:, 1] if v != inf]))
        diagrams_list.append(diagrams)

    birth = int(birth)
    death = int(death)

    for j, diagrams in enumerate(diagrams_list):
        label = str(c) + "_" + names[j].replace("/", "_")
        fn = '{0}/{1}.png'.format(directory, label)
        c += 1

        # rips.plot(diagrams)
        fig = plt.figure()
        for k, diagram in enumerate(diagrams):
            plt.scatter(diagram[:, 0], diagram[:, 1])

        plt.title(label)
        axes = plt.gca()
        axes.set_xlim([-1, birth + 10])
        axes.set_ylim([-1, death + 10])

        plt.savefig(fn)
        plt.clf()
        images.append(imageio.imread(fn))
    imageio.mimsave('{0}/all.gif'.format(directory), images, fps=3)

    return images
