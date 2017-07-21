#include <math.h>
#include "filt.h"
extern void bcoef (double, double *, double (*)[2], double (*)[2], int *, double *);

#include <stdio.h>
void notchcoef(int mm)
{
	static double pai=3.14159265358979324;
	double  cos(),atan(),tan();
	double  th,wpl,wph,ar,b1,b2,cd,kp,a,b,d,e, wpc;
	double  gg1[NoConst2],aa1[NoConst2][NoConst3/2],bb1[NoConst2][NoConst3/2],c;
	float   fcl,fch,fcc;
	int     i,nn;

        e = notch.decay[mm] / 2.0;
        bcoef(e, gg1, aa1, bb1, &nn, &c);
	fcl = 0.99 * notch.freq[mm] / smpf;//f1/fs
	fch = 1.01 * notch.freq[mm] / smpf;//f2/fs
        wpl = 2.0 * pai * fcl;//Op1
        wph = 2.0 * pai * fch;//Op2
	ar=cos((wph+wpl)/2.0)/cos((wph-wpl)/2.0);//alpha
	kp=tan((wph-wpl)/2.0)*(c/2.0);//k
	a=(2.0*ar)/(1.0+kp);//A
	b=(1.0-kp)/(1.0+kp);//B
	d=(1.0+b)*(1.0+b);//(1+B)**2
	for(i=0;i<nn;i++){
		b1=bb1[i][0];//basic["b1"](k)
		b2=bb1[i][1];//basic["b2"](k)
		cd=1.0+b1*b+b2*b*b;//C(k)
		ggn[mm][i]=gg1[i]*d/cd;//notch["A"]
		bbn[mm][i][0]=-a*((2.0+b1)+b*(b1+2.0*b2))/cd;//notch["b1"]
		bbn[mm][i][1]=(b1*b*b+2.0*(1.0+b2)*b+b1+(1.0+b1+b2)*a*a)/cd;//notch["b2"]
		bbn[mm][i][2]=-a*((2.0+b1)*b+b1+2.0*b2)/cd;//notch["b3"]
		bbn[mm][i][3]=(b*b+b1*b+b2)/cd;//notch["b4"]
		aan[mm][i][0]=-4.0*a*(b+1.0)/d;//notch["a1"]
		aan[mm][i][1]=2.0*(1.0+2.0*a*a/d);//notch["a2"]
		aan[mm][i][2]=-4.0*a*(b+1.0)/d;//notch["a3"]
		aan[mm][i][3]=1.0;//notch["a4"]
	}
	notch.pole[mm] = nn;
}
