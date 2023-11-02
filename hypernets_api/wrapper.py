

__author__ = "Pieter De Vis <pieter.de.vis@npl.co.uk>"



from calvalplots.plot_factory.factory import PlotTypeFactory

fact=PlotTypeFactory()

def make_plotter(type,*args,**kwargs):
    return fact.get_plot_maker(type)(*args,**kwargs)

def plot(type,*args,**kwargs):
    plotter=fact.get_plot_maker(type)()
    plotter.plot(*args,**kwargs)

def plot_series(type,*args,**kwargs):
    plotter=fact.get_plot_maker(type)()
    plotter.plot_series(*args,**kwargs)

def plot_satcomp(type,*args,**kwargs):
    plotter=fact.get_plot_maker(type)()
    plotter.plot_satcomp(*args,**kwargs)








