import matplotlib.pyplot as plt
import numpy as np

# plt.plot(range(1, 5), [x * x for x in range(1, 5)], 'ro')
# plt.axis([0, 6, 0, 20])
# plt.show()

# t = np.arange(0, 5, 0.2)
#
# plot = plt.plot(t, t, 'r--', t, t ** 2, 'bs', t, t ** 3, 'g^')
# for p in plot:
#     print(p)
# line = plot[0]
# line.set_antialiased(True)
#
# plt.show()

# def f(t):
#     return np.exp(-t) * np.cos(2 * np.pi * t)
#
# t1 = np.arange(0, 5, 0.1)
# t2 = np.arange(0, 5, 0.02)
#
# plt.figure(1)
# plt.subplot(211)
# plt.plot(t1, f(t1), 'bo', t2, f(t2), 'k')
#
# plt.subplot(223)
# plt.plot(t2, np.cos(2 * np.pi * t2), 'r--')
# plt.figure(2)                # a second figure
# plt.plot([4, 5, 6])
# plt.show()
# make up some data in the interval ]0, 1[
# y = np.random.normal(loc=0.5, scale=0.4, size=1000)
# y = y[(y > 0) & (y < 1)]
# y.sort()
# x = np.arange(len(y))
#
# # plot with various axes scales
# plt.figure(1)
#
# # linear
# plt.subplot(221)
# plt.plot(x, y)
# plt.yscale('linear')
# plt.title('linear')
# plt.grid(True)
#
#
# # log
# plt.subplot(222)
# plt.plot(x, y)
# plt.yscale('log')
# plt.title('log')
# plt.grid(True)
#
#
# # symmetric log
# plt.subplot(223)
# plt.plot(x, y - y.mean())
# plt.yscale('symlog', linthreshy=0.05)
# plt.title('symlog')
# plt.grid(True)
#
# # logit
# plt.subplot(224)
# plt.plot(x, y)
# plt.yscale('logit')
# plt.title('logit')
# plt.grid(True)
#
# plt.show()

'''
For each colormap, plot the lightness parameter L* from CIELAB colorspace
along the y axis vs index through the colormap. Colormaps are examined in
categories as in the original matplotlib gallery of colormaps.
'''

