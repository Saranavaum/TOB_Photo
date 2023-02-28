import numpy as np
import os,glob
import pylab as pl

from pyraf import iraf


iraf.noao.digiphot(_doprint=0)
iraf.noao.digiphot.phot(_doprint=0)
iraf.noao.digiphot.daophot(_doprint=0)

iraf.datapars.noise='poisson'
iraf.datapars.scale=1.


iraf.imhead('brillante.fits',long='yes') #para ver el nombre de los parametros
iraf.datapars.ccdread='RDNOISE'
iraf.datapars.gain='GAIN'
iraf.datapars.exposure='EXPTIME'
iraf.datapars.airmass='AIRMASS'
iraf.datapars.filter='INSFILTE'
iraf.datapars.datamax=50000.

iraf.findpars.threshold=8.0 #razonS/R si pilla muchas cosas de demas igua esque esta pillando perturbacion
#cuanto mas grande el algoritmo encontrará menos estrellas, mayor señal
iraf.findpars.nsigma=1.5
iraf.findpars.ratio=1.0
iraf.findpars.theta=0.

iraf.centerpars.calgorithm='centroid'

iraf.display('oscura.fits',1)
iraf.daoedit('oscura.fits')

iraf.display('brillante.fits',1)
iraf.daoedit('brillante.fits')
#con esta opción se buscan estrellas que no estén saturadas, es decir con número de cuentas menor que 60000
#y con la opción a de daoedit se hace una media de las fwhm y sigma

iraf.delete('oscura*.coo*',verify='no')


iraf.datapars.fwhmpsf=4.08
iraf.datapars.sigma=10.51

iraf.daofind('oscura',output='default',starmap='',skymap='',interactive='no',verify='no')


iraf.fitskypars.salgorithm='centroid'
iraf.photpars.aperture=float(iraf.datapars.fwhmpsf)*2.5
iraf.fitskypars.annulus=float(iraf.photpars.aperture)+4.0
iraf.fitskypars.dannulus=6.0
iraf.photpars.weighting='constant'
iraf.phot.interactive='no'
iraf.phot.verify='no'
iraf.phot.update='no'



iraf.delete('oscura*.mag.*',verify='no') 
iraf.phot('oscura.fits', coords="oscura.coo.1",output="default")

#se cambian los parámetros para la brillante puesto que sigma fue mayor

iraf.datapars.fwhmpsf=4.18
iraf.datapars.sigma=30.51

iraf.fitskypars.salgorithm='centroid'
iraf.photpars.aperture=float(iraf.datapars.fwhmpsf)*2.5
iraf.fitskypars.annulus=float(iraf.photpars.aperture)+4.0
iraf.fitskypars.dannulus=6.0
iraf.photpars.weighting='constant'
iraf.phot.interactive='no'
iraf.phot.verify='no'
iraf.phot.update='no'
 
iraf.delete("brillante.mag.*",verify="no") # borra antes la salida
iraf.phot('brillante.fits', coords="oscura.coo.1",output="default")


iraf.delete("oscura.fits.phot.",verify="no")
iraf.txdump('oscura.fits.mag.1',fields='XCENTER,YCENTER,MAG,MERR',expr='yes',header='yes',parameters='yes',Stdout='oscura.fits.phot')

iraf.delete("brillante.fits.phot.",verify="no")
iraf.txdump('brillante.fits.mag.1',fields='XCENTER,YCENTER,MAG,MERR',expr='yes',header='yes',parameters='yes',Stdout='brillante.fits.phot')

iraf.delete('oscura_bien.*',verify='no')
iraf.txselect('oscura.fits.phot','oscura_bien.phot.1','MAG!=INDEF && MERR < 0.8')


iraf.delete('brillante_bien.*',verify='no')
iraf.txselect('brillante.fits.phot','brillante_bien.phot.1','MAG!=INDEF && MERR < 0.8')



Oxc, Oyc, Omag, Omerr = np.loadtxt('oscura_bien.phot.1',usecols=(0,1,2,3),unpack=True)
Bxc, Byc, Bmag, Bmerr = np.loadtxt('brillante_bien.phot.1',usecols=(0,1,2,3),unpack=True)


leyenda= ['']
leyenda.pop(0)
pl.clf()

pl.plot(Omag, Omerr, 'ro', markersize=1.)
leyenda.append('oscura.phot')

pl.plot(Omag, Omerr, 'bo', markersize=1.)
leyenda.append('brillante.phot')


pl.xlabel(' mag')
pl.ylabel('err mag')
pl.xlim(11.,18.)
pl.ylim(-0.01,0.25)
pl.legend(leyenda,loc=2,fontsize='xx-small')
pl.title('Magnitudes instrumentales')
pl.savefig('ruido.png')
pl.show()


# para un error de 0.10 se obtuvo una magnitud de 16,37 aproximadamente, para ams
