"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

import matplotlib as mt
mt.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import dates
import pylab
import prettyplotlib as plb
from mpl_toolkits.mplot3d import Axes3D
from Core.settings import settings
from TLSensing.settings import CHART_URL
from Core.models import Mote
import os

import logging
logger = logging.getLogger('Core.management.commands.acquire_values_oneshot')

def setUp():
    """
    Set up some stuff to get nicer charts
    """
    font = dict(family='serif', size=8)
    pylab.rcParams['xtick.major.pad'] = '10'
    pylab.rcParams['ytick.major.pad'] = '10'
    pylab.grid()
    mt.rc('font', **font)

def generate_accel_chart(x, y, mote_id):
    """
    Generate charts for Accelerometer sensor.
    It creates a 3d chart showing the point in the space
    and it subplots single values to another figure.

    @params x: dates list
    @param y: a list of tuples, containing acc_x, acc_y, acc_z
    @param mote_id: the id of the mote whose charts need to be generated
    """
    logger.info("Generating accelerometer graph")
    titles = ("X values", "Y values", "Z values")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("Accelerometer values", y=1.08, fontweight='bold')
    ax.set_xlabel(titles[0], fontweight='bold')
    ax.set_ylabel(titles[1], fontweight='bold')
    ax.set_zlabel(titles[2], fontweight='bold')
    for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(8)

    for _ in range(0, len(y)):
        plb.scatter(ax, xs=y[_][0], ys=y[_][0] , zs=y[_][0], color='b', label=x[_].strftime('%d %b,  %H:%M'))
    plt.legend(loc=2, numpoints=1,  scatterpoints=1, ncol=2, fontsize=8, bbox_to_anchor=(0, 0))

    fig.tight_layout()
    fig.savefig(os.path.join(CHART_URL, "mote_acc-%s.svg" %(mote_id)), bbox_inches='tight')

def chart(motes_ipv6, n_measures=int(settings.read()["sampledmeasures"])):
    """
    Set some params in chart generation and then start chart generation workflow.

    @param n_measures: the number of points for sensor value to be plotted out
    @param motes: motes to compute chart
    """
    setUp()
    for ipv6 in motes_ipv6:
        generate_charts(ipv6, n_measures)

def generate_charts(m_ipv6, n_measures):
    """
    Generate charts and save it to disk.

    @param motes: the motes whose charts need to be generated and saved
    @param n_measures: the number of point to be plotted out
    """
    mote = Mote.objects(ipv6=m_ipv6).fields(slice__measures=-n_measures).first()    #TODO: Usa motes.get
    measures = mote.measures
    logger.info("Generating charts for mote with IPv6: %s" % mote.ipv6)
    try:
        x = [measure.date for measure in measures]
        y = [(measure.temperature, measure.humidity, measure.light) for measure in measures]
        logger.info("Generating base graph")
        #generate_base_chart(x, y, mote.id)
        generate_2d_chart(x, y, mote.id, ["Temperature", "Humidity", "Light"], "base")
        if mote.mote_type == "OpenMote":
            xx = [measure.date for measure in measures if (measure.accel_x, measure.accel_y, measure.accel_z) != (None, None, None)]
            yy = [(measure.accel_x, measure.accel_y, measure.accel_z) for measure in measures if (measure.accel_x, measure.accel_y, measure.accel_z) != (None, None, None)]
            generate_2d_chart(xx, yy, mote.id, ["X-Axis Values", "Y-Axis Values", "Z-Axis Values"], "acc_details")
            generate_accel_chart(xx, yy, mote.id)
    except Exception, e:
        logger.error("Error while generating charts \
            for mote with IPv6: %s; exception is: %s" % (mote.ipv6, str(e)))

def generate_2d_chart(x, y, mote_id, titles, name):
    """
    Generate charts for temperature, humidity and light values.

    @params x: dates list
    @param y: a list of tuples, containing temperature, humidity and light
    @param mote_id: the id of the mote whose charts need to be generated
    """
    f, subs = plt.subplots(3, sharex=True)
    f.tight_layout()

    plt.xticks(rotation=25)
    for _ in range(0, 3):
        plb.plot(subs[_], range(0, len(x)), [item[_] for item in y], 'b', marker="o")
        lbls = [xd.strftime('%d %b %Y, %H:%M') for xd in x]
        subs[_].set_xticklabels(lbls)
        subs[_].set_title(titles[_], fontweight='bold')
        subs[_].set_ylabel("Values", fontweight='bold')
        subs[_].autoscale_view(True,True,True)
        for tick in subs[_].xaxis.get_major_ticks():
            tick.label.set_fontsize(8)

    f.savefig(os.path.join(CHART_URL, "mote_" + name + "-" + str(mote_id) + ".svg"), bbox_inches='tight')
