#include <math.h>
#include "filt.h"
extern void bcoef (double, double *, double (*)[2], double (*)[2], int *, double *);

void bandstopcoef()
{
	static double pai=3.14159265358979324;
	double  cos(),atan(),tan();
	double  th,wpl,wph,ar,b1,b2,cd,kp,a,b,d,e;
	double  gg1[BsConst1],aa1[BsConst1][BsConst2/2],bb1[BsConst1][BsConst2/2],c;
	int    i,nn;

        e = bandstop.decay / 2.0;
        bcoef(e, gg1, aa1, bb1, &nn, &c);
        wpl = 2.0 * pai * bandstop.cutoff1 / smpf;
        wph = 2.0 * pai * bandstop.cutoff2 / smpf;
	th=2.0*atan(c/2.0);
	ar=cos((wph+wpl)/2.0)/cos((wph-wpl)/2.0);
	kp=tan((wph-wpl)/2.0)*tan(th/2.0);
	a=(2.0*ar)/(1.0+kp);
	b=(1.0-kp)/(1.0+kp);
	d=(1.0+b)*(1.0+b);
	for(i=0;i<nn;i++){
		b1=bb1[i][0]; 
		b2=bb1[i][1];
		cd=1.0+b1*b+b2*b*b;
		ggb[i]=gg1[i]*d/cd;
		bbb[i][0]=-a*((2.0+b1)+b*(b1+2.0*b2))/cd;
		bbb[i][1]=(b1*b*b+2.0*(1.0+b2)*b+b1+(1.0+b1+b2)*a*a)/cd;
		bbb[i][2]=-a*((2.0+b1)*b+b1+2.0*b2)/cd;
		bbb[i][3]=(b*b+b1*b+b2)/cd;
		aab[i][0]=-4.0*a*(b+1.0)/d;
		aab[i][1]=2.0*(1.0+2.0*a*a/d);
		aab[i][2]=-4.0*a*(b+1.0)/d;
		aab[i][3]=1.0;
	}
        bandstop.pole=nn;
}