# from colormaps import cmaps
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib import cm
# import matplotlib as mpl
# from colorspacious import cspace_converter
#
# mpl.rcParams.update({'font.size': 12})
# mpl.rcParams['font.sans-serif'] = ('Arev Sans, Bitstream Vera Sans, '
#                                    'Lucida Grande, Verdana, Geneva, Lucid, '
#                                    'Helvetica, Avant Garde, sans-serif')
# mpl.rcParams['mathtext.fontset'] = 'custom'
# mpl.rcParams['mathtext.cal'] = 'cursive'
# mpl.rcParams['mathtext.rm'] = 'sans'
# mpl.rcParams['mathtext.tt'] = 'monospace'
# mpl.rcParams['mathtext.it'] = 'sans:italic'
# mpl.rcParams['mathtext.bf'] = 'sans:bold'
# mpl.rcParams['mathtext.sf'] = 'sans'
# mpl.rcParams['mathtext.fallback_to_cm'] = 'True'
#
# # indices to step through colormap
# x = np.linspace(0.0, 1.0, 100)
#
# # Do plot
# for cmap_category, cmap_list in cmaps:
#
#     # Do subplots so that colormaps have enough space. 5 per subplot?
#     dsub = 5 # number of colormaps per subplot
#     if cmap_category == 'Diverging': # because has 12 colormaps
#         dsub = 6
#     elif cmap_category == 'Sequential (2)':
#         dsub = 6
#     elif cmap_category == 'Sequential':
#         dsub = 7
#     nsubplots = int(np.ceil(len(cmap_list)/float(dsub)))
#
#     fig = plt.figure(figsize=(7,2.6*nsubplots))
#
#     for i, subplot in enumerate(range(nsubplots)):
#
#         locs = [] # locations for text labels
#
#         ax = fig.add_subplot(nsubplots, 1, i+1)
#
#         for j, cmap in enumerate(cmap_list[i*dsub:(i+1)*dsub]):
#
#             # Get rgb values for colormap
#             rgb = cm.get_cmap(cmap)(x)[np.newaxis,:,:3]
#
#             # Get colormap in CAM02-UCS colorspace. We want the lightness.
#             lab = cspace_converter("sRGB1", "CAM02-UCS")(rgb)
#
#             # Plot colormap L values
#             # Do separately for each category so each plot can be pretty
#             # to make scatter markers change color along plot:
#             # http://stackoverflow.com/questions/8202605/matplotlib-scatterplot-colour-as-a-function-of-a-third-variable
#             if cmap_category=='Perceptually Uniform Sequential':
#                 dc = 1.15 # spacing between colormaps
#                 ax.scatter(x+j*dc, lab[0,:,0], c=x, cmap=cmap,
#                            s=300, linewidths=0.)
#                 if i==2:
#                     ax.axis([-0.1,4.1,0,100])
#                 else:
#                     ax.axis([-0.1,4.7,0,100])
#                 locs.append(x[-1]+j*dc) # store locations for colormap labels
#
#             elif cmap_category=='Sequential':
#                 dc = 0.6 # spacing between colormaps
#                 # These colormaps all start at high lightness but we want them
#                 # reversed to look nice in the plot, so reverse the order.
#                 ax.scatter(x+j*dc, lab[0,::-1,0], c=x[::-1], cmap=cmap,
#                            s=300, linewidths=0.)
#                 if i==2:
#                     ax.axis([-0.1,4.1,0,100])
#                 else:
#                     ax.axis([-0.1,4.7,0,100])
#                 locs.append(x[-1]+j*dc) # store locations for colormap labels
#
#             elif cmap_category=='Sequential (2)':
#                 dc = 1.15
#                 ax.scatter(x+j*dc, lab[0,:,0], c=x, cmap=cmap,
#                            s=300, linewidths=0.)
#                 ax.axis([-0.1,7.0,0,100])
#                 # store locations for colormap labels
#                 locs.append(x[-1]+j*dc)
#
#             elif cmap_category=='Diverging':
#                 dc = 1.2
#                 ax.scatter(x+j*dc, lab[0,:,0], c=x, cmap=cmap,
#                            s=300, linewidths=0.)
#                 ax.axis([-0.1,7.1,0,100])
#                 # store locations for colormap labels
#                 locs.append(x[int(x.size/2.)]+j*dc)
#             elif cmap_category=='Qualitative':
#                 dc = 1.3
#                 ax.scatter(x+j*dc, lab[0,:,0], c=x, cmap=cmap,
#                            s=300, linewidths=0.)
#                 ax.axis([-0.1,6.3,0,100])
#                 # store locations for colormap labels
#                 locs.append(x[int(x.size/2.)]+j*dc)
#
#             elif cmap_category=='Miscellaneous':
#                 dc = 1.25
#                 ax.scatter(x+j*dc, lab[0,:,0], c=x, cmap=cmap,
#                            s=300, linewidths=0.)
#                 ax.axis([-0.1,6.1,0,100])
#                 # store locations for colormap labels
#                 locs.append(x[int(x.size/2.)]+j*dc)
#
#             # Set up labels for colormaps
#             ax.xaxis.set_ticks_position('top')
#             ticker = mpl.ticker.FixedLocator(locs)
#             ax.xaxis.set_major_locator(ticker)
#             formatter = mpl.ticker.FixedFormatter(cmap_list[i*dsub:(i+1)*dsub])
#             ax.xaxis.set_major_formatter(formatter)
#             labels = ax.get_xticklabels()
#             for label in labels:
#                 label.set_rotation(60)
#
#     ax.set_xlabel(cmap_category + ' colormaps', fontsize=14)
#     fig.text(0.0, 0.55, 'Lightness $L^*$', fontsize=12,
#              transform=fig.transFigure, rotation=90)
#
#     fig.tight_layout(h_pad=0.05, pad=1.5)
#     plt.show()

axes = plt.gca()

circle = plt.Circle((0, 0), radius=0.75, fc='y')
t = plt.Line2D([0, 1, 1, 0], [0, 1, 0, 0], lw=3, color='b', marker='.', markersize=20, markerfacecolor='k')
axes.add_patch(circle)
axes.add_line(t)
axes.get_xaxis().set_visible(False)
axes.get_yaxis().set_visible(False)

plt.axis('scaled')
plt.show()

# ax = fig.add_subplot(2, 1, 2)
# t = np.arange(0, 1, 0.01)
# s = np.sin(2 * np.pi * t)
# ax.plot(t, s, color='blue', lw=2)
# plt.show()
