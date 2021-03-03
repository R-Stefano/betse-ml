import matplotlib.pyplot as plt
import numpy as np
import pickle
import matplotlib.cm as cm
from collections import namedtuple

def pretty_patch_plot(
    data_verts, ax, cell_verts, um, clrmap,
    cmin=None,
    cmax=None,
    use_other_verts=None
):
    """
    Maps data on mem midpoints to vertices, and
    uses tripcolor on every cell patch to create a
    lovely gradient. Slow but beautiful!

    data:   mem midpoint data for plotting (e.g vm)
    ax:     plot axispretty_patch_plot
    """

    # data_verts = data

    # colormap clim
    if cmin is None:
        amin = data_verts.min()
        amax = data_verts.max()
    else:
        amin = cmin
        amax = cmax

    # amin = amin + 0.1 * np.abs(amin)
    # amax = amax - 0.1 * np.abs(amax)

    # collection of cell patchs at vertices:
    cell_faces = np.multiply(cell_verts, um)

    # Cell membrane (Vmem) plotter (slow but beautiful!)
    for i in range(len(cell_faces)):
        x = cell_faces[i][:, 0]
        y = cell_faces[i][:, 1]

        # Average color value of each cell membrane, situated at the midpoint
        # of that membrane. This parameter is referred to as "C" in both the
        # documentation and implementation of the tripcolor() function.
        dati = np.repeat(data_verts[i], len(x))

        # "matplotlib.collections.TriMesh" instance providing the
        # Gouraud-shaded triangulation mesh for the non-triangular vertices of
        # this cell from the Delaunay hull of these vertices.
        col_cell = ax.tripcolor(x, y, dati, shading='gouraud', cmap=clrmap)

        #FIXME: No need to manually call set_clim() here. Instead, pass the
        #"vmin=amin, vmax=amax" parameters to the above tripcolor() call.

        # Autoscale this mesh's colours as desired.
        col_cell.set_clim(amin, amax)

    return col_cell, ax

def plotPrettyPolyData(data_verts, cells, clrAutoscale = True, clrMin = None, clrMax = None,
    clrmap = None, showCellsIdxs=False, plotIecm=False):
        """
        Assigns color-data to each polygon mem-mid, vertex and cell centre in a cell cluster
        diagram and returns a plot instance (fig, axes).

        Parameters
        ----------
        cells : Cells
            Data structure holding all world information about cell geometry.
        data : [numpy.ndarray]
            A data array with each scalar entry corresponding to a cell's data
            value (for instance, concentration or voltage) at cell membranes. If zdata is not
            supplied, the cells will be plotted with a uniform color; if zdata
            is the string `random`, a random data set will be created and
            plotted.
        clrAutoscale : optional[bool]
            If `True`, the colorbar is autoscaled to the max and min of zdata.
        clrMin : optional[float]
            Set the colorbar to a user-specified minimum value.
        clrMax : optional[float]
            Set the colorbar to a user-specified maximum value.
        clrmap : optional[matplotlib.cm]
            The colormap to use for plotting. Must be specified as cm.mapname.
            A list of available mapnames is supplied at:
            http://matplotlib.org/examples/color/colormaps_reference.html

        Returns
        -------
        fig, ax
            Matplotlib figure and axes instances for the plot.

        Notes
        -------
        This method Uses `matplotlib.collections.PolyCollection`,
        `matplotlib.cm`, `matplotlib.pyplot`, and numpy arrays and hence is
        computationally slow. Avoid calling this method for large collectives
        (e.g., larger than 500 x 500 um).
        """

        um = 1000000.0

        # define the figure and axes instances
        fig = plt.figure()
        ax = plt.subplot(111)

        # define colorbar limits for the PolyCollection
        maxval = data_verts.max()
        minval = data_verts.min()

        coll, ax = pretty_patch_plot(data_verts, ax, cells.cell_verts, um, clrmap, cmin=minval, cmax=maxval)

        # add a colorbar
        coll.set_clim(minval, maxval)
        ax_cb = fig.colorbar(coll, ax=ax)

        ax.axis('equal')

        if showCellsIdxs is True:
            for i,cll in enumerate(cells.cell_centres):
                ax.text(um*cll[0], um*cll[1], i, ha='center',va='center')

        xmin = cells.xmin*um
        xmax = cells.xmax*um
        ymin = cells.ymin*um
        ymax = cells.ymax*um

        ax.axis([xmin,xmax,ymin,ymax])

        return fig,ax,ax_cb

def run():
    exampleIdx = 0
    # Load Helper data
    with open("storage/raw/{}/cells.pkl".format(exampleIdx), "rb") as f:
        cells = pickle.load(f)

    CellsObj = namedtuple('CellsObj', 'cell_verts xmin xmax ymin ymax')
    cells = CellsObj(cell_verts=cells['cell_verts'], xmin=cells['xmin'], xmax=cells['xmax'], ymin=cells['ymin'], ymax=cells['ymax'])


    # Open Vmems (ground truth)
    x, y = np.load('storage/processed/validation/id_{}.npy'.format(exampleIdx), allow_pickle = True)
    Vmems = y
    print("X {} | Y {}".format(x.shape, y.shape))
    print("Cells Verts", cells.cell_verts.shape)
    print("Cells Vmems", Vmems.shape)


    '''
    Plot all transmembrane voltages (Vmem) for the cell cluster at the last
    time step.

    Args:
    - data: SimPhase
    - conf:  SimConfExportPlotCells
    '''

    figV, axV, cbV = plotPrettyPolyData(
        Vmems,
        cells,   ###############
        showCellsIdxs = False,
        plotIecm = True,
        clrmap = cm.RdBu_r,
        clrMin = -70.00,
        clrMax = 10.00,
    )

    figV.suptitle('Final Vmem', fontsize=14, fontweight='bold')
    axV.set_xlabel('Spatial distance [um]')
    axV.set_ylabel('Spatial distance [um]')
    cbV.set_label('Voltage mV')

    plt.show()
    # Export this plot to disk and/or display.
    #self._export(phase=phase, basename='final_Vmem_2D')
