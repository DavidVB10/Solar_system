#-------------TODOS LOS PLANETAS---------------------------------------------------------
from numpy import *
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from mpl_toolkits.mplot3d import Axes3D

#----------------------------------------------------------------------------------------
#creación datos astropy
from astropy.coordinates import get_body_barycentric_posvel
import astropy.units as u
from astropy.time import Time
from datetime import datetime


t = Time(datetime.today().isoformat()) #utilizamos el tiempo actual
planets=('sun', 'mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune')#lista con los planetas que se van a usar

x,y,z,vx,vy,vz=ones((len(planets),1)),ones((len(planets),1)),ones((len(planets),1)),ones((len(planets),1)),ones((len(planets),1)),ones((len(planets),1)) #arrays vacios donde se meteran los correspondientes datos de posicion y velocidad

for i in range(len(planets)):
	posvel=get_body_barycentric_posvel(planets[i],t)
	pos,vel=posvel
	pos=pos.xyz.to(u.m) #cambiamos las unidades de los datos obtenidos ya que estos estan en UA y en UA/d
	vel=vel.xyz.to(u.m/u.s)
	x[i]=pos[0]
	y[i]=pos[1]
	z[i]=pos[2]
	vx[i]=vel[0]
	vy[i]=vel[1]
	vz[i]=vel[2]
	
datos=concatenate((x,y,z,vx,vy,vz),axis=1)

#--------------------------------------------------------------------------------------
#DATOS

G=6.67408e-11

#masas

msol=1.988435e30
mmer=3.302e23
mven=4.8685e24
mtie=5.9742e24
mmar=6.4185e23
mjup=1.899e27
msat=5.6846e26
mura=8.6832e25
mnep=1.0243e26

M=array([msol,mmer,mven,mtie,mmar,mjup,msat,mura,mnep]) #array con todas las masas de los planetas

#Colores que se van a usar

colSol='yellow'
colMer='slategrey'
colVen='darkkhaki'
colTie='b'
colMar='r'
colJup='sandybrown'
colSat='darkgoldenrod'
colUra='mediumseagreen'
colNep='mediumslateblue'
colors=[colSol,colMer,colVen,colTie,colMar,colJup,colSat,colUra,colNep]  #colores que se van a usar en matplotlib

# años en segundos

segSol=6000000000
segMer=7600000
segVen=19400000
segTie=31600000
segMar=59400000
segJup=400000000
segSat=930000000
segUra=2700000000
segNep=5200000000
seg=array([segSol,segMer,segVen,segTie,segMar,segJup,segSat,segUra,segNep]) #tiempo de un año en segundos de todos los planetas (al Sol se le puso lo mismo que a Neptuno)


tf=6000000000
nin=60000
tiempo=arange(0,tf,nin)

#definimos distintas funciones----------------------------------------------------------------

def r(x0,x1,y0,y1,z0,z1):
	return array([(x1-x0),(y1-y0),(z1-z0)])

def modulo(r):
	return sqrt(r[0]**2+r[1]**2+r[2]**2)

def acel(r,m):
	return (G*m/modulo(r)**3)*r

def matrizafila(p):
	fin=reshape(p,(size(p),))
	return fin

def filaamatriz(f):
	tam=len(f)/6
	fin=reshape(f,(int(tam),6))
	return fin

def matrizacubo(m):
	tam=int(len(m)/6)
	fin=reshape(m,(int(tam),6,len(m[0])))
	return fin
	

def diffPlanets(p):
	w=filaamatriz(p)
	diff=zeros_like(w)
	for i in range(len(w)):
		x1,y1,z1,vx1,vy1,vz1=w[i]
		dx_dt=vx1
		dy_dt=vy1
		dz_dt=vz1
		dvx_dt=0
		dvy_dt=0
		dvz_dt=0
		for j in range(len(w)):
			if i==j: continue
			x2,y2,z2,vx2,vy2,vz2=w[j]
			R=r(x1,x2,y1,y2,z1,z2)
			m=M[j]    
			dvx_dt+=acel(R,m)[0] #vamos sumando cada aceleración obtenida
			dvy_dt+=acel(R,m)[1]
			dvz_dt+=acel(R,m)[2]
		diff[i]=array([dx_dt,dy_dt,dz_dt,dvx_dt,dvy_dt,dvz_dt])

	integrando=matrizafila(diff)
	return integrando

def funder(t,p):
		ar=diffPlanets(p)
		return ar #creamos una función que acepte solve_ivp


#llamamos a solve_ivp--------------------------------------------------------------------

datoslinea=matrizafila(datos)
result=solve_ivp(funder,[tiempo[0],tiempo[-1]],datoslinea,t_eval=tiempo,method='RK23').y
#RK45 no llega a hacer una orbita de neptuno
#RK23 no está mal
#BDF sale mal mercurio
#LSODA y Radau y  tarda demasiado,


trayectorias=matrizacubo(result)

#creamos las figuras

planet3D=plt.figure(figsize=(14,10))
ax=Axes3D(planet3D)

for i in range(len(trayectorias)):
	cuerpo=trayectorias[i]
	x=cuerpo[0]
	y=cuerpo[1]
	z=cuerpo[2]
	ax.plot(x,y,z,colors[i],label=planets[i]) #creamos una representación de todas las trayectorias
	if i>4: mark=10
	else: mark=5
	ax.plot([x[-1]],[y[-1]],[z[-1]],markersize=mark,color=colors[i],marker='o')  #circulo que representa la posicion final de cada planeta


ax.legend(loc=1)
plt.title('Sistema Solar en 3D')
plt.xlabel('x')
plt.ylabel('y')
plt.savefig("SistemaSolar3D.png")
plt.show()
